---
phase: 01-engine-core
plan: 02
type: execute
wave: 2
depends_on:
  - 01-PLAN-foundations
files_modified:
  - crowd_mvp/people.py
  - crowd_mvp/sniffers.py
autonomous: true
requirements:
  - SIM-01
  - SIM-02
  - SIM-05
  - SNF-01
  - SNF-02
  - SNF-03
  - SNF-04
  - VIZ-04

must_haves:
  truths:
    - "Agent can be instantiated, updates its position each frame, and never leaves the map boundary"
    - "Agent steers toward a target POI and re-targets after dwelling"
    - "Sniffer counts real agents in its zone and adds calibrated Gaussian noise"
    - "Sniffer exposes zone_id, position, estimated_count, and timestamp"
  artifacts:
    - path: "crowd_mvp/people.py"
      provides: "Agent class with wanderer steering"
      exports: ["Agent"]
      contains: "class Agent:"
    - path: "crowd_mvp/sniffers.py"
      provides: "Sniffer class with noisy count"
      exports: ["Sniffer"]
      contains: "class Sniffer:"
  key_links:
    - from: "crowd_mvp/simulation.py (Wave 3)"
      to: "crowd_mvp/people.py"
      via: "Agent(map_def, poi_list)"
      pattern: "from crowd_mvp.people import Agent"
    - from: "crowd_mvp/simulation.py (Wave 3)"
      to: "crowd_mvp/sniffers.py"
      via: "Sniffer(zone, sigma)"
      pattern: "from crowd_mvp.sniffers import Sniffer"
---

<objective>
Implement the Agent class (wanderer AI, boundary clamping) and the Sniffer class (zone counting, Gaussian noise). These are the two core domain objects of the simulation.

Purpose: Simulation.py (Wave 3) depends on both of these. Getting them right independently — with unit-testable logic — is the critical path.
Output: crowd_mvp/people.py and crowd_mvp/sniffers.py, both importable and behaviorally correct without Pygame running.
</objective>

<execution_context>
@C:/Users/AlessandroBenassi/.claude/get-shit-done/workflows/execute-plan.md
@C:/Users/AlessandroBenassi/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/01-engine-core/01-CONTEXT.md
@.planning/REQUIREMENTS.md

<interfaces>
<!-- From crowd_mvp/config.py (created in Plan 01) -->
AGENT_SPEED = 1.5        # px/frame
AGENT_NOISE = 0.3        # px/frame jitter
AGENT_RADIUS = 4         # render radius px
ARRIVAL_THRESHOLD = 12   # px distance → POI reached
DWELL_MIN_FRAMES = 60    # 1 second at 60 FPS
DWELL_MAX_FRAMES = 180   # 3 seconds at 60 FPS
SIGMA_ERROR = 2.0        # Gaussian noise std dev

<!-- From crowd_mvp/maps.py (created in Plan 01) -->
SMALL_MAP = {
    'size': (600, 400),
    'zones': [
        {'id': 'A', 'rect': (0,   0,   300, 200)},
        {'id': 'B', 'rect': (300, 0,   300, 200)},
        {'id': 'C', 'rect': (0,   200, 300, 200)},
        {'id': 'D', 'rect': (300, 200, 300, 200)},
    ],
    'poi': [
        {'id': 'entrance', 'category': 'entrance',     'pos': (50,  200)},
        {'id': 'exit',     'category': 'exit',         'pos': (550, 200)},
        {'id': 'bar',      'category': 'bar',          'pos': (150, 100)},
        {'id': 'stand',    'category': 'sponsor_stand','pos': (450, 100)},
        {'id': 'bathroom', 'category': 'bathroom',     'pos': (300, 350)},
    ]
}

def get_sniffer_positions(map_def) -> list[dict]
    # returns [{'zone_id': 'A', 'pos': (150, 100)}, ...]

def find_zone_for_point(map_def, px, py) -> str | None
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement Agent class (people.py)</name>
  <files>crowd_mvp/people.py</files>

  <read_first>
    - .planning/phases/01-engine-core/01-CONTEXT.md (D-01, D-02, D-03, D-04 and the wanderer steering formula in specifics section)
    - .planning/REQUIREMENTS.md (SIM-01, SIM-02, SIM-05)
    - crowd_mvp/config.py (all AGENT_* and DWELL_* constants)
    - crowd_mvp/maps.py (SMALL_MAP structure, poi list format)
  </read_first>

  <action>
Create crowd_mvp/people.py with the Agent class. Implement exactly as described below — no shortcuts, no placeholder logic.

```python
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

        # Boundary clamping — keep agent inside map (SIM-05)
        self.pos[0] = np.clip(self.pos[0], self.radius, self.map_w - self.radius)
        self.pos[1] = np.clip(self.pos[1], self.radius, self.map_h - self.radius)

    @property
    def x(self):
        return int(self.pos[0])

    @property
    def y(self):
        return int(self.pos[1])
```

