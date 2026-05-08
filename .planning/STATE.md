# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-08)

**Core value:** Il confronto "realtà vs stima WiFi sniffing" deve essere visivamente convincente e immediatamente comprensibile in 30 secondi
**Current focus:** Phase 2 — Full Venue + Heatmap

## Current Position

Phase: 2 of 3 (Full Venue + Heatmap)
Plan: 0 of 5 in current phase
Status: Ready to execute — Phase 2 planned, checker passed (2 blockers fixed)
Last activity: 2026-05-08 — Phase 2 planned: 5 plans in 3 waves, verification passed

Progress: [#####░░░░░] 33% (4/13 plans total, 5 Phase 2 plans ready)

## Performance Metrics

**Velocity:**
- Total plans completed: 4
- Average duration: 2 min
- Total execution time: ~0.1 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1: Engine Core | 4/4 | ~9 min | 2 min |

**Recent Trend:**
- Last 5 plans: 01-01 (2 min), 01-02 (2 min), 01-03 (2 min), 01-04 (3 min)
- Trend: stable

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Init: Pygame + NumPy/SciPy stack locked; no web dependencies
- Init: KDE computed via NumPy → Surface (no matplotlib embed) for 60 FPS performance
- Init: Behavior is global per run (all agents share one behavior type) to simplify MVP
- 01-01: SMALL_MAP zone layout 2x2 grid (300x200 each), sniffer at geometric centre of zone
- 01-01: POI positions entrance(50,200), exit(550,200), bar(150,100), stand(450,100), bathroom(300,350)
- 01-01: SIGMA_ERROR=2.0 as global uniform sniffer noise; hook for per-node override deferred to Phase 2
- 01-01: viz/heatmap.py raises NotImplementedError in Phase 1 — structural placeholder only
- 01-02: Agent.pos stored as float32 ndarray; x/y properties return int for render compatibility
- 01-02: Sniffer.tick lazily imports find_zone_for_point to avoid circular import risk
- 01-02: σ-per-node hook stored as self.sigma per Sniffer instance; hook comment in 4 locations
- 01-03: import math at top level (not local to _draw_sniffer) for cleaner module structure
- 01-03: WiFi arc angles 225-315 deg give upward-pointing fan in Pygame screen-coordinate system
- 01-03: frame_count incremented after sniffer tick check so first tick fires at frame 0
- 01-04: Window size 600x420 = map 600x400 + status bar 20px; status bar filled grey (200,200,200)
- 01-04: Status bar format: FPS | Time: elapsed/total s | Agents: N — live investor-facing metrics
- 01-04: screen.subsurface() pattern for zero-overhead partition rendering (no extra blit per frame)
- 01-04: Elapsed time derived from sim.frame_count / FPS for determinism

### Pending Todos

None.

### Blockers/Concerns

None.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-05-08
Stopped at: Phase 2 planned — 5 plans in 3 waves, checker passed, ready to execute
Resume file: .planning/phases/02-full-venue-heatmap/02-01-PLAN.md
