---
phase: 01-engine-core
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - crowd_mvp/__init__.py
  - crowd_mvp/config.py
  - crowd_mvp/maps.py
  - crowd_mvp/viz/__init__.py
  - crowd_mvp/viz/heatmap.py
autonomous: true
requirements:
  - SIM-06
  - SIM-07
  - SNF-03

must_haves:
  truths:
    - "SMALL_MAP dict is importable and contains the correct 4 zones and 5 POI"
    - "Default simulation parameters (n_people=50, sigma=2.0, duration=300, FPS=60) are accessible from config.py"
    - "viz/heatmap.py exists as a placeholder module (no matplotlib embed in main loop)"
  artifacts:
    - path: "crowd_mvp/config.py"
      provides: "All default simulation constants"
      contains: "N_PEOPLE"
    - path: "crowd_mvp/maps.py"
      provides: "SMALL_MAP data dict with zones and POI"
      contains: "SMALL_MAP"
    - path: "crowd_mvp/viz/heatmap.py"
      provides: "Placeholder KDE heatmap module"
      contains: "# Phase 2"
  key_links:
    - from: "crowd_mvp/people.py (Wave 2)"
      to: "crowd_mvp/maps.py"
      via: "import SMALL_MAP"
      pattern: "SMALL_MAP"
    - from: "crowd_mvp/sniffers.py (Wave 2)"
      to: "crowd_mvp/maps.py"
      via: "import SMALL_MAP"
      pattern: "SMALL_MAP"
---

<objective>
Create the data foundations for Phase 1: project package structure, configuration constants, the SMALL_MAP data dictionary, and the viz/heatmap.py placeholder.

Purpose: All Wave 2 modules (people.py, sniffers.py) import from maps.py and config.py. These must exist and be correct before any simulation code is written.
Output: crowd_mvp/ package with config.py, maps.py, viz/heatmap.py. No simulation logic yet.
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
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create package structure and config.py</name>
  <files>crowd_mvp/__init__.py, crowd_mvp/config.py</files>

  <read_first>
    - .planning/phases/01-engine-core/01-CONTEXT.md (all decisions, especially D-02, D-05, D-06, D-10)
    - .planning/REQUIREMENTS.md (SIM-06, SIM-07, SNF-03)
  </read_first>

  <action>
Create the directory crowd_mvp/ and the following two files.

crowd_mvp/__init__.py — empty file, makes crowd_mvp a Python package.

crowd_mvp/config.py — all default simulation constants. Create this file with exactly these contents:

```python
# crowd_mvp/config.py
# Global simulation constants — defaults calibrated for a convincing pitch demo.

# Display
WINDOW_TITLE = "Human Cymatics — Crowd Monitor"
FPS = 60

# Simulation defaults (SIM-06: configurable via slider, default 50 for small map)
N_PEOPLE = 50
SIM_DURATION = 300  # seconds (SIM-07: auto-stop after this duration)

# Agent movement (D-02)
AGENT_SPEED = 1.5       # pixels per frame
AGENT_NOISE = 0.3       # px/frame random jitter magnitude
AGENT_RADIUS = 4        # render radius in pixels
ARRIVAL_THRESHOLD = 12  # distance in px at which agent considers POI reached
DWELL_MIN_FRAMES = 60   # minimum dwell at POI (1 second at 60 FPS) (D-03)
DWELL_MAX_FRAMES = 180  # maximum dwell at POI (3 seconds at 60 FPS) (D-03)

# Sniffer (SNF-03: σ is a global parameter, same for all nodes)
SIGMA_ERROR = 2.0  # Gaussian noise std dev for sniffer estimates
SNIFFER_TICK_FRAMES = 60  # frames between sniffer ticks (D-10: 60 frames ≈ 1 second)

# Colours (D-05, D-08)
COLOUR_BG = (240, 240, 240)          # light grey canvas
COLOUR_ZONE_FILL = (220, 220, 220)   # darker grey zone areas
COLOUR_ZONE_BORDER = (160, 160, 160) # thin zone border lines
COLOUR_AGENT = (180, 220, 255)       # light blue agents (D-05)
COLOUR_SNIFFER = (60, 120, 200)      # sniffer WiFi icon
COLOUR_POI_ENTRANCE = (80, 200, 80)  # green
COLOUR_POI_EXIT = (200, 80, 80)      # red
COLOUR_POI_BAR = (255, 180, 0)       # amber
COLOUR_POI_STAND = (180, 100, 220)   # purple
COLOUR_POI_BATHROOM = (80, 180, 200) # teal
COLOUR_OVERLAY_BG = (20, 20, 20, 180) # semi-transparent end overlay (D-11)
COLOUR_TEXT = (255, 255, 255)
COLOUR_LABEL = (40, 40, 40)

# Font sizes
FONT_SIZE_LABEL = 11   # POI and sniffer count labels
FONT_SIZE_OVERLAY = 28 # "Simulation complete" text
```
  </action>

  <verify>
    <automated>python -c "import sys; sys.path.insert(0, '.'); from crowd_mvp.config import FPS, N_PEOPLE, SIM_DURATION, SIGMA_ERROR; assert FPS == 60; assert N_PEOPLE == 50; assert SIM_DURATION == 300; assert SIGMA_ERROR == 2.0; print('config OK')"</automated>
  </verify>

  <acceptance_criteria>
    - crowd_mvp/__init__.py exists (file present, can be empty)
    - crowd_mvp/config.py contains `FPS = 60`
    - crowd_mvp/config.py contains `N_PEOPLE = 50`
    - crowd_mvp/config.py contains `SIM_DURATION = 300`
    - crowd_mvp/config.py contains `SIGMA_ERROR = 2.0`
    - crowd_mvp/config.py contains `SNIFFER_TICK_FRAMES = 60`
    - crowd_mvp/config.py contains `AGENT_SPEED = 1.5`
    - crowd_mvp/config.py contains `COLOUR_AGENT = (180, 220, 255)`
    - `from crowd_mvp.config import FPS` succeeds with no import errors
  </acceptance_criteria>

  <done>config.py importable with all Phase 1 constants defined at correct default values</done>
