import math
from collections import deque
from dataclasses import dataclass, asdict
from typing import List, Optional

from crowd_mvp.config import (
    ALERT_CAPACITY_WARN, ALERT_CAPACITY_CRIT,
    ALERT_SURGE_RATIO, ALERT_BOTTLENECK_RATIO,
    ALERT_EVAC_DISTANCE, ALERT_DATAQUAL_RATIO,
)

_HISTORY_MAX = 60   # 30s * 2Hz


@dataclass
class Alert:
    id: str
    severity: str
    type: str
    room: str
    title: str
    description: str
    suggestion: str
    since: float

    def to_dict(self):
        return asdict(self)


class AlertEngine:
    def __init__(self):
        self._history: deque = deque(maxlen=_HISTORY_MAX)
        self._alert_since: dict = {}

    def evaluate(self, snap: dict) -> List[Alert]:
        self._history.append(snap)
        t = snap.get('elapsed_s', snap.get('t', 0.0))

        alerts = []
        alerts.extend(self._capacity_alerts(snap))
        alerts.extend(self._surge_alerts(snap))
        alerts.extend(self._bottleneck_alerts(snap))
        alerts.extend(self._evac_risk_alerts(snap))
        alerts.extend(self._data_quality_alerts(snap))

        current_ids = {a.id for a in alerts}
        for a in alerts:
            if a.id not in self._alert_since:
                self._alert_since[a.id] = t
            a.since = self._alert_since[a.id]

        gone = set(self._alert_since.keys()) - current_ids
        for aid in gone:
            del self._alert_since[aid]

        return alerts

    def _capacity_alerts(self, snap) -> List[Alert]:
        alerts = []
        map_def = snap.get('map_def', {})
        room_density = snap.get('room_density', {})

        for room in map_def.get('rooms', []):
            rid = room['id']
            cap = room.get('capacity')
            if not cap:
                continue
            density = room_density.get(rid, 0)
            ratio = density / cap

            if ratio >= ALERT_CAPACITY_CRIT:
                severity, label = 'critical', 'over'
                suggestion = f"Limit incoming flow at entrance to {room['name']}"
            elif ratio >= ALERT_CAPACITY_WARN:
                severity, label = 'warning', 'near'
                suggestion = f"Monitor flow into {room['name']}"
            else:
                continue

            alerts.append(Alert(
                id=f'capacity:{rid}',
                severity=severity,
                type='capacity',
                room=rid,
                title=f"{room['name']} {label} capacity",
                description=f"{density}/{cap} people ({int(ratio * 100)}%)",
                suggestion=suggestion,
                since=0.0,
            ))
        return alerts

    def _surge_alerts(self, snap) -> List[Alert]:
        map_def = snap.get('map_def', {})
        room_density = snap.get('room_density', {})
        old_snap = self._snapshot_n_ago(20)  # ~10s ago at 2Hz
        if old_snap is None:
            return []
        old_density = old_snap.get('room_density', {})

        alerts = []
        for room in map_def.get('rooms', []):
            rid = room['id']
            now = room_density.get(rid, 0)
            before = old_density.get(rid, 0)
            ratio = (now - before) / max(1, before)
            if ratio >= ALERT_SURGE_RATIO:
                alerts.append(Alert(
                    id=f'surge:{rid}',
                    severity='critical',
                    type='surge',
                    room=rid,
                    title=f"Surge in {room['name']}",
                    description=f"+{int(ratio * 100)}% in ~10s ({before}→{now})",
                    suggestion=f"Deploy staff to {room['name']}",
                    since=0.0,
                ))
        return alerts

    def _bottleneck_alerts(self, snap) -> List[Alert]:
        map_def = snap.get('map_def', {})
        door_flow = snap.get('door_flow', {})
        room_density = snap.get('room_density', {})

        flow_history: dict = {}
        for old in self._history:
            for did, flow in old.get('door_flow', {}).items():
                flow_history.setdefault(did, []).append(flow)

        alerts = []
        for door in map_def.get('doors', []):
            did = door['id']
            current = door_flow.get(did, 0.0)
            hist = flow_history.get(did, [])
            baseline = sum(hist) / len(hist) if hist else 0.0
            if baseline < 0.1:
                continue
            if current >= baseline * ALERT_BOTTLENECK_RATIO:
                continue

            room_a, room_b = door['rooms']
            den_a = room_density.get(room_a, 0)
            den_b = room_density.get(room_b, 0)
            upstream_id = room_a if den_a >= den_b else room_b
            upstream = next((r for r in map_def.get('rooms', []) if r['id'] == upstream_id), None)
            if upstream is None:
                continue
            cap = upstream.get('capacity')
            if cap and room_density.get(upstream_id, 0) > 0.7 * cap:
                label = did.replace('d_', '').replace('_', ' → ')
                alerts.append(Alert(
                    id=f'bottleneck:{did}',
                    severity='warning',
                    type='bottleneck',
                    room=upstream_id,
                    title=f"Bottleneck: {label}",
                    description=f"Flow {current:.1f}/s vs baseline {baseline:.1f}/s",
                    suggestion="Open secondary route or redirect crowd",
                    since=0.0,
                ))
        return alerts

    def _evac_risk_alerts(self, snap) -> List[Alert]:
        map_def = snap.get('map_def', {})
        room_density = snap.get('room_density', {})
        agents = snap.get('agents', [])

        exit_pois = [p for p in map_def.get('poi', []) if p['category'] == 'exit']
        if not exit_pois:
            return []

        alerts = []
        for room in map_def.get('rooms', []):
            rid = room['id']
            cap = room.get('capacity')
            if not cap:
                continue
            density = room_density.get(rid, 0)
            if density <= 0.6 * cap:
                continue

            room_agents = [(x, y) for x, y, r in agents if r == rid]
            if not room_agents:
                continue

            avg_dist = sum(
                min(math.hypot(ax - p['pos'][0], ay - p['pos'][1]) for p in exit_pois)
                for ax, ay in room_agents
            ) / len(room_agents)

            if avg_dist > ALERT_EVAC_DISTANCE:
                rx, ry, rw, rh = room['rect']
                nearest_exit = min(
                    exit_pois,
                    key=lambda p: math.hypot(rx + rw/2 - p['pos'][0], ry + rh/2 - p['pos'][1]),
                )
                alerts.append(Alert(
                    id=f'evac:{rid}',
                    severity='warning',
                    type='evacuation_risk',
                    room=rid,
                    title=f"Evacuation risk: {room['name']}",
                    description=f"Avg exit dist {avg_dist:.0f}px · {int(density/cap*100)}% cap",
                    suggestion=f"Direct crowd toward {nearest_exit['id']}",
                    since=0.0,
                ))
        return alerts

    def _data_quality_alerts(self, snap) -> List[Alert]:
        real = snap.get('zone_counts_real', {})
        est = snap.get('zone_counts_estimated', {})

        alerts = []
        for zone_id in real:
            r_val = real.get(zone_id, 0)
            e_val = est.get(zone_id, 0)
            ratio = abs(r_val - e_val) / max(r_val, 1)
            if ratio > ALERT_DATAQUAL_RATIO:
                alerts.append(Alert(
                    id=f'dataqual:{zone_id}',
                    severity='warning',
                    type='data_quality',
                    room=zone_id,
                    title=f"WiFi mismatch: zone {zone_id}",
                    description=f"Real {r_val} · estimated {e_val} ({int(ratio*100)}% error)",
                    suggestion=f"Check sniffer {zone_id} calibration",
                    since=0.0,
                ))
        return alerts

    def _snapshot_n_ago(self, n: int) -> Optional[dict]:
        if len(self._history) > n:
            return list(self._history)[-(n + 1)]
        return None