No draw logic in this file — rendering happens in simulation.py or a dedicated renderer. Keep this module pure simulation logic.
  </action>

  <verify>
    <automated>python -c "
import sys; sys.path.insert(0, '.')
from crowd_mvp.maps import SMALL_MAP
from crowd_mvp.people import Agent
spawn = SMALL_MAP['poi'][0]['pos']
a = Agent(spawn, SMALL_MAP['poi'], SMALL_MAP['size'])
# Run 300 frames
for _ in range(300):
    a.update()
# Must stay within bounds
assert 0 <= a.x <= 600, f'x out of bounds: {a.x}'
assert 0 <= a.y <= 400, f'y out of bounds: {a.y}'
print(f'Agent OK — final pos ({a.x}, {a.y})')
"</automated>
  </verify>

  <acceptance_criteria>
    - crowd_mvp/people.py contains `class Agent:`
    - crowd_mvp/people.py contains `def update(self):`
    - crowd_mvp/people.py contains `def _pick_random_poi(self):`
    - crowd_mvp/people.py contains `np.clip` (boundary clamping, SIM-05)
    - crowd_mvp/people.py contains `ARRIVAL_THRESHOLD` (arrival detection, D-01)
    - crowd_mvp/people.py contains `dwell_frames` (dwell logic, D-03)
    - crowd_mvp/people.py contains `AGENT_SPEED` import from config
    - After 300 update() calls starting at entrance (50, 200), agent.x is between 4 and 596, agent.y is between 4 and 396
    - `from crowd_mvp.people import Agent` succeeds
  </acceptance_criteria>

  <done>Agent class fully implements wanderer steering, dwell logic, and boundary clamping; position stays within (4..596, 4..396) after arbitrary update() calls</done>
</task>

<task type="auto">
  <name>Task 2: Implement Sniffer class (sniffers.py)</name>
  <files>crowd_mvp/sniffers.py</files>

  <read_first>
    - .planning/phases/01-engine-core/01-CONTEXT.md (D-06, D-07, D-10 and SNF-01–SNF-04 in REQUIREMENTS.md)
    - .planning/REQUIREMENTS.md (SNF-01, SNF-02, SNF-03, SNF-04, VIZ-04)
    - crowd_mvp/config.py (SIGMA_ERROR)
    - crowd_mvp/maps.py (get_sniffer_positions, find_zone_for_point)
  </read_first>

  <action>
Create crowd_mvp/sniffers.py with the Sniffer class. Each Sniffer watches one zone.

```python
# crowd_mvp/sniffers.py
# Sniffer class: counts agents in its zone + adds Gaussian noise (SNF-02).
# σ is a uniform global parameter (SNF-03). Per-node σ hook left in code as comment.
# Sniffer exposes: zone_id, position, estimated_count, timestamp (SNF-04).

import numpy as np
from crowd_mvp.config import SIGMA_ERROR


class Sniffer:
    """WiFi sniffer node placed at the centre of one map zone.

    Attributes:
        zone_id (str):          zone this sniffer covers (e.g. 'A')
        pos (tuple):            (x, y) pixel position of sniffer icon (SNF-01)
        sigma (float):          Gaussian noise std dev (SNF-03, uniform default)
        estimated_count (int):  last computed noisy estimate (SNF-04)
        real_count (int):       last actual agent count in zone (ground truth)
        timestamp (int):        frame number of last tick (SNF-04)

    Note:
        σ-per-node hook: to enable heterogeneous noise in future (SIM-V2-02),
        pass per-node sigma values instead of the global SIGMA_ERROR default.
        # σ-per-node hook: replace `sigma=SIGMA_ERROR` arg with per-node dict lookup
    """

    def __init__(self, zone_id, pos, sigma=SIGMA_ERROR):
        """
        Args:
            zone_id: str identifier matching a zone in the map definition
            pos:     (x, y) pixel tuple — centre of the zone (SNF-01)
            sigma:   Gaussian noise std dev; defaults to global SIGMA_ERROR (SNF-03)
                     # σ-per-node hook: caller can pass per-node value here
        """
        self.zone_id = zone_id
        self.pos = pos
        self.sigma = sigma       # σ-per-node hook: stored per instance for future override
        self.estimated_count = 0
        self.real_count = 0
        self.timestamp = 0       # frame number of last tick (SNF-04)

    def tick(self, agents, map_def, frame_number):
        """Count agents in zone and compute noisy estimate. Call once per second (SNF-02).

        Formula (SNF-02): estimated = max(0, round(real_count + N(0, σ)))

        Args:
            agents:       list of Agent instances
            map_def:      map definition dict (used to determine zone membership)
            frame_number: current frame number (stored as timestamp)
        """
        from crowd_mvp.maps import find_zone_for_point

        # Count real agents in this zone
        real = sum(
            1 for a in agents
            if find_zone_for_point(map_def, a.x, a.y) == self.zone_id
        )
        self.real_count = real
        self.timestamp = frame_number

        # Add Gaussian noise — SNF-02 formula
        noise = np.random.normal(0.0, self.sigma)
        self.estimated_count = max(0, round(real + noise))

    @property
    def data(self):
        """Return SNF-04 tuple: (zone_id, position, estimated_count, timestamp)."""
        return (self.zone_id, self.pos, self.estimated_count, self.timestamp)
```

  </action>

  <verify>
    <automated>python -c "
