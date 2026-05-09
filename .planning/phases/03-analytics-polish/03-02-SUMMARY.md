---
phase: 3
plan: "03-02"
subsystem: viz
tags: [traffic-matrix, trajectory, tab3, heatmap, pygame]
dependency_graph:
  requires: [crowd_mvp/people.py, crowd_mvp/simulation.py, crowd_mvp/maps.py, crowd_mvp/viz/heatmap.py]
  provides: [crowd_mvp/viz/traffic.py, sim.traffic_matrix, sim.tracked_agents, Tab-3-content]
  affects: [crowd_mvp/main.py]
tech_stack:
  added: []
  patterns: [plasma-colormap-matrix, BLEND_RGBA_ADD-light-painting, per-tick-surface-cache]
key_files:
  created:
    - crowd_mvp/viz/traffic.py
  modified:
    - crowd_mvp/people.py
    - crowd_mvp/simulation.py
    - crowd_mvp/main.py
decisions:
  - "Tracking inserted in all three Agent update paths (dwell, movement, SocialAgent) so every behavior records history correctly"
  - "traffic_matrix and tracked_agents initialised at Simulation.__init__ time so they are always available on first sniffer tick"
  - "Traffic panel cache reset to None on Reset button so stale panels from previous sim do not bleed into new run"
metrics:
  duration: "3 min"
  completed: "2026-05-09"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 4
---

# Phase 3 Plan 02: Traffic Matrix + Trajectory Visualisation Summary

**One-liner:** Plasma-colormap NxN zone traffic matrix (left) and BLEND_RGBA_ADD light-painting trajectory trace (right) wired as Tab 3 with per-tick surface caching.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| T01 | Extend Agent with pos_history + Simulation with traffic matrix | f16367d | crowd_mvp/people.py, crowd_mvp/simulation.py |
| T02 | Create viz/traffic.py and wire Tab 3 in main.py | 2bc7f61 | crowd_mvp/viz/traffic.py, crowd_mvp/main.py |

## What Was Built

### T01 — Agent pos_history + Simulation traffic infrastructure

**people.py changes:**
- `Agent.__init__`: added `self._track = False` and `self.pos_history = []` after target_pos init
- `Agent.update()`: tracking appended in dwell branch (before `return`) and movement branch (between `pos += vel` and boundary clamp)
- `SocialAgent.update_social()`: tracking appended after boundary clamp at end of method

**simulation.py changes:**
- Import extended: `from crowd_mvp.maps import get_sniffer_positions, find_zone_for_point`
- Post-sniffers init block adds `self.traffic_matrix` (nested dict, zone_id → zone_id → int), `self.tracked_agents` (random 10–15 subset with `_track = True`), and `self._agent_last_zone` (initial zone per agent)
- `update()`: calls `self._update_traffic_matrix()` on every sniffer tick
- New `_update_traffic_matrix()` method: iterates all agents, detects zone transitions by comparing current to `_agent_last_zone`, increments `traffic_matrix[prev][current]`

### T02 — viz/traffic.py + Tab 3 wiring

**crowd_mvp/viz/traffic.py (new):**
- `build_traffic_panels(left_surf, right_surf, map_def, traffic_matrix, tracked_agents, canvas_w, canvas_h, font_label)` — top-level renderer called once per sniffer tick
- `_draw_matrix_panel()` — builds `np.array` from traffic_matrix, normalises, applies `_PLASMA` colormap cell-by-cell; draws row/column zone-id labels and bottom title
- `_draw_trajectory_panel()` — dark `_TRAJ_BG` fill, subtle zone outlines, per-agent segment loop onto `SRCALPHA` accumulation surface blitted with `pygame.BLEND_RGBA_ADD` for additive brightness

**crowd_mvp/main.py changes:**
- Added `from crowd_mvp.viz.traffic import build_traffic_panels`
- Added `traffic_panels_cache = None` alongside `heatmap_surface`
- Sniffer-tick block: builds `pygame.Surface` pair, calls `build_traffic_panels`, caches as `traffic_panels_cache = (traffic_left, traffic_right)`
- Tab 3 draw block: blits from cache (two `surface.blit` calls per frame) or fills dark placeholder if cache is None
- Reset button: adds `traffic_panels_cache = None` so new sim starts fresh

## Verification Results

```
traffic_matrix zones: ['A', 'B', 'C', 'D']
tracked_agents count: 12
total transitions recorded: 13
min/max history length: 121 121
```

All plan success criteria met:
- Traffic matrix accumulates nonzero values after 120 frames
- 10–15 tracked agents have pos_history fully populated (121 entries each at 120 frames)
- Import clean: `import crowd_mvp.viz.traffic` OK
- No old stub text in main.py
- Cache-based Tab 3 draw confirmed (blit only, no per-frame rebuild)

## Deviations from Plan

**1. [Rule 2 - Missing reset handling] Reset clears traffic_panels_cache**
- **Found during:** T02 implementation review
- **Issue:** Plan did not mention resetting `traffic_panels_cache` on Reset button press, but without it, stale trajectory/matrix panels from the previous simulation would be blitted for 60 frames into the new run
- **Fix:** Added `traffic_panels_cache = None` in the Reset button handler alongside existing `heatmap_surface = None`
- **Files modified:** crowd_mvp/main.py

## Known Stubs

None — Tab 3 panels display live data from simulation (traffic_matrix + pos_history).

## Threat Flags

None — no new network endpoints, auth paths, file access, or schema changes. Purely local rendering.

## Self-Check: PASSED

- crowd_mvp/viz/traffic.py exists: FOUND
- crowd_mvp/people.py contains "_track": FOUND
- crowd_mvp/simulation.py contains "traffic_matrix": FOUND
- Commit f16367d exists: FOUND
- Commit 2bc7f61 exists: FOUND
- Verification script ran without error: 13 transitions, 12 tracked agents, 121 history entries
