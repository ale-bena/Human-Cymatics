# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-08)

**Core value:** Il confronto "realtà vs stima WiFi sniffing" deve essere visivamente convincente e immediatamente comprensibile in 30 secondi
**Current focus:** Phase 1 — Engine Core

## Current Position

Phase: 1 of 3 (Engine Core)
Plan: 3 of 4 in current phase
Status: Executing
Last activity: 2026-05-08 — Completed Plan 03 (Simulation class): Simulation orchestrator with full update/draw cycle

Progress: [####░░░░░░] 25% (3/12 plans total)

## Performance Metrics

**Velocity:**
- Total plans completed: 3
- Average duration: 2 min
- Total execution time: ~0.1 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1: Engine Core | 3/4 | ~6 min | 2 min |

**Recent Trend:**
- Last 5 plans: 01-01 (2 min), 01-02 (2 min), 01-03 (2 min)
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

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-05-08
Stopped at: Completed Phase 1 Plan 03 (Simulation class) — ready for Plan 04 (main.py entry point)
Resume file: None
