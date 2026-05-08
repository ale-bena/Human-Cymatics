---
phase: 01-engine-core
plan: 02
subsystem: simulation
tags: [numpy, pygame, agent, sniffer, wanderer, crowd-monitoring]

# Dependency graph
requires:
  - phase: 01-engine-core plan 01
    provides: config.py constants (AGENT_SPEED, SIGMA_ERROR, etc.), maps.py SMALL_MAP, get_sniffer_positions, find_zone_for_point

provides:
  - Agent class (people.py): wanderer steering, dwell logic, boundary clamping
  - Sniffer class (sniffers.py): zone agent counting, Gaussian noise estimation, SNF-04 data tuple

affects: [01-engine-core plan 03 (simulation.py), 01-engine-core plan 04 (renderer)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Agent pos as np.float32 array, x/y as int properties for pixel access"
    - "Sniffer tick called externally by simulation loop at frame_count % 60"
    - "σ-per-node hook: sigma stored per Sniffer instance, defaults to global SIGMA_ERROR"

key-files:
  created:
    - crowd_mvp/people.py
    - crowd_mvp/sniffers.py
  modified: []

key-decisions:
  - "Agent position stored as float32 ndarray; x/y properties return int for render compatibility"
  - "Sniffer.tick imports find_zone_for_point lazily (inside method) to avoid circular import risk"
  - "σ-per-node hook preserved as comment across 4 locations in sniffers.py per plan spec"

patterns-established:
  - "Pure NumPy simulation objects — no Pygame import in people.py or sniffers.py"
  - "Boundary clamping uses np.clip with radius offset so agents never partially leave canvas"
  - "Sniffer noise formula is exactly: max(0, round(real + N(0, sigma)))"

requirements-completed: [SIM-01, SIM-02, SIM-05, SNF-01, SNF-02, SNF-03, SNF-04, VIZ-04]

# Metrics
duration: 2min
completed: 2026-05-08
---

# Phase 1 Plan 02: Agents and Sniffers Summary

**Agent wanderer class with POI steering + dwell logic, and Sniffer class with zone-based Gaussian noise estimation exposing zone_id/pos/count/timestamp tuple**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-05-08T16:24:04Z
- **Completed:** 2026-05-08T16:25:38Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Agent class: steering toward random POIs at 1.5 px/frame + 0.3 px jitter, 1-3 second dwell on arrival, boundary clamping via np.clip (SIM-01, SIM-02, SIM-05)
- Sniffer class: counts agents in zone each tick, applies N(0, sigma) noise, exposes (zone_id, pos, estimated_count, timestamp) data tuple (SNF-01 through SNF-04)
- Both modules are pure NumPy — importable without Pygame, unit-testable independently
- σ-per-node hook preserved in 4 locations in sniffers.py for future Phase 2 heterogeneous noise

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement Agent class (people.py)** - `c1213dd` (feat)
2. **Task 2: Implement Sniffer class (sniffers.py)** - `97d75ab` (feat)

## Files Created/Modified

- `crowd_mvp/people.py` - Agent class: wanderer steering, dwell, boundary clamping
- `crowd_mvp/sniffers.py` - Sniffer class: zone counting, Gaussian noise, data property

## Decisions Made

- Agent x/y properties return `int(self.pos[0/1])` so render code can use them directly as pixel coordinates without casting
- Sniffer.tick uses a lazy import of `find_zone_for_point` inside the method body to avoid potential circular import if maps.py ever imports from sniffers.py
- sigma stored as instance attribute (`self.sigma`) so future callers can pass per-node values without changing the class interface

## Deviations from Plan

None - plan executed exactly as written.

## Boundary Test Results

- Agent: 300 update() calls from spawn (50, 200) produced final position (439, 102) — within [4, 596] x [4, 396]
- Sniffer: tick() with 10 agents returned total_estimated = 13 (noise applied to 10 agents; count >= 0 confirmed)
- SNF-04 data tuple: sniffers[0].data returned ('A', (150, 100), int, 60) — all types correct
- σ-per-node hook: grep found 4 occurrences in sniffers.py

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both Agent and Sniffer are ready to be instantiated by simulation.py (Wave 3 / Plan 03)
- Integration pattern confirmed: `Agent(spawn_pos, poi_list, map_size)` and `Sniffer(zone_id, pos)`
- simulation.py should call `agent.update()` each frame and `sniffer.tick(agents, map_def, frame_number)` every 60 frames

---
*Phase: 01-engine-core*
*Completed: 2026-05-08*
