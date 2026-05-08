---
phase: 02-full-venue-heatmap
plan: "01"
subsystem: config-maps
tags: [maps, config, data-definitions, phase2-foundation]
dependency_graph:
  requires: []
  provides:
    - MEDIUM_MAP data dict (900x600, 8 zones, 10 POI)
    - LARGE_MAP data dict (1200x800, 12 zones, 15 POI)
    - ALL_MAPS convenience dict
    - Phase 2 UI layout constants (WINDOW_W, WINDOW_H, CANVAS_W, CANVAS_H, etc.)
    - Phase 2 slider range constants
    - Phase 2 UI colour constants
  affects:
    - crowd_mvp/simulation.py (consumes map_def dict)
    - crowd_mvp/main.py (imports WINDOW_W, WINDOW_H)
    - All Phase 2 plans that need map selection or UI sizing
tech_stack:
  added: []
  patterns:
    - dict-based map schema (zones + poi arrays) matching SMALL_MAP
    - ALL_MAPS lookup dict for map selection by key ('S'/'M'/'L')
key_files:
  created: []
  modified:
    - crowd_mvp/config.py
    - crowd_mvp/maps.py
decisions:
  - MEDIUM_MAP uses 4-column x 2-row grid (225x300 each) to fill 900x600
  - LARGE_MAP uses 4-column x 3-row grid (300x266/268) with last row h=268 to reach exact 800px height
  - ALL_MAPS dict keyed by 'S'/'M'/'L' for ergonomic map selection in control panel
  - Phase 2 constants appended to config.py without removing any Phase 1 constant
metrics:
  duration: "2 min"
  completed: "2026-05-08"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 2
---

# Phase 2 Plan 01: Config and Maps Foundation Summary

**One-liner:** Phase 2 UI layout constants and MEDIUM_MAP/LARGE_MAP data dicts with full zone/POI schema matching SMALL_MAP, enabling all-map venue selection.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add Phase 2 constants to config.py | e046221 | crowd_mvp/config.py |
| 2 | Define MEDIUM_MAP and LARGE_MAP in maps.py | 71b53cf | crowd_mvp/maps.py |

## What Was Built

### Task 1 — config.py Phase 2 constants

Appended a `# Phase 2 — UI Layout` section to `crowd_mvp/config.py` containing:

- **Window/canvas sizing:** `WINDOW_W=1200`, `WINDOW_H=520`, `CANVAS_W=600`, `CANVAS_H=400`, `TAB_BAR_H=25`, `CONTROL_PANEL_H=75`, `STATUS_BAR_H=20`
- **Slider ranges:** `N_PEOPLE_MIN/MAX`, `N_PEOPLE_DEFAULT/DEFAULT_M/DEFAULT_L`, `SIGMA_ERROR_MIN/MAX`, `SIGMA_KERNEL_MIN/MAX/DEFAULT`
- **UI colours:** `COLOUR_TAB_ACTIVE/INACTIVE`, `COLOUR_BTN_ACTIVE/INACTIVE`, `COLOUR_CONTROL_BG`, `COLOUR_SLIDER_TRACK/THUMB`

All Phase 1 constants preserved unchanged.

### Task 2 — maps.py MEDIUM_MAP and LARGE_MAP

Added two new map data dicts following the exact `{'size', 'zones', 'poi'}` schema as `SMALL_MAP`:

- **MEDIUM_MAP:** 900x600 canvas, 4x2 grid of 8 zones (225x300 each), 10 POI with all 5 categories
- **LARGE_MAP:** 1200x800 canvas, 4x3 grid of 12 zones (300x266 rows 0-1, 300x268 row 2), 15 POI with all 5 categories
- **ALL_MAPS:** `{'S': SMALL_MAP, 'M': MEDIUM_MAP, 'L': LARGE_MAP}` convenience dict

`get_sniffer_positions()`, `find_zone_for_point()`, and `get_map_bounds()` work on all three maps without modification.

## Verification Results

Both verification scripts passed:

```
config ok  (Task 1)
maps ok    (Task 2)
['S', 'M', 'L']  (ALL_MAPS keys)
```

- MEDIUM_MAP: 8 zones, 10 POI, 8 sniffers via `get_sniffer_positions()`
- LARGE_MAP: 12 zones, 15 POI, 12 sniffers via `get_sniffer_positions()`

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — these are pure data definition files; no rendering or behavior logic.

## Threat Flags

None — read-only data dicts, no new network endpoints, auth paths, or trust boundary crossings. Consistent with T-02-01-01 (accept) from plan threat register.

## Self-Check: PASSED

- crowd_mvp/config.py: FOUND (modified, WINDOW_W=1200 present)
- crowd_mvp/maps.py: FOUND (modified, MEDIUM_MAP and LARGE_MAP present)
- Commit e046221: FOUND (feat(02-01): add Phase 2 UI layout and slider constants)
- Commit 71b53cf: FOUND (feat(02-01): define MEDIUM_MAP and LARGE_MAP)
