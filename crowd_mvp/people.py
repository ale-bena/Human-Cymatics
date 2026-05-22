# crowd_mvp/people.py
# Agent classes with waypoint-based navigation through rooms and doors.
# When a map defines rooms/walls/doors, agents A*-route via door waypoints
# and clip movement at walls — producing organic congestion at narrow doors.
# When a map has no rooms (legacy S/M/L), agents fall back to single-waypoint
# POI seeking with boundary clamping — same behavior as before.

import numpy as np
from crowd_mvp.config import (
    AGENT_SPEED, AGENT_NOISE, AGENT_RADIUS,
    ARRIVAL_THRESHOLD, DWELL_MIN_FRAMES, DWELL_MAX_FRAMES
)
from crowd_mvp.maps import find_room_for_point
from crowd_mvp.navigation import astar, build_waypoints, clip_to_walls


# Tighter arrival threshold for door waypoints — narrow doors need a small
# acceptance radius so agents commit to passing through rather than orbiting.
_DOOR_ARRIVAL_THRESHOLD = 6.0


class Agent:
    """Single simulated person — Wanderer behavior.

    Movement model:
      - Pick random POI -> A* over room graph -> list of door waypoints + POI.
      - Steer toward current waypoint; on arrival at door, advance to next.
      - On arrival at final waypoint (POI), dwell 1-3s then repick.
      - Each frame, candidate movement is clipped against walls.

    Attributes:
        pos (np.ndarray):        float32 [x, y] in map pixels
        vel (np.ndarray):        float32 [vx, vy]
        waypoints (list):        list of (x, y) tuples ending at target POI
        waypoint_idx (int):      index of the current waypoint
        dwell_frames (int):      frames remaining to dwell at final POI
    """

    def __init__(self, spawn_pos, poi_list, map_size,
                 room_graph=None, walls=None, room_centers=None, map_def=None):
        """
        Args:
            spawn_pos: (x, y) starting position
            poi_list:  list of POI dicts with 'pos' key
            map_size:  (width, height) tuple
            room_graph: adjacency dict from maps.build_room_graph, or None
            walls:      list of wall segment dicts, or None
            room_centers: {room_id: (cx, cy)} for A* heuristic, or None
            map_def:    map definition dict (needed for find_room_for_point)
        """
        self.pos = np.array(spawn_pos, dtype=np.float32)
        self.vel = np.zeros(2, dtype=np.float32)
        self.poi_list = poi_list
        self.map_w, self.map_h = map_size
        self.radius = AGENT_RADIUS
        self.dwell_frames = 0

        self._room_graph = room_graph or {}
        self._walls = walls or []
        self._room_centers = room_centers or {}
        self._map_def = map_def

        self.waypoints = []
        self.waypoint_idx = 0

        # Tracking (D-07)
        self._track = False
        self.pos_history = []

        self._pick_new_target()

    def _pick_random_poi(self):
        idx = np.random.randint(0, len(self.poi_list))
        return self.poi_list[idx]

    def _pick_new_target(self):
        """Choose a new POI and plan a waypoint path to it."""
        target_poi = self._pick_random_poi()
        target_pos = target_poi['pos']
        self.waypoints = self._plan_path(target_pos)
        self.waypoint_idx = 0

    def _plan_path(self, target_pos):
        """Build a list of (x, y) waypoints from current pos through doors to target_pos.

        Falls back to a single waypoint (target_pos) when the map has no rooms.
        """
        if not self._room_graph or not self._map_def:
            return [(float(target_pos[0]), float(target_pos[1]))]
        start_room = find_room_for_point(self._map_def, float(self.pos[0]), float(self.pos[1]))
        end_room = find_room_for_point(self._map_def, float(target_pos[0]), float(target_pos[1]))
        if start_room is None or end_room is None:
            return [(float(target_pos[0]), float(target_pos[1]))]
        path = astar(self._room_graph, start_room, end_room, self._room_centers)
        if not path:
            return [(float(target_pos[0]), float(target_pos[1]))]
        return build_waypoints(path, self._room_graph, target_pos)

    @property
    def target_pos(self):
        """Current immediate target — a door center or the final POI."""
        if self.waypoints and self.waypoint_idx < len(self.waypoints):
            return np.array(self.waypoints[self.waypoint_idx], dtype=np.float32)
        return self.pos.copy()

    def update(self):
        """Advance one frame."""
        if self.dwell_frames > 0:
            self.dwell_frames -= 1
            if self.dwell_frames == 0:
                self._pick_new_target()
            if self._track:
                self.pos_history.append((int(self.pos[0]), int(self.pos[1])))
            return

        if not self.waypoints or self.waypoint_idx >= len(self.waypoints):
            self._pick_new_target()

        wp = self.waypoints[self.waypoint_idx]
        target = np.array(wp, dtype=np.float32)
        direction = target - self.pos
        dist = float(np.linalg.norm(direction))

        is_final = (self.waypoint_idx == len(self.waypoints) - 1)
        threshold = ARRIVAL_THRESHOLD if is_final else _DOOR_ARRIVAL_THRESHOLD

        if dist < threshold:
            if is_final:
                self.dwell_frames = np.random.randint(DWELL_MIN_FRAMES, DWELL_MAX_FRAMES + 1)
                self.vel = np.zeros(2, dtype=np.float32)
            else:
                self.waypoint_idx += 1
            if self._track:
                self.pos_history.append((int(self.pos[0]), int(self.pos[1])))
            return

        # Steer toward current waypoint with noise
        unit = direction / dist
        noise = np.random.uniform(-AGENT_NOISE, AGENT_NOISE, size=2).astype(np.float32)
        self.vel = unit * AGENT_SPEED + noise
        intended = (float(self.pos[0] + self.vel[0]), float(self.pos[1] + self.vel[1]))

        if self._walls:
            new_pos = clip_to_walls(
                (float(self.pos[0]), float(self.pos[1])), intended, self._walls
            )
            self.pos[0] = new_pos[0]
            self.pos[1] = new_pos[1]
        else:
            self.pos[0] = intended[0]
            self.pos[1] = intended[1]

        if self._track:
            self.pos_history.append((int(self.pos[0]), int(self.pos[1])))

        # Boundary clamp (SIM-05)
        self.pos[0] = np.clip(self.pos[0], self.radius, self.map_w - self.radius)
        self.pos[1] = np.clip(self.pos[1], self.radius, self.map_h - self.radius)

    @property
    def x(self):
        return int(self.pos[0])

    @property
    def y(self):
        return int(self.pos[1])


