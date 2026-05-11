# crowd_mvp/api.py
# FastAPI server — headless simulation engine + WebSocket dashboard.
# Run: python crowd_mvp/api.py
# Dashboard: http://127.0.0.1:8765

import os
import sys

# Headless pygame: must be set before any crowd_mvp import that pulls in pygame
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
import threading
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from crowd_mvp.config import (
    FPS, SIM_DURATION,
    N_PEOPLE_DEFAULT, N_PEOPLE_MIN, N_PEOPLE_MAX,
    SIGMA_ERROR, SIGMA_ERROR_MIN, SIGMA_ERROR_MAX,
)
from crowd_mvp.maps import ALL_MAPS
from crowd_mvp.simulation import Simulation

# ── Shared state ────────────────────────────────────────────────────────────

_lock    = threading.Lock()
_paused  = False
_staged  = dict(map_key='4', behavior='wanderer', n_people=N_PEOPLE_DEFAULT)
_live    = dict(sigma_error=float(SIGMA_ERROR))
_sim: Simulation = None


def _make_sim():
    global _sim
    _sim = Simulation(
        ALL_MAPS[_staged['map_key']],
        n_people=_staged['n_people'],
        sigma=_live['sigma_error'],
        duration=SIM_DURATION,
        behavior=_staged['behavior'],
    )


_make_sim()


# ── Simulation loop (background thread at FPS) ──────────────────────────────

def _sim_loop():
    target = 1.0 / FPS
    while True:
        t0 = time.perf_counter()
        with _lock:
            if not _paused:
                _sim.update()
        dt = time.perf_counter() - t0
        if dt < target:
            time.sleep(target - dt)


threading.Thread(target=_sim_loop, daemon=True).start()


# ── Snapshot builder ─────────────────────────────────────────────────────────

def _snapshot() -> dict:
    with _lock:
        sim = _sim
        real, est = sim.get_zone_counts()
        zones = []
        for z in sim.map_def['zones']:
            zid = z['id']
            zones.append({
                'id':        zid,
                'label':     z.get('label', zid),
                'rect':      list(z['rect']),
                'colour':    list(z.get('colour', [60, 60, 80, 100])),
                'real':      real.get(zid, 0),
                'estimated': est.get(zid, 0),
            })
        agents   = [[round(float(a.x), 1), round(float(a.y), 1)] for a in sim.agents]
        sniffers = [
            {'pos': list(s.pos), 'zone_id': s.zone_id, 'estimated': s.estimated_count}
            for s in sim.sniffers
        ]
        traffic = {k: dict(v) for k, v in sim.traffic_matrix.items()}
        # Tracked agent trajectories — last 400 positions sampled every 2 frames
        trajectories = []
        for a in sim.tracked_agents:
            hist = list(a.pos_history)[-400::2]
            if len(hist) >= 2:
                trajectories.append(
                    [[round(float(x), 1), round(float(y), 1)] for x, y in hist]
                )
        return {
            'frame':        sim.frame_count,
            'elapsed':      round(sim.frame_count / FPS, 1),
            'duration':     SIM_DURATION,
            'total_real':   sum(real.values()),
            'total_est':    sum(est.values()),
            'is_complete':  sim.is_complete,
            'paused':       _paused,
            'map_key':      _staged['map_key'],
            'behavior':     _staged['behavior'],
            'n_people':     _staged['n_people'],
            'sigma_error':  _live['sigma_error'],
            'map_size':     list(sim.map_def['size']),
            'has_bg_image': bool(sim.map_def.get('bg_image')),
            'zones':        zones,
            'agents':       agents,
            'sniffers':     sniffers,
            'traffic':      traffic,
            'trajectories': trajectories,
        }


# ── FastAPI app ──────────────────────────────────────────────────────────────

app = FastAPI(title='Human Cymatics — Crowd Intelligence')

_STATIC = Path(__file__).parent / 'static'


@app.get('/')
def root():
    return FileResponse(str(_STATIC / 'index.html'))


app.mount('/static', StaticFiles(directory=str(_STATIC)), name='static')


@app.get('/bg_image')
def bg_image():
    with _lock:
        path = _sim.map_def.get('bg_image', '')
    p = Path(path)
    if p.is_file():
        return FileResponse(str(p), media_type='image/png')
    return JSONResponse({'error': 'not found'}, status_code=404)


@app.post('/control')
async def control(body: dict):
    global _paused
    action = body.get('action', '')

    if action == 'toggle_pause':
        with _lock:
            if not _sim.is_complete:
                _paused = not _paused

    elif action == 'set_sigma':
        val = float(body.get('value', _live['sigma_error']))
        val = max(SIGMA_ERROR_MIN, min(SIGMA_ERROR_MAX, val))
        _live['sigma_error'] = val
        with _lock:
            for s in _sim.sniffers:
                s.sigma = val

    elif action == 'reset':
        _staged['map_key']   = body.get('map_key',   _staged['map_key'])
        _staged['behavior']  = body.get('behavior',  _staged['behavior'])
        _staged['n_people']  = max(N_PEOPLE_MIN, min(N_PEOPLE_MAX,
                                   int(body.get('n_people', _staged['n_people']))))
        _live['sigma_error'] = max(SIGMA_ERROR_MIN, min(SIGMA_ERROR_MAX,
                                   float(body.get('sigma_error', _live['sigma_error']))))
        with _lock:
            _make_sim()
        _paused = False

    return {'ok': True, 'paused': _paused}


@app.websocket('/ws')
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_text(json.dumps(_snapshot()))
            await asyncio.sleep(0.1)   # 10 updates / second
    except (WebSocketDisconnect, Exception):
        pass


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('\n  Human Cymatics — Crowd Intelligence Dashboard')
    print('  → http://127.0.0.1:8765\n')
    uvicorn.run(app, host='127.0.0.1', port=8765, log_level='warning')