</task>

<task type="auto">
  <name>Task 2: Create maps.py with SMALL_MAP and viz placeholder</name>
  <files>crowd_mvp/maps.py, crowd_mvp/viz/__init__.py, crowd_mvp/viz/heatmap.py</files>

  <read_first>
    - .planning/phases/01-engine-core/01-CONTEXT.md (D-12, D-13, D-14 and the SMALL_MAP example in specifics section)
    - .planning/REQUIREMENTS.md (SNF-01, MAP-04, MAP-05 context for zone/POI structure)
  </read_first>

  <action>
Create three files.

crowd_mvp/maps.py — the SMALL_MAP data dict plus a helper to get sniffer positions. Use the exact structure from D-12 and D-13:

```python
# crowd_mvp/maps.py
# Map data definitions. SMALL_MAP is the Phase 1 map.
# Zones are 2×2 equal grid covering the 600×400 canvas (D-12).
# POI categories: entrance, exit, bar, sponsor_stand, bathroom (D-13, MAP-05).

SMALL_MAP = {
    'size': (600, 400),
    'zones': [
        {'id': 'A', 'rect': (0,   0,   300, 200)},  # top-left
        {'id': 'B', 'rect': (300, 0,   300, 200)},  # top-right
        {'id': 'C', 'rect': (0,   200, 300, 200)},  # bottom-left
        {'id': 'D', 'rect': (300, 200, 300, 200)},  # bottom-right
    ],
    'poi': [
        {'id': 'entrance', 'category': 'entrance',     'pos': (50,  200)},
        {'id': 'exit',     'category': 'exit',         'pos': (550, 200)},
        {'id': 'bar',      'category': 'bar',          'pos': (150, 100)},
        {'id': 'stand',    'category': 'sponsor_stand','pos': (450, 100)},
        {'id': 'bathroom', 'category': 'bathroom',     'pos': (300, 350)},
    ]
}


def get_sniffer_positions(map_def):
    """Return list of (zone_id, center_x, center_y) for each zone.
    Sniffer is placed at the geometric centre of its zone (SNF-01).
    """
    positions = []
    for zone in map_def['zones']:
        x, y, w, h = zone['rect']
        cx = x + w // 2
        cy = y + h // 2
        positions.append({'zone_id': zone['id'], 'pos': (cx, cy)})
    return positions


def get_map_bounds(map_def):
    """Return (width, height) of map canvas."""
    return map_def['size']


def find_zone_for_point(map_def, px, py):
    """Return zone id for a point (px, py), or None if out of bounds."""
    for zone in map_def['zones']:
        x, y, w, h = zone['rect']
        if x <= px < x + w and y <= py < y + h:
            return zone['id']
    return None
```

crowd_mvp/viz/__init__.py — empty package init.

crowd_mvp/viz/heatmap.py — Phase 2 placeholder. Do NOT embed matplotlib in main loop per project guidelines:

```python
# crowd_mvp/viz/heatmap.py
# Phase 2 placeholder — KDE bivariate heatmap rendered via NumPy → Pygame Surface.
# NOT imported in Phase 1. Added here as a structural placeholder.
#
# Phase 2 implementation notes:
#   - Use scipy.stats.gaussian_kde on sniffer estimated_count-weighted positions
#   - Render to numpy array using viridis/hot colormap from matplotlib.cm
#   - Convert array to pygame.Surface with pygame.surfarray.make_surface
#   - Alpha-blend over map surface using Surface.blit with BLEND_RGBA_MULT
#   - Do NOT call plt.show() or embed matplotlib figure in the game loop


def build_heatmap_surface(sniffer_positions, sniffer_counts, map_size, sigma_kernel=20.0):
    """
    Phase 2: Build a pygame.Surface heatmap from sniffer data.

    Args:
        sniffer_positions: list of (x, y) tuples
        sniffer_counts:    list of float estimated counts (weights)
        map_size:          (width, height) tuple
        sigma_kernel:      KDE bandwidth in pixels

    Returns:
        pygame.Surface with RGBA heatmap, same size as map_size
    """
    raise NotImplementedError("Phase 2 — not implemented in Phase 1")
```
  </action>

  <verify>
    <automated>python -c "import sys; sys.path.insert(0, '.'); from crowd_mvp.maps import SMALL_MAP, get_sniffer_positions, find_zone_for_point; assert len(SMALL_MAP['zones']) == 4; assert len(SMALL_MAP['poi']) == 5; sniffers = get_sniffer_positions(SMALL_MAP); assert sniffers[0] == {'zone_id': 'A', 'pos': (150, 100)}; assert find_zone_for_point(SMALL_MAP, 0, 0) == 'A'; assert find_zone_for_point(SMALL_MAP, 350, 250) == 'D'; print('maps OK')"</automated>
  </verify>

  <acceptance_criteria>
    - crowd_mvp/maps.py contains `SMALL_MAP = {`
    - crowd_mvp/maps.py contains `'size': (600, 400)`
    - crowd_mvp/maps.py contains `{'id': 'A', 'rect': (0,   0,   300, 200)}`
    - crowd_mvp/maps.py contains `{'id': 'entrance', 'category': 'entrance',     'pos': (50,  200)}`
    - crowd_mvp/maps.py contains `def get_sniffer_positions(`
    - crowd_mvp/maps.py contains `def find_zone_for_point(`
    - crowd_mvp/viz/heatmap.py contains `# Phase 2`
    - crowd_mvp/viz/heatmap.py contains `raise NotImplementedError`
    - `from crowd_mvp.maps import SMALL_MAP` succeeds
    - `get_sniffer_positions(SMALL_MAP)` returns list of length 4
    - Zone A sniffer position is (150, 100) — center of (0,0,300,200)
  </acceptance_criteria>

  <done>SMALL_MAP importable with correct 4-zone 2×2 grid and 5 POI; sniffer positions derivable; viz placeholder module present</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Python import | All code runs locally, no network I/O in this plan |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-01-01 | Tampering | config.py constants | accept | Local single-process app; constants are in source, not user-supplied at this layer |
| T-01-02 | Information Disclosure | maps.py hardcoded positions | accept | No PII, no secrets; hardcoded venue layout is intentional for MVP |
</threat_model>

<verification>
After both tasks complete:
- `python -c "from crowd_mvp.config import FPS; from crowd_mvp.maps import SMALL_MAP; print('foundations OK')"` exits 0
- crowd_mvp/ directory contains: __init__.py, config.py, maps.py, viz/__init__.py, viz/heatmap.py
- SMALL_MAP has exactly 4 zones (2×2 grid, each 300×200px) and 5 POI
- Sniffer center for Zone A = (150, 100), B = (450, 100), C = (150, 300), D = (450, 300)
</verification>

<success_criteria>
- All 5 files created and importable as Python modules
- SMALL_MAP matches D-12 zone layout and D-13 POI positions exactly
- config.py defaults match: FPS=60, N_PEOPLE=50, SIM_DURATION=300, SIGMA_ERROR=2.0
- viz/heatmap.py present as structural placeholder, raises NotImplementedError
</success_criteria>

<output>
After completion, create `.planning/phases/01-engine-core/01-01-SUMMARY.md` with:
- Files created
- SMALL_MAP zone grid and sniffer center positions
- config.py key constant values
- Any deviations from plan
</output>