class GoalAgent(Agent):
    """Goal-oriented agent (SIM-03, D-06).

    Identical movement mechanics to Agent (waypoint navigation + wall clip),
    but only picks bar/sponsor_stand/bathroom POIs. Skips entrance/exit so the
    crowd concentrates around venue features.
    """

    _GOAL_CATEGORIES = ('bar', 'sponsor_stand', 'bathroom')

    def __init__(self, spawn_pos, poi_list, map_size,
                 room_graph=None, walls=None, room_centers=None, map_def=None):
        self._goal_pois = [p for p in poi_list if p['category'] in self._GOAL_CATEGORIES]
        if not self._goal_pois:
            self._goal_pois = list(poi_list)
        super().__init__(spawn_pos, poi_list, map_size,
                         room_graph=room_graph, walls=walls,
                         room_centers=room_centers, map_def=map_def)

    def _pick_random_poi(self):
        idx = np.random.randint(0, len(self._goal_pois))
        return self._goal_pois[idx]


class SocialAgent(Agent):
    """Cluster-following agent (SIM-04, D-07).

    Steers toward the centroid of K nearest neighbors (no POI seeking, no
    A*). Still respects walls via clip_to_walls so clusters don't tunnel
    through architecture.
    """

    K_NEIGHBOURS = 10

    def update_social(self, agents):
        others = [a for a in agents if a is not self]
        if not others:
            return

        positions = np.array([a.pos for a in others], dtype=np.float32)
        diffs = positions - self.pos
        dists = np.linalg.norm(diffs, axis=1)
        k = min(self.K_NEIGHBOURS, len(others))
        nearest_idx = np.argpartition(dists, k - 1)[:k]
        centroid = positions[nearest_idx].mean(axis=0)

        direction = centroid - self.pos
        dist = float(np.linalg.norm(direction))

        if dist > 1.0:
            unit = direction / dist
            jitter = np.random.uniform(-AGENT_NOISE * 2, AGENT_NOISE * 2, size=2).astype(np.float32)
            self.vel = unit * AGENT_SPEED * 0.6 + jitter
            intended = (float(self.pos[0] + self.vel[0]), float(self.pos[1] + self.vel[1]))
        else:
            jitter = np.random.uniform(-AGENT_NOISE * 3, AGENT_NOISE * 3, size=2).astype(np.float32)
            intended = (float(self.pos[0] + jitter[0]), float(self.pos[1] + jitter[1]))

        if self._walls:
            new_pos = clip_to_walls(
                (float(self.pos[0]), float(self.pos[1])), intended, self._walls
            )
            self.pos[0] = new_pos[0]
            self.pos[1] = new_pos[1]
        else:
            self.pos[0] = intended[0]
            self.pos[1] = intended[1]

        self.pos[0] = np.clip(self.pos[0], self.radius, self.map_w - self.radius)
        self.pos[1] = np.clip(self.pos[1], self.radius, self.map_h - self.radius)

        if self._track:
            self.pos_history.append((int(self.pos[0]), int(self.pos[1])))


# Alias for clarity in simulation.py imports
WandererAgent = Agent
