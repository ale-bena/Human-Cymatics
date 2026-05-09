---
phase: 3
plan: "03-01"
subsystem: viz/compare
tags: [tab2, heatmap, viridis, ground-truth, sniffer-estimate]
dependency_graph:
  requires: [crowd_mvp/simulation.py, crowd_mvp/sniffers.py, crowd_mvp/viz/heatmap.py]
  provides: [crowd_mvp/viz/compare.py, Simulation.get_zone_counts()]
  affects: [crowd_mvp/main.py Tab 2]
tech_stack:
  added: [matplotlib colormaps viridis via compare.py]
  patterns: [shared-normalisation dual-panel, sniffer-tick cadence update]
key_files:
  created: [crowd_mvp/viz/compare.py]
  modified: [crowd_mvp/simulation.py, crowd_mvp/main.py]
decisions:
  - "Shared viridis normalisation uses max across real+estimated combined so colour differences are directly comparable"
  - "Panel update cadence matches sniffer tick (every 60 frames / 1 second) — no per-frame recompute"
  - "Agent dots drawn on left (Ground Truth) panel only to distinguish panels visually"
  - "Column headers drawn after build_compare_panels() call so they appear on top of zone fills"
metrics:
  duration: "4 min"
  completed: "2026-05-09"
  tasks_completed: 2
  files_changed: 3
---

# Phase 3 Plan 01: Tab 2 Zone-Fill Comparison Heatmap Summary

Dual-panel viridis zone-fill comparison for Tab 2: left shows real agent counts, right shows noisy WiFi sniffer estimates, with shared normalisation so colour differences instantly reveal estimation error.

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| T01 | Add get_zone_counts() to Simulation + create viz/compare.py | dde95d1 |
| T02 | Wire Tab 2 into main.py, replace placeholder with build_compare_panels | b2e2366 |

## What Was Built

- `crowd_mvp/viz/compare.py` — new module with `build_compare_panels()` that renders both Tab 2 panels. Uses matplotlib viridis colormap for zone fill colours, a shared normalisation max across all real+estimated counts, and contrast-adaptive text labels. Agent dots appear on the left panel only.
- `Simulation.get_zone_counts()` — returns `(real_counts, estimated_counts)` dicts keyed by zone_id, pulling directly from `sniffer.real_count` and `sniffer.estimated_count`.
- `main.py` updates — import, compare state variables (`compare_real_counts`, `compare_est_counts`) updated on sniffer tick, Tab 2 block replaced with `build_compare_panels()` call plus column headers "Ground Truth" and "WiFi Estimate".

## Verification Results

```
python -c "import crowd_mvp.viz.compare; print('import OK')"
# import OK

python -c "from crowd_mvp.simulation import Simulation; from crowd_mvp.maps import SMALL_MAP; s = Simulation(SMALL_MAP); s.update(); rc, ec = s.get_zone_counts(); assert isinstance(rc, dict); assert len(rc) == 4; print('get_zone_counts OK', rc)"
# get_zone_counts OK {'A': 11, 'B': 17, 'C': 12, 'D': 10}
```

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

Tab 3 left and right panels remain blank fills (`left_surf.fill((40, 40, 55))`, `right_surf.fill((40, 40, 55))`). This is intentional — Tab 3 content is the goal of 03-02-PLAN (Traffic Matrix).

## Threat Flags

None — no new network endpoints, auth paths, file I/O, or schema changes introduced. Pure local rendering logic.

## Self-Check: PASSED

- crowd_mvp/viz/compare.py: FOUND
- crowd_mvp/simulation.py contains get_zone_counts(): FOUND
- main.py contains build_compare_panels import: FOUND
- main.py does NOT contain "Tab 2 — Ground Truth Comparison (Phase 3)": CONFIRMED
- Commit dde95d1: FOUND
- Commit b2e2366: FOUND
