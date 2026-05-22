# crowd_mvp/simulation.py
# Simulation: owns agents, sniffers, room graph, and per-tick analytics.
# Headless by design — no pygame import. UI layers read state via get_snapshot()
# and friends; rendering lives in crowd_mvp/render.py.

import random as _random

from crowd_mvp.config import (
    FPS, N_PEOPLE, SIM_DURATION, SIGMA_ERROR, SNIFFER_TICK_FRAMES,
)
from crowd_mvp.maps import (
    get_sniffer_positions, find_zone_for_point,
    find_room_for_point, build_room_graph, get_room_center,
    obstacles_to_walls,
)
from crowd_mvp.people import WandererAgent, GoalAgent, SocialAgent
from crowd_mvp.sniffers import Sniffer


class Simulation:
    """Central simulation orchestrator (headless).

    Usage:
        sim = Simulation(map_def, n_people=50, sigma=2.0, duration=300, behavior='wanderer')
        while not sim.is_complete:
            sim.update()
            snapshot = sim.get_snapshot()   # any UI consumes this
    """

    def __init__(self, map_def, n_people=N_PEOPLE, sigma=SIGMA_ERROR,
                 duration=SIM_DURATION, behavior='wanderer'):
        """
        Args:
            map_def:   map definition dict (may include 'rooms', 'walls', 'doors')
            n_people:  number of agents to spawn (SIM-06)
            sigma:     Gaussian noise std dev for all sniffers (SNF-03)
            duration:  seconds before auto-stop (SIM-07)
            behavior:  'wanderer' | 'goal' | 'social'
        """
        self.map_def = map_def
        self.n_people = n_people
        self.sigma = sigma
        self.duration = duration
        self.duration_frames = int(duration * FPS)

        self.behavior = behavior
        self.frame_count = 0
        self._complete = False

        map_size = map_def['size']
        poi_list = map_def['poi']
        map_w, map_h = map_size

        # --- Room navigation context (empty for legacy maps without rooms) ---
        self.rooms = map_def.get('rooms', [])
        self.walls = map_def.get('walls', [])           # raw walls (for rendering)
        self.doors = map_def.get('doors', [])
        self.obstacles = map_def.get('obstacles', [])
        self.decor = map_def.get('decor', [])
        # Walls the agents collide against — raw walls + obstacle perimeters.
        # clip_to_walls handles them uniformly, no special-casing needed.
        self.agent_walls = list(self.walls) + obstacles_to_walls(self.obstacles)
        self.room_graph = build_room_graph(map_def) if self.rooms else {}
        self.room_centers = {r['id']: get_room_center(map_def, r['id']) for r in self.rooms}

        # --- Door flow tracking ---
        # Map an ordered room pair to the door connecting them (bidirectional).
        self._door_for_pair = {}
        for d in self.doors:
            a, b = d['rooms']
            self._door_for_pair[(a, b)] = d['id']
            self._door_for_pair[(b, a)] = d['id']
        self._door_total = {d['id']: 0 for d in self.doors}
        self._door_total_prev_tick = {d['id']: 0 for d in self.doors}
        self._door_flow = {d['id']: 0.0 for d in self.doors}  # crossings/sec

        # --- Agent class selection ---
        _AGENT_CLASSES = {
            'wanderer': WandererAgent,
            'goal':     GoalAgent,
            'social':   SocialAgent,
        }
        agent_cls = _AGENT_CLASSES.get(behavior, WandererAgent)
        self._is_social = (behavior == 'social')

        # --- Spawn agents ---
        # If the map has rooms, spawn each agent inside a randomly chosen room
        # (with margin), rejecting positions that land inside an obstacle so no
        # one starts boxed in. Otherwise fall back to uniform-on-canvas (legacy).
        self.agents = []
        margin = 20
        for _ in range(n_people):
            spawn = self._sample_spawn(margin)
            self.agents.append(
                agent_cls(
                    spawn, poi_list, map_size,
                    room_graph=self.room_graph,
                    walls=self.agent_walls,
                    room_centers=self.room_centers,
                    map_def=map_def,
                )
            )

        # --- Sniffers at zone centers (SNF-01) ---
        sniffer_defs = get_sniffer_positions(map_def)
        self.sniffers = [
            Sniffer(s['zone_id'], s['pos'], sigma=sigma) for s in sniffer_defs
        ]

        # --- Traffic matrix: zone-to-zone transitions ---
        zone_ids = [z['id'] for z in map_def['zones']]
        self._zone_ids = zone_ids
        self.traffic_matrix = {zi: {zj: 0 for zj in zone_ids} for zi in zone_ids}

        # --- Tracked-agent subset for trajectory rendering ---
        n_track = min(len(self.agents), _random.randint(10, 15))
        self.tracked_agents = _random.sample(self.agents, n_track) if self.agents else []
        for a in self.tracked_agents:
            a._track = True
            a.pos_history.append((a.x, a.y))

        # --- Last-known zone & room per agent (for transition detection) ---
        self._agent_last_zone = {}
        self._agent_last_room = {}
        for a in self.agents:
            self._agent_last_zone[id(a)] = find_zone_for_point(map_def, a.x, a.y)
            self._agent_last_room[id(a)] = find_room_for_point(map_def, a.x, a.y)

    def _sample_spawn(self, margin):
        """Pick a spawn position inside a random room, outside any obstacle.

        Retries a few times if the random point lands inside furniture; gives
        up after MAX_RETRIES and accepts the last sample (rare with the current
        layout — every room has plenty of clear floor space).
        """
        map_w, map_h = self.map_def['size']
        MAX_RETRIES = 12
        for _ in range(MAX_RETRIES):
            if self.rooms:
                room = _random.choice(self.rooms)
                rx, ry, rw, rh = room['rect']
                sx = (_random.uniform(rx + margin, rx + rw - margin)
                      if rw > 2 * margin else rx + rw / 2)
                sy = (_random.uniform(ry + margin, ry + rh - margin)
                      if rh > 2 * margin else ry + rh / 2)
            else:
                sx = _random.uniform(margin, map_w - margin)
                sy = _random.uniform(margin, map_h - margin)
            if not self._in_obstacle(sx, sy):
                return (sx, sy)
        return (sx, sy)

    def _in_obstacle(self, x, y, pad=2):
        """True if (x,y) is inside any obstacle rect (with a small padding)."""
        for o in self.obstacles:
            ox, oy, ow, oh = o['rect']
            if ox - pad <= x <= ox + ow + pad and oy - pad <= y <= oy + oh + pad:
                return True
        return False

    # ------------------------------------------------------------------
    # Core loop
    # ------------------------------------------------------------------
    @property
    def is_complete(self):
        return self._complete

    @property
    def map_size(self):
        return self.map_def['size']

    def update(self):
        """Advance one frame (LOOP-01)."""
        if self._complete:
            return

        if self._is_social:
            for agent in self.agents:
                agent.update_social(self.agents)
        else:
            for agent in self.agents:
                agent.update()

        # Detect door crossings every frame so flow counts are accurate
        # regardless of agent speed.
        self._track_door_crossings()

        if self.frame_count % SNIFFER_TICK_FRAMES == 0:
            self._tick_sniffers()
            self._update_traffic_matrix()
            self._refresh_door_flow()

        self.frame_count += 1
        if self.frame_count >= self.duration_frames:
            self._complete = True

    def _tick_sniffers(self):
        for sniffer in self.sniffers:
            sniffer.tick(self.agents, self.map_def, self.frame_count)

    def _update_traffic_matrix(self):
        """Increment traffic_matrix[from][to] when an agent changes zone."""
        for agent in self.agents:
            aid = id(agent)
            current_zone = find_zone_for_point(self.map_def, agent.x, agent.y)
            prev_zone = self._agent_last_zone.get(aid)
            if (current_zone is not None and prev_zone is not None
                    and current_zone != prev_zone
                    and current_zone in self.traffic_matrix
                    and prev_zone in self.traffic_matrix):
                self.traffic_matrix[prev_zone][current_zone] += 1
            if current_zone is not None:
                self._agent_last_zone[aid] = current_zone

    def _track_door_crossings(self):
        """Increment per-door counters when agents change rooms across a door."""
        if not self._door_for_pair:
            return
        for agent in self.agents:
            aid = id(agent)
            current_room = find_room_for_point(self.map_def, agent.x, agent.y)
            prev_room = self._agent_last_room.get(aid)
            if (current_room is not None and prev_room is not None
                    and current_room != prev_room):
                door_id = self._door_for_pair.get((prev_room, current_room))
                if door_id is not None:
                    self._door_total[door_id] += 1
            if current_room is not None:
                self._agent_last_room[aid] = current_room

    def _refresh_door_flow(self):
        """Compute crossings/sec per door over the last sniffer tick window."""
        seconds = SNIFFER_TICK_FRAMES / FPS
        for door_id, total in self._door_total.items():
            delta = total - self._door_total_prev_tick.get(door_id, 0)
            self._door_flow[door_id] = delta / seconds
            self._door_total_prev_tick[door_id] = total

    # ------------------------------------------------------------------
    # Read API (any UI consumes these — no pygame dependency)
    # ------------------------------------------------------------------
    def get_heatmap_data(self):
        """Sniffer positions and estimated counts — for KDE heatmap input."""
        positions = [s.pos for s in self.sniffers]
        counts = [float(s.estimated_count) for s in self.sniffers]
        return positions, counts

    def get_zone_counts(self):
        """real_counts, estimated_counts: dict[zone_id -> int]."""
        real_counts = {s.zone_id: s.real_count for s in self.sniffers}
        estimated_counts = {s.zone_id: s.estimated_count for s in self.sniffers}
        return real_counts, estimated_counts

    def get_room_density(self):
        """{room_id: int} — current headcount per room.

        Empty dict if the map defines no rooms (legacy S/M/L).
        """
        density = {r['id']: 0 for r in self.rooms}
        if not density:
            return density
        for a in self.agents:
            rid = find_room_for_point(self.map_def, a.x, a.y)
            if rid is not None and rid in density:
                density[rid] += 1
        return density

    def get_door_flow(self):
        """{door_id: crossings_per_second} averaged over the last tick window."""
        return dict(self._door_flow)

    def get_snapshot(self):
        """Headless state snapshot — one dict any future UI can render from.

        Returns:
            dict with frame, elapsed_s, complete, agents (list of (x, y, room_id)),
            zone_counts (real/estimated), room_density, door_flow.
        """
        real, est = self.get_zone_counts()
        agents = []
        for a in self.agents:
            agents.append((a.x, a.y, find_room_for_point(self.map_def, a.x, a.y)))
        return {
            'frame': self.frame_count,
            'elapsed_s': self.frame_count / FPS,
            'complete': self._complete,
            'agents': agents,
            'zone_counts_real': real,
            'zone_counts_estimated': est,
            'room_density': self.get_room_density(),
            'door_flow': self.get_door_flow(),
            'door_total': dict(self._door_total),
        }
