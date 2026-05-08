---
phase: 02-full-venue-heatmap
plan: "04"
subsystem: simulation
tags: [simulation, behavior, heatmap, scaling, agents]
dependency_graph:
  requires: [02-01, 02-02]
  provides: [behavior-parameterized-simulation, heatmap-data-accessor, scale-aware-draw]
  affects: [crowd_mvp/main.py]
tech_stack:
  added: []
  patterns: [behavior-strategy-pattern, uniform-scale-transform]
key_files:
  created: []
  modified:
    - crowd_mvp/simulation.py
decisions:
  - "draw_scaled() handles both 'poi' and 'pois' dict keys via .get('pois', .get('poi', [])) for forward compatibility"
  - "Threat T-02-04-01 mitigated: _AGENT_CLASSES.get(behavior, WandererAgent) falls back to Wanderer on unknown strings"
  - "scale = min(canvas_w/map_w, canvas_h/map_h) preserves aspect ratio; no clipping for any supported map"
metrics:
  duration: "270s"
  completed: "2026-05-08"
  tasks_completed: 2
  files_modified: 1
---

# Phase 2 Plan 04: Behavior-Parameterized Simulation Summary

**One-liner:** Simulation extended with behavior routing (WandererAgent/GoalAgent/SocialAgent), sniffer data accessor (get_heatmap_data), and uniform-scale draw method (draw_scaled) for multi-map support.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add behavior parameter and agent routing | 436a835 | crowd_mvp/simulation.py |
| 2 | Add get_heatmap_data(), map_size, draw_scaled() | 8071908 | crowd_mvp/simulation.py |

## What Was Built

**Task 1 — Behavior parameter and agent routing:**
- `Simulation.__init__` now accepts `behavior='wanderer'|'goal'|'social'`
- Agent class selection via `_AGENT_CLASSES` dict with WandererAgent fallback (T-02-04-01 mitigation)
- `self._is_social` flag routes update loop: SocialAgents call `update_social(agents)`, others call `agent.update()`
- Import updated to include `GoalAgent, SocialAgent, WandererAgent` from `people.py`
- Backward compatible: default `behavior='wanderer'` preserves Phase 1 behavior

**Task 2 — Heatmap data accessor, map_size property, draw_scaled:**
- `get_heatmap_data()` returns `(positions, counts)` — list of `(x,y)` tuples and list of floats per sniffer
- `map_size` property exposes `map_def['size']` for main.py canvas calculations
- `draw_scaled(surface, canvas_w, canvas_h)` computes `scale = min(canvas_w/map_w, canvas_h/map_h)` and transforms all geometry (zones, POI, agents, sniffers) into canvas coordinates
- `draw()` confirmed agent-only rendering (no heatmap — D-17 naturally satisfied)

## Verification Results

All verification scripts passed (exit 0):
- All three behaviors (`wanderer`, `goal`, `social`) instantiate and update on SMALL_MAP
- MEDIUM_MAP and LARGE_MAP instantiate without error
- `get_heatmap_data()` returns 4 positions/counts for SMALL_MAP, 8 for MEDIUM_MAP
- All positions are tuples, all counts are floats
- `draw_scaled()` does not raise for SMALL_MAP or LARGE_MAP rendered onto 600x400 surface
- `map_size` returns `(600, 400)` for SMALL_MAP

## Deviations from Plan

**1. [Rule 2 - Missing Critical Functionality] draw_scaled POI key fallback**
- **Found during:** Task 2 implementation
- **Issue:** Plan's draw_scaled code used `self.map_def.get('pois', [])` but maps.py uses `'poi'` key (confirmed from simulation.py draw() which uses `self.map_def['poi']`)
- **Fix:** Used `self.map_def.get('pois', self.map_def.get('poi', []))` to handle both key spellings
- **Files modified:** crowd_mvp/simulation.py
- **Commit:** 8071908

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. All inputs (behavior string, map_def) come from internal main.py calls — no external attack surface added.

## Self-Check: PASSED

- crowd_mvp/simulation.py: FOUND
- .planning/phases/02-full-venue-heatmap/02-04-SUMMARY.md: FOUND
- commit 436a835 (task 1): FOUND
- commit 8071908 (task 2): FOUND
