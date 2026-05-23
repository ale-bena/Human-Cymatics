import asyncio
import json
import time
from typing import Set

from crowd_mvp.maps import ROOMED_MAP
from crowd_mvp.simulation import Simulation
from crowd_mvp.web.alerts import AlertEngine
from crowd_mvp.web.heatmap_png import kde_to_b64, estimate_to_b64
from crowd_mvp.web.scenarios import SCENARIOS

_BROADCAST_INTERVAL = 0.5   # seconds (2 Hz)
_UPDATE_INTERVAL    = 1.0 / 60  # ~16.7 ms


class SimulationManager:
    def __init__(self):
        self._sim: Simulation = None
        self._scenario: str = 'baseline'
        self._paused: bool = False
        self._connections: Set = set()
        self._alert_engine = AlertEngine()
        self._last_snapshot: dict = None
        self._static_geometry: dict = None
        self._task: asyncio.Task = None
        self._reset_sim('baseline')

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def _reset_sim(self, scenario_name: str, n_people_override: int = None):
        cfg = SCENARIOS[scenario_name]
        n = n_people_override if n_people_override is not None else cfg['n_people']
        n = max(10, min(700, n))
        self._sim = Simulation(
            map_def=ROOMED_MAP,
            n_people=n,
            sigma=cfg['sigma'],
            duration=86400,   # effectively infinite
            behavior=cfg['behavior'],
        )
        if cfg.get('post_init'):
            cfg['post_init'](self._sim)
        self._scenario = scenario_name
        self._alert_engine = AlertEngine()
        self._paused = False
        self._last_snapshot = None
        self._static_geometry = _extract_geometry(ROOMED_MAP)

    async def start(self):
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        last_broadcast = 0.0
        while True:
            t0 = time.monotonic()

            if not self._paused:
                self._sim.update()

            now = time.monotonic()
            if now - last_broadcast >= _BROADCAST_INTERVAL:
                await self._broadcast()
                last_broadcast = time.monotonic()

            elapsed = time.monotonic() - t0
            await asyncio.sleep(max(0.0, _UPDATE_INTERVAL - elapsed))

    # ------------------------------------------------------------------
    # Broadcast
    # ------------------------------------------------------------------
    async def _broadcast(self):
        sim = self._sim
        snap = sim.get_snapshot()
        real, est = sim.get_zone_counts()
        room_density = sim.get_room_density()
        door_flow = sim.get_door_flow()

        ext_snap = {
            **snap,
            'zone_counts_real': real,
            'zone_counts_estimated': est,
            'room_density': room_density,
            'door_flow': door_flow,
            'map_def': sim.map_def,
        }

        alerts = self._alert_engine.evaluate(ext_snap)

        agents_xy = [(x, y) for x, y, _ in snap['agents']]
        kde_b64 = kde_to_b64(agents_xy, sim.map_size)
        est_b64 = estimate_to_b64(sim.map_def, est)

        payload = {
            't': snap['elapsed_s'],
            'running': not self._paused,
            'scenario': self._scenario,
            'n_people': self._sim.n_people,
            'rooms': _rooms_payload(sim.map_def, room_density),
            'doors': _doors_payload(sim.map_def, door_flow),
            'agents': [[round(x, 1), round(y, 1), r] for x, y, r in snap['agents']],
            'kde_png_b64': kde_b64,
            'estimate_png_b64': est_b64,
            'alerts': [a.to_dict() for a in alerts],
        }
        self._last_snapshot = payload

        if not self._connections:
            return

        msg = json.dumps(payload)
        dead = set()
        for ws in list(self._connections):
            try:
                await ws.send_text(msg)
            except Exception:
                dead.add(ws)
        self._connections -= dead

    # ------------------------------------------------------------------
    # WebSocket management
    # ------------------------------------------------------------------
    async def connect(self, ws):
        await ws.accept()
        self._connections.add(ws)
        if self._static_geometry:
            await ws.send_text(json.dumps({'type': 'geometry', **self._static_geometry}))
        if self._last_snapshot:
            await ws.send_text(json.dumps(self._last_snapshot))

    def disconnect(self, ws):
        self._connections.discard(ws)

    # ------------------------------------------------------------------
    # Control API
    # ------------------------------------------------------------------
    async def pause(self):
        self._paused = True

    async def resume(self):
        self._paused = False

    async def reset(self, n_people: int = None):
        self._reset_sim(self._scenario, n_people_override=n_people)
        geom_msg = json.dumps({'type': 'geometry', **self._static_geometry})
        for ws in list(self._connections):
            try:
                await ws.send_text(geom_msg)
            except Exception:
                self._connections.discard(ws)

    async def load_scenario(self, name: str):
        if name not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {name}")
        self._reset_sim(name)
        geom_msg = json.dumps({'type': 'geometry', **self._static_geometry})
        for ws in list(self._connections):
            try:
                await ws.send_text(geom_msg)
            except Exception:
                self._connections.discard(ws)

    def last_snapshot(self) -> dict:
        return self._last_snapshot

    # ------------------------------------------------------------------
    # Testing helper
    # ------------------------------------------------------------------
    async def run_for(self, seconds: float):
        """Advance simulation for `seconds` of wall-clock time (for unit tests)."""
        end = time.monotonic() + seconds
        last_broadcast = 0.0
        while time.monotonic() < end:
            if not self._paused:
                self._sim.update()
            now = time.monotonic()
            if now - last_broadcast >= _BROADCAST_INTERVAL:
                await self._broadcast()
                last_broadcast = now
            await asyncio.sleep(0)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _extract_geometry(map_def: dict) -> dict:
    return {
        'map_size': list(map_def['size']),
        'rooms': [
            {'id': r['id'], 'name': r['name'], 'rect': list(r['rect']), 'capacity': r.get('capacity')}
            for r in map_def.get('rooms', [])
        ],
        'walls': map_def.get('walls', []),
        'doors': map_def.get('doors', []),
        'obstacles': map_def.get('obstacles', []),
        'decor': map_def.get('decor', []),
        'pois': map_def.get('poi', []),
    }


def _rooms_payload(map_def: dict, room_density: dict) -> list:
    return [
        {
            'id': r['id'],
            'name': r['name'],
            'rect': list(r['rect']),
            'density': room_density.get(r['id'], 0),
            'capacity': r.get('capacity'),
        }
        for r in map_def.get('rooms', [])
    ]


def _doors_payload(map_def: dict, door_flow: dict) -> list:
    return [
        {
            'id': d['id'],
            'x0': d['x0'], 'y0': d['y0'],
            'x1': d['x1'], 'y1': d['y1'],
            'flow': door_flow.get(d['id'], 0.0),
        }
        for d in map_def.get('doors', [])
    ]
