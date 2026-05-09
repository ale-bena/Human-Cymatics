# crowd_mvp/people.py
# Agent class: wanderer behavior with POI steering and boundary clamping.
# SIM-01: agent has position (x,y), velocity, behavior (always Wanderer in Phase 1).
# SIM-02: random walk with POI attraction; changes target every N seconds.
# SIM-05: agents stay within map boundary — no internal walls, just edge clamping.

import numpy as np
from crowd_mvp.config import (
    AGENT_SPEED, AGENT_NOISE, AGENT_RADIUS,
    ARRIVAL_THRESHOLD, DWELL_MIN_FRAMES, DWELL_MAX_FRAMES
)


class Agent:
    """Single simulated person. Phase 1 behavior: Wanderer.

    Attributes:
        pos (np.ndarray): float32 [x, y] position in map pixels
        vel (np.ndarray): float32 [vx, vy] current velocity
        target_pos (np.ndarray): float32 [x, y] current POI target
        dwell_frames (int): frames remaining to dwell at current POI (0 = moving)
        radius (int): render radius in pixels
    """

    def __init__(self, spawn_pos, poi_list, map_size):
        """
        Args:
            spawn_pos: (x, y) tuple — starting position (D-04: entrance POI position)
            poi_list:  list of dicts with 'pos' key — all POI on the map
            map_size:  (width, height) tuple — map boundary
        """
        self.pos = np.array(spawn_pos, dtype=np.float32)
        self.vel = np.zeros(2, dtype=np.float32)
        self.poi_list = poi_list
        self.map_w, self.map_h = map_size
        self.radius = AGENT_RADIUS
        self.dwell_frames = 0
        self.target_pos = self._pick_random_poi()

        # Position history for Tab 3 trajectory rendering (D-07).
        # Populated only when track=True is passed at construction.
        self._track = False
        self.pos_history = []  # list of (x, y) int tuples, appended each frame when tracking

    def _pick_random_poi(self):
        """Pick a random POI position from the poi_list."""
        idx = np.random.randint(0, len(self.poi_list))
        return np.array(self.poi_list[idx]['pos'], dtype=np.float32)

    def update(self):
        """Advance agent one frame. Called once per frame by Simulation.update().

        Wanderer logic (D-01, D-02):
          - If dwelling: decrement dwell counter, stay put.
          - If moving: steer toward target POI.
            velocity = normalize(target - pos) * AGENT_SPEED + noise
          - On arrival (distance < ARRIVAL_THRESHOLD): start dwell, then re-target (D-03).
          - Position clamped to map boundary after move (SIM-05).
        """
        if self.dwell_frames > 0:
            self.dwell_frames -= 1
            if self.dwell_frames == 0:
                self.target_pos = self._pick_random_poi()
            if self._track:
                self.pos_history.append((int(self.pos[0]), int(self.pos[1])))
            return

        # Steering toward target (D-01)
        direction = self.target_pos - self.pos
        dist = np.linalg.norm(direction)

        if dist < ARRIVAL_THRESHOLD:
            # Arrived — dwell for 1–3 seconds (D-03)
            self.dwell_frames = np.random.randint(DWELL_MIN_FRAMES, DWELL_MAX_FRAMES + 1)
            self.vel = np.zeros(2, dtype=np.float32)
        else:
            # Normalise + scale + noise (D-02)
            unit = direction / dist
            noise = np.random.uniform(-AGENT_NOISE, AGENT_NOISE, size=2).astype(np.float32)
            self.vel = unit * AGENT_SPEED + noise
            self.pos += self.vel

        # Record position if tracking enabled (D-07)
        if self._track:
            self.pos_history.append((int(self.pos[0]), int(self.pos[1])))

        # Boundary clamping — keep agent inside map (SIM-05)
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

    Identical movement mechanics to Agent (Wanderer) but picks only
    'bar', 'sponsor_stand', or 'bathroom' POI as targets — never
    entrance/exit. This concentrates agents around venue features,
    producing visible POI clustering in the heatmap (D-08).
    """

    _GOAL_CATEGORIES = ('bar', 'sponsor_stand', 'bathroom')

    def __init__(self, spawn_pos, poi_list, map_size):
        # Filter poi_list to goal categories before super().__init__
        # so that _pick_random_poi() override works during super().__init__.
        self._goal_pois = [p for p in poi_list if p['category'] in self._GOAL_CATEGORIES]
        if not self._goal_pois:
            # Fallback: use full poi_list if no goal POIs defined
            self._goal_pois = list(poi_list)
        super().__init__(spawn_pos, poi_list, map_size)
        # target_pos is already set to a goal POI via _pick_random_poi() override above

    def _pick_goal_poi(self):
        """Pick a random goal-category POI."""
        idx = np.random.randint(0, len(self._goal_pois))
        return np.array(self._goal_pois[idx]['pos'], dtype=np.float32)

    def _pick_random_poi(self):
        """Override: always pick from goal POIs, not all POIs."""
        return self._pick_goal_poi()


class SocialAgent(Agent):
    """Social/clusterer agent (SIM-04, D-07).

    Steers toward the centroid of its K nearest neighbours.
    Does NOT override update() — call update_social(agents) each frame.
    Retains random jitter so agents stay dynamic and don't freeze.
    """

    K_NEIGHBOURS = 10

    def __init__(self, spawn_pos, poi_list, map_size):
        super().__init__(spawn_pos, poi_list, map_size)

    def update_social(self, agents):
        """Advance one frame using social steering (D-07).

        Args:
            agents: full list of Agent-like instances in the simulation.
                    Self is expected to be in this list.

        Behaviour:
          1. Collect positions of all other agents.
          2. Compute Euclidean distances from self.pos.
          3. Take K nearest (excluding self).
          4. Steer toward their centroid + random jitter.
          5. Clamp to map boundary.
        """
        # Build position matrix — exclude self
        others = [a for a in agents if a is not self]
        if not others:
            return  # only agent, stay put

        positions = np.array([a.pos for a in others], dtype=np.float32)  # (N-1, 2)
        diffs = positions - self.pos  # (N-1, 2)
        dists = np.linalg.norm(diffs, axis=1)  # (N-1,)

        k = min(self.K_NEIGHBOURS, len(others))
        nearest_idx = np.argpartition(dists, k - 1)[:k]
        centroid = positions[nearest_idx].mean(axis=0)

        direction = centroid - self.pos
        dist = np.linalg.norm(direction)

        if dist > 1.0:
            unit = direction / dist
            jitter = np.random.uniform(-AGENT_NOISE * 2, AGENT_NOISE * 2, size=2).astype(np.float32)
            self.vel = unit * AGENT_SPEED * 0.6 + jitter  # slower convergence — D-07 clusters stay tight
            self.pos += self.vel
        else:
            # Arrived at centroid — add jitter only
            jitter = np.random.uniform(-AGENT_NOISE * 3, AGENT_NOISE * 3, size=2).astype(np.float32)
            self.pos += jitter

        # Boundary clamp (SIM-05)
        self.pos[0] = np.clip(self.pos[0], self.radius, self.map_w - self.radius)
        self.pos[1] = np.clip(self.pos[1], self.radius, self.map_h - self.radius)

        # Record position if tracking enabled
        if self._track:
            self.pos_history.append((int(self.pos[0]), int(self.pos[1])))


# Alias for clarity in simulation.py import
WandererAgent = Agent
