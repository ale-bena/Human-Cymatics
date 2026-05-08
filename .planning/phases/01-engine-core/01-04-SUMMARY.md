---
phase: 01-engine-core
plan: 04
subsystem: ui
tags: [pygame, python, game-loop, event-loop]

# Dependency graph
requires:
  - phase: 01-engine-core
    provides: Simulation class (simulation.py), SMALL_MAP (maps.py), config constants (config.py)
provides:
  - crowd_mvp/main.py entry point — python crowd_mvp/main.py launches full Phase 1 demo
  - 600x420 Pygame window (600x400 map + 20px status bar)
  - 60 FPS event loop calling sim.update() + sim.draw() per frame
  - Status bar displaying live FPS, elapsed time, and agent count
  - ESC key and window-close quit handlers
affects: [phase-2-full-venue, phase-3-analytics]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Thin entry point: main() owns only Pygame init + event loop; all logic in Simulation"
    - "screen.subsurface() for partitioned rendering without extra blit per frame"
    - "clock.tick(FPS) for frame-rate cap; clock.get_fps() for smoothed display"

key-files:
  created:
    - crowd_mvp/main.py
  modified: []

key-decisions:
  - "Window size 600x420 = map 600x400 + status bar 20px; status bar filled grey (200,200,200)"
  - "Status bar format: FPS | Time: elapsed/total s | Agents: N — gives investor-facing live metrics"
  - "map_surface = screen.subsurface(...) avoids extra blit per frame (Pygame partition pattern)"
  - "sim.frame_count / FPS used for elapsed time display (no separate wall-clock timer)"

patterns-established:
  - "Entry point pattern (D-09): thin loop, sim.update() + sim.draw(), no simulation logic in main"

requirements-completed:
  - LOOP-01
  - LOOP-02
  - SIM-06
  - SIM-07
  - VIZ-04

# Metrics
duration: 3min
completed: 2026-05-08
---

# Phase 1 Plan 04: main.py Entry Point Summary

**Pygame entry point wiring Simulation to 60 FPS event loop with 600x420 window and live status bar**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-05-08T00:00:00Z
- **Completed:** 2026-05-08T00:03:00Z
- **Tasks:** 1 of 1 auto tasks (checkpoint:human-verify pending user approval)
- **Files modified:** 1

## Accomplishments

- Created crowd_mvp/main.py as thin Pygame orchestration layer (D-09 pattern)
- 60 FPS event loop calling sim.update() and sim.draw(map_surface) each frame
- Status bar shows FPS, elapsed seconds vs total duration, agent count at a glance
- ESC key and window close both trigger clean pygame.quit() + sys.exit(0)
- Phase 1 Engine Core is now fully launchable: `python crowd_mvp/main.py`

## Task Commits

1. **Task 1: Create main.py entry point** - `0fc001d` (feat)

**Plan metadata:** (to be added after checkpoint approval)

## Files Created/Modified

- `crowd_mvp/main.py` - Pygame entry point: init, Simulation(SMALL_MAP), event loop, status bar render

## Window Dimensions Used

- Map area: 600 x 400 px (SMALL_MAP['size'])
- Status bar: 20 px height
- Total window: 600 x 420 px

## Status Bar Contents

`FPS: {fps:.0f}  |  Time: {elapsed:.0f}/{SIM_DURATION}s  |  Agents: {N_PEOPLE}`

- FPS: smoothed via clock.get_fps(), rendered without decimals
- Time: frame_count / FPS gives elapsed seconds vs configured duration
- Agents: constant N_PEOPLE (50) — no dynamic headcount in Phase 1

## Decisions Made

- Used `screen.subsurface(pygame.Rect(0, 0, map_w, map_h))` to share pixel buffer — simulation draws directly to the screen region, no extra blit overhead per frame
- Status bar area filled with (200, 200, 200) grey before rendering text each frame
- Elapsed time derived from `sim.frame_count / FPS` rather than wall clock for determinism
- Font size 16 for status bar text (SysFont None for cross-platform compatibility)

## Deviations from Plan

None - plan executed exactly as written. Code matched the plan template verbatim.

## Issues Encountered

None.

## Stub Scan

No stubs — main.py contains no hardcoded placeholders. All values sourced from config constants and live simulation state.

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. Only Pygame event queue handling (QUIT + K_ESCAPE) as documented in the plan's threat model.

## User Setup Required

None - no external service configuration required. Run with: `python crowd_mvp/main.py`

## Next Phase Readiness

Phase 1 Engine Core is complete pending human visual verification of the Pygame window:
- 50 agents visible as light blue circles at entrance, spreading across map
- 5 sniffer WiFi arc icons at zone centres with updating count labels
- FPS >= 55 in status bar
- "Simulation complete" overlay appears after SIM_DURATION seconds

Once checkpoint approved: Phase 2 (Full Venue + Heatmap) can begin with control panel and KDE heatmap tabs.

---
*Phase: 01-engine-core*
*Completed: 2026-05-08*

## Self-Check: PASSED

- crowd_mvp/main.py: FOUND
- .planning/phases/01-engine-core/01-04-SUMMARY.md: FOUND
- Commit 0fc001d: FOUND