import sys; sys.path.insert(0, '.')
from crowd_mvp.maps import SMALL_MAP, get_sniffer_positions
from crowd_mvp.sniffers import Sniffer
from crowd_mvp.people import Agent

# Build sniffers
sniffer_defs = get_sniffer_positions(SMALL_MAP)
sniffers = [Sniffer(s['zone_id'], s['pos']) for s in sniffer_defs]
assert len(sniffers) == 4

# Build agents at entrance
spawn = SMALL_MAP['poi'][0]['pos']
agents = [Agent(spawn, SMALL_MAP['poi'], SMALL_MAP['size']) for _ in range(10)]

# Run 5 update cycles then tick sniffers
for _ in range(5):
    for a in agents: a.update()

for s in sniffers:
    s.tick(agents, SMALL_MAP, 60)

# Check SNF-04 data tuple
total_estimated = sum(s.estimated_count for s in sniffers)
assert total_estimated >= 0
z, pos, cnt, ts = sniffers[0].data
assert z == 'A'
assert ts == 60
print(f'Sniffers OK — total estimated {total_estimated} for 10 agents')
"</automated>
  </verify>

  <acceptance_criteria>
    - crowd_mvp/sniffers.py contains `class Sniffer:`
    - crowd_mvp/sniffers.py contains `def tick(self, agents, map_def, frame_number):`
    - crowd_mvp/sniffers.py contains `def data(self):`
    - crowd_mvp/sniffers.py contains `max(0, round(real + noise))` (exact SNF-02 formula)
    - crowd_mvp/sniffers.py contains `# σ-per-node hook` (at least one occurrence)
    - crowd_mvp/sniffers.py contains `self.timestamp = frame_number`
    - crowd_mvp/sniffers.py contains `self.real_count = real`
    - crowd_mvp/sniffers.py contains `from crowd_mvp.config import SIGMA_ERROR` (correct module path)
    - `sniffer.data` returns 4-tuple `(zone_id, pos, estimated_count, timestamp)` (SNF-04)
    - `estimated_count` is never negative after tick()
    - Sum of all sniffer real_counts equals total agents when all agents are within map bounds
  </acceptance_criteria>

  <done>Sniffer class counts agents per zone, applies SNF-02 noise formula, exposes SNF-04 data tuple, and has σ-per-node hook comment visible in code</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Python process | All inputs (agent positions, sigma) are internally generated; no user input crosses this boundary in Phase 1 |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-01 | Tampering | Agent.pos | accept | Position derived from simulation logic only; no external input in Phase 1 |
| T-02-02 | Denial of Service | np.random.normal in Sniffer.tick | accept | Called at most 4 times per second (4 sniffers × 1 tick/sec); negligible compute |
| T-02-03 | Elevation of Privilege | find_zone_for_point with out-of-bounds pos | mitigate | Boundary clamping in Agent.update() (SIM-05) ensures pos stays within map; find_zone_for_point returns None for OOB, Sniffer.tick skips None |
</threat_model>

<verification>
After both tasks complete:
- `python -c "from crowd_mvp.people import Agent; from crowd_mvp.sniffers import Sniffer; print('imports OK')"` exits 0
- Agent boundary test: 300 update() calls from (50,200) never produce x outside [4,596] or y outside [4,396]
- Sniffer noise test: tick() with 10 agents in one zone, estimated_count >= 0 always
- SNF-04 data tuple: sniffers[0].data returns (str, tuple, int, int)
- σ-per-node hook visible: `grep "σ-per-node hook" crowd_mvp/sniffers.py` returns at least one match
</verification>

<success_criteria>
- people.py: Agent class with update(), _pick_random_poi(), boundary clamping, dwell logic
- sniffers.py: Sniffer class with tick(), data property, SNF-02 formula, σ-per-node hook comment
- Both importable without Pygame installed (pure NumPy logic)
- All 8 requirement IDs in this plan's requirements are implemented
</success_criteria>

<output>
After completion, create `.planning/phases/01-engine-core/01-02-SUMMARY.md` with:
- Agent class interface (constructor args, key methods)
- Sniffer class interface (constructor args, tick() signature, data property)
- Boundary test results
- Any deviations from plan
</output>
