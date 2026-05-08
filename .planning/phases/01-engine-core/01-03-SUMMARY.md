---
phase: 01-engine-core
plan: "03"
subsystem: simulation
tags: [pygame, numpy, simulation, orchestrator, render]

# Dependency graph
requires:
  - phase: 01-engine-core plan 01
    provides: config.py constants, maps.py SMALL_MAP + get_sniffer_positions + find_zone_for_point
  - phase: 01-engine-core plan 02
    provides: Agent class (people.py), Sniffer class (sniffers.py)
provides:
  - Simulation class in crowd_mvp/simulation.py
  - Full update/draw cycle orchestrating agents + sniffers
  - Auto-stop with is_complete property after configurable duration
  - Complete scene rendering: background, zones, POI icons, agent circles, WiFi arcs, end overlay
affects:
  - 01-engine-core plan 04 (main.py — imports Simulation and calls sim.update()/sim.draw())

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Orchestrator pattern: Simulation owns agents + sniffers, main.py is a thin runner"
    - "Lazy font init: _ensure_fonts() called each draw(), initialises only on first call"
    - "Frame-based tick: sniffer updates every SNIFFER_TICK_FRAMES (60) using frame_count % N"
    - "SRCALPHA overlay: semi-transparent completion screen via pygame.Surface with SRCALPHA flag"

key-files:
  created:
    - crowd_mvp/simulation.py
  modified: []

key-decisions:
  - "import math moved to top level (not local to _draw_sniffer) for cleaner module structure"
  - "WiFi arc angles 225-315 deg give upward-pointing fan in Pygame screen-coordinate system"
  - "Auto-stop increments frame_count before comparing to duration_frames (frame_count >= duration_frames after increment)"

patterns-established:
  - "Simulation is the sole owner of agent list and sniffer list"
  - "draw() always calls _ensure_fonts() as first step — safe to call every frame"
  - "All scene layers rendered back-to-front: BG -> zones -> POI -> agents -> sniffers -> overlay"

requirements-completed:
  - SIM-06
  - SIM-07
  - LOOP-01
  - LOOP-02

# Metrics
duration: 2min
completed: 2026-05-08
---

# Phase 1 Plan 03: Simulation Class Summary

**Simulation orchestrator with 6-layer scene renderer, 60-frame sniffer tick, and auto-stop after configurable duration using Pygame SRCALPHA overlay**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-05-08T16:27:30Z
- **Completed:** 2026-05-08T16:29:13Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Implemented Simulation class that spawns all agents at the entrance POI and places sniffers at zone geometric centres
- update() advances all agents each frame; ticks sniffers every SNIFFER_TICK_FRAMES (60 frames); sets is_complete=True after duration_frames
- draw() renders 6 layers back-to-front: background fill, zone rects, POI coloured squares + labels, agent circles, sniffer WiFi arc icons + count labels, semi-transparent completion overlay

## Task Commits

1. **Task 1: Implement Simulation class with update logic** - `25acfa7` (feat)

**Plan metadata:** _(to be added after docs commit)_

## Files Created/Modified

- `crowd_mvp/simulation.py` — Simulation class (224 lines); full update/draw orchestration

## Simulation Class Constructor Signature

```python
Simulation(map_def, n_people=N_PEOPLE, sigma=SIGMA_ERROR, duration=SIM_DURATION)
```

## Draw Order Layers

1. Background fill (`COLOUR_BG`)
2. Zone filled rects + 1-px border (`COLOUR_ZONE_FILL`, `COLOUR_ZONE_BORDER`)
3. POI 8x8 coloured squares + short text label below (`_POI_COLOURS`, `_POI_LABELS`)
4. Agent filled circles radius `AGENT_RADIUS` (`COLOUR_AGENT`)
5. Sniffer WiFi arc icon (3 concentric arcs, radii 6/10/14 px) + estimated count label (`COLOUR_SNIFFER`)
6. Completion overlay — `SRCALPHA` surface filled `COLOUR_OVERLAY_BG`, centred "Simulation complete" text (`COLOUR_TEXT`)

## Sniffer WiFi Arc Angles

- Arc start: `math.radians(225)` (225 deg)
- Arc end: `math.radians(315)` (315 deg)
- Result: upward-pointing ~90 deg fan in Pygame screen coordinates (y-axis flipped vs standard math)
- Centre dot radius 3 px drawn at sniffer position

## Decisions Made

- `import math` at top level rather than inside `_draw_sniffer` for cleaner module structure (plan noted either option acceptable)
- Arc angles 225-315 deg produce upward fan in Pygame's flipped y-axis coordinate system
- `frame_count` is incremented after the sniffer tick check so the first tick fires at frame 0 (frame_count=0 before any increment), satisfying the verification assertion `s.timestamp == 0`

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Simulation class complete; main.py (Plan 04, Wave 4) can import and use `sim = Simulation(SMALL_MAP)`, call `sim.update()` and `sim.draw(screen)` each frame
- No blockers

---
*Phase: 01-engine-core*
*Completed: 2026-05-08*
