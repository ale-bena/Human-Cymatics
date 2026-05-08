---
phase: 01-engine-core
plan: 01
subsystem: infra
tags: [pygame, numpy, scipy, crowd-simulation, config, maps]

# Dependency graph
requires: []
provides:
  - crowd_mvp Python package with importable config.py and maps.py
  - SMALL_MAP data dict (4 zones, 5 POI, 600x400 canvas)
  - Sniffer position helpers (get_sniffer_positions, find_zone_for_point)
  - All Phase 1 simulation constants (FPS, N_PEOPLE, SIM_DURATION, SIGMA_ERROR, etc.)
  - viz/heatmap.py Phase 2 structural placeholder
affects: [02-agents, 03-sniffers, 04-render-loop]

# Tech tracking
tech-stack:
  added: [Python 3.10+, Pygame (planned), NumPy (planned)]
  patterns:
    - SMALL_MAP as a data dict with size/zones/poi keys (importable from maps.py)
    - All simulation constants in one config.py module
    - Zone geometry as (x, y, w, h) rect tuples
    - Sniffer centers computed from zone rect (x + w//2, y + h//2)

key-files:
  created:
    - crowd_mvp/__init__.py
    - crowd_mvp/config.py
    - crowd_mvp/maps.py
    - crowd_mvp/viz/__init__.py
    - crowd_mvp/viz/heatmap.py
  modified: []

key-decisions:
  - "Zone layout: 2x2 equal grid 300x200px each, sniffer at geometric centre"
  - "POI positions: entrance(50,200), exit(550,200), bar(150,100), stand(450,100), bathroom(300,350)"
  - "SIGMA_ERROR=2.0 as global uniform sniffer noise (hook for per-node override in future)"
  - "viz/heatmap.py raises NotImplementedError — not imported in Phase 1"

patterns-established:
  - "Config pattern: all constants in crowd_mvp/config.py, imported by name across modules"
  - "Map pattern: SMALL_MAP dict with size/zones/poi; helpers return dicts not tuples for readability"

requirements-completed: [SIM-06, SIM-07, SNF-03]

# Metrics
duration: 2min
completed: 2026-05-08
---

# Phase 1 Plan 01: Foundations Summary

**crowd_mvp Python package created with SMALL_MAP (4 zones, 5 POI, 600x400 canvas), simulation constants, and viz/heatmap.py Phase 2 placeholder — all importable and verified**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-05-08T16:20:09Z
- **Completed:** 2026-05-08T16:22:xx Z
- **Tasks:** 2 of 2
- **Files modified:** 5

## Accomplishments

- Created crowd_mvp Python package with all Phase 1 foundation modules
- SMALL_MAP defines the 2x2 zone grid (A/B/C/D, each 300x200px) with 5 typed POI
- Sniffer centers correctly computed: A(150,100), B(450,100), C(150,300), D(450,300)
- All Phase 1 simulation constants defined: FPS=60, N_PEOPLE=50, SIM_DURATION=300, SIGMA_ERROR=2.0
- viz/heatmap.py placeholder present with Phase 2 implementation notes; raises NotImplementedError

## Task Commits

1. **Task 1: Create package structure and config.py** - `68ed3cd` (chore)
2. **Task 2: Create maps.py with SMALL_MAP and viz placeholder** - `aa76a8f` (feat)

## Files Created/Modified

- `crowd_mvp/__init__.py` - Empty Python package init
- `crowd_mvp/config.py` - All Phase 1 simulation constants (display, agents, sniffers, colours, fonts)
- `crowd_mvp/maps.py` - SMALL_MAP dict; get_sniffer_positions(), find_zone_for_point(), get_map_bounds()
- `crowd_mvp/viz/__init__.py` - Empty viz sub-package init
- `crowd_mvp/viz/heatmap.py` - Phase 2 placeholder: build_heatmap_surface() raises NotImplementedError

## SMALL_MAP Zone Grid and Sniffer Centers

| Zone | Rect (x, y, w, h)    | Sniffer Center |
|------|----------------------|----------------|
| A    | (0, 0, 300, 200)     | (150, 100)     |
| B    | (300, 0, 300, 200)   | (450, 100)     |
| C    | (0, 200, 300, 200)   | (150, 300)     |
| D    | (300, 200, 300, 200) | (450, 300)     |

## POI Positions

| ID       | Category      | Position    |
|----------|---------------|-------------|
| entrance | entrance      | (50, 200)   |
| exit     | exit          | (550, 200)  |
| bar      | bar           | (150, 100)  |
| stand    | sponsor_stand | (450, 100)  |
| bathroom | bathroom      | (300, 350)  |

## config.py Key Constants

| Constant              | Value              |
|-----------------------|--------------------|
| FPS                   | 60                 |
| N_PEOPLE              | 50                 |
| SIM_DURATION          | 300 (seconds)      |
| AGENT_SPEED           | 1.5 px/frame       |
| AGENT_NOISE           | 0.3 px/frame       |
| AGENT_RADIUS          | 4 px               |
| ARRIVAL_THRESHOLD     | 12 px              |
| DWELL_MIN_FRAMES      | 60 (1 sec @ 60FPS) |
| DWELL_MAX_FRAMES      | 180 (3 sec @ 60FPS)|
| SIGMA_ERROR           | 2.0                |
| SNIFFER_TICK_FRAMES   | 60                 |

## Decisions Made

- Used dict format `{'zone_id': ..., 'pos': ...}` for sniffer positions (more readable than plain tuples) — consistent with the SMALL_MAP dict pattern established in D-13
- viz/heatmap.py raises NotImplementedError rather than returning None to make Phase 2 integration obvious

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. Both verification commands passed on first run.

## User Setup Required

None - no external service configuration required. Pure Python package, no installs triggered.

## Next Phase Readiness

- crowd_mvp package fully importable; Wave 2 modules (people.py, sniffers.py) can import SMALL_MAP and config constants immediately
- All sniffer zone positions computable via get_sniffer_positions(SMALL_MAP)
- Zone membership for any (x, y) point available via find_zone_for_point()
- No blockers for Wave 2 execution

---
*Phase: 01-engine-core*
*Completed: 2026-05-08*

## Self-Check: PASSED

- FOUND: crowd_mvp/__init__.py
- FOUND: crowd_mvp/config.py
- FOUND: crowd_mvp/maps.py
- FOUND: crowd_mvp/viz/__init__.py
- FOUND: crowd_mvp/viz/heatmap.py
- FOUND commit: 68ed3cd (Task 1)
- FOUND commit: aa76a8f (Task 2)
