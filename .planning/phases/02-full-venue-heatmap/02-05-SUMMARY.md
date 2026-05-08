---
phase: 02-full-venue-heatmap
plan: "05"
subsystem: main-entrypoint
status: checkpoint
tags: [main, ui, heatmap, control-panel, tab-bar, phase2-complete]
dependency_graph:
  requires: [02-01, 02-02, 02-03, 02-04]
  provides:
    - Full Phase 2 entry point (crowd_mvp/main.py)
    - Dual-panel layout (agent view + KDE heatmap)
    - Tab bar with 3 tabs (keys 1/2/3 + click)
    - Control panel (map selector, behavior selector, 3 sliders, Reset)
    - Staged settings (map, behavior, n_people applied on Reset)
    - Live settings (sigma_error, sigma_kernel apply immediately)
  affects:
    - All Phase 3 plans (main.py is the entry point they extend)
tech_stack:
  added: []
  patterns:
    - staged-vs-live settings pattern for UI controls
    - subsurface-per-panel rendering (pygame.Surface.subsurface)
    - sniffer-tick-cadence heatmap rebuild (every 60 frames)
    - native-coordinates heatmap + scale-to-canvas transform
key_files:
  created: []
  modified:
    - crowd_mvp/main.py
decisions:
  - "All map/behavior/n_people changes staged; applied only on Reset (D-10) — prevents mid-simulation glitches"
  - "sigma_error and sigma_kernel apply live on drag (D-12) — immediate visual feedback for demo"
  - "Heatmap rebuilt every 60 frames (not every frame) to stay at 60 FPS (D-15)"
  - "build_heatmap_surface called with sim.map_size (native coords), result scaled to CANVAS_W x CANVAS_H"
  - "Initial heatmap rendered with 4 zero-count dummy positions — produces flat deep blue (D-14)"
  - "Tab 2 and Tab 3 show placeholder text on both panels (Phase 3 scope)"
metrics:
  duration: "~5 min"
  completed: "2026-05-08"
  tasks_completed: 1
  tasks_total: 2
  files_changed: 1
---

# Phase 2 Plan 05: Main.py Full Interface Summary

**One-liner:** Pygame 1200x520 interactive interface with dual panels, tab bar, horizontal control panel, staged/live settings model, and KDE heatmap display — complete Phase 2 pitch interface.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Rewrite main.py — full Phase 2 interface | 41b6515 | crowd_mvp/main.py |

## Task 2 — Awaiting Human Verification

**Type:** checkpoint:human-verify
**Status:** Paused — awaiting user to run `python crowd_mvp/main.py` and verify all 6 criteria.

## What Was Built

### Task 1 — main.py complete rewrite

Replaced the Phase 1 single-panel main.py with the full Phase 2 interface:

**Window layout (1200x520):**
- Left panel (0,0 → 600x400): agents on map, scaled via `sim.draw_scaled()`
- Right panel (600,0 → 600x400): KDE heatmap scaled from native map coords
- Tab bar (y=400, h=25): three clickable tabs
- Control panel (y=425, h=75): map/behavior buttons + 3 sliders + Reset
- Status bar (y=500, h=20): FPS, time, map, behavior, agent count

**Staged settings (apply on Reset):**
- `staged_map_key`: 'S' | 'M' | 'L' — selects from ALL_MAPS
- `staged_behavior`: 'wanderer' | 'goal' | 'social' — passed to Simulation()
- `staged_n_people`: INT — used as n_people param to Simulation()

**Live settings (apply immediately on drag):**
- `live_sigma_error`: updates `sniffer.sigma` for all sniffers on each drag event
- `live_sigma_kernel`: used on next heatmap rebuild tick

**Heatmap pipeline:**
- Every 60 frames: `sim.get_heatmap_data()` → native-coord positions/counts
- `build_heatmap_surface(positions, counts, sim.map_size, sigma_kernel)` → native-size Surface
- `pygame.transform.scale(raw, (CANVAS_W, CANVAS_H))` → panel-sized Surface
- Result blitted to right panel subsurface on Tab 1

**Initial heatmap (D-14):** Before first tick, renders 4 dummy zero-count points → flat deep blue from viridis colormap minimum.

## Verification Results

Automated structural check passed:

```
main.py syntax and structure ok
```

Acceptance criteria all met:
- WINDOW_W: 8 occurrences (≥1 required)
- build_heatmap_surface: 5 occurrences (≥2 required — import + calls)
- staged_map_key: 5 occurrences (≥3 required)
- staged_behavior: 5 occurrences (≥3 required)
- live_sigma_error: 7 occurrences (≥3 required)
- get_heatmap_data: 1 occurrence (≥1 required)
- active_tab: 11 occurrences (≥5 required)
- build_sim: 3 occurrences (≥2 required)
- draw_scaled: 1 occurrence (≥1 required)
- pygame.transform.scale: 2 occurrences (≥1 required)
- sim.map_size: 2 occurrences (≥1 required)

## Deviations from Plan

**1. [Rule 3 - Blocking Issue] Worktree missing Phase 2 modules**
- **Found during:** Pre-execution environment check
- **Issue:** Worktree was created from commit `ed50238` (before plans 02-01 through 02-04 executed). config.py was missing WINDOW_W, CANVAS_W, COLOUR_TAB_ACTIVE etc. maps.py was missing MEDIUM_MAP, LARGE_MAP, ALL_MAPS. simulation.py was missing draw_scaled(), get_heatmap_data(), map_size.
- **Fix:** Merged local main branch commit `115eb95` (the merge commit for all 4 completed plans) into the worktree branch via `git merge --no-edit 115eb95`
- **Files affected:** crowd_mvp/config.py, crowd_mvp/maps.py, crowd_mvp/simulation.py, crowd_mvp/people.py, crowd_mvp/viz/heatmap.py — all brought up to date from prior plan work
- **Commit:** Fast-forward merge (no separate commit needed; merged into branch history)

**2. [Rule 1 - Cosmetic] Greek sigma characters replaced with ASCII**
- **Found during:** Task 1 implementation
- **Issue:** Plan code used `σ_err` and `σ_kern` as slider labels, which may render as `?` on some Windows system fonts
- **Fix:** Used `sigma_err` and `sigma_kern` as slider labels (ASCII-safe)
- **Files modified:** crowd_mvp/main.py
- **Commit:** 41b6515

## Known Stubs

- **Tab 2:** Both panels show placeholder text "Tab 2 — Ground Truth Comparison (Phase 3)" — intentional; wired in Phase 3
- **Tab 3:** Both panels show placeholder text "Tab 3 — Traffic Matrix (Phase 3)" — intentional; wired in Phase 3

These stubs do not prevent the plan's goal: Phase 2 requires only Tab 1 (KDE heatmap) to be functional.

## Threat Flags

None — no new network endpoints, auth paths, or file access patterns. Slider values are clamped to [vmin, vmax] via `slider_value_from_x()` (T-02-05-03 mitigated). Heatmap is rebuilt on fixed 60-frame cadence only (T-02-05-02 mitigated).

## Self-Check: PASSED

- crowd_mvp/main.py: FOUND (modified, WINDOW_W present, 352 net lines added)
- Commit 41b6515: FOUND (feat(02-05): rewrite main.py — full Phase 2 interactive interface)
- .planning/phases/02-full-venue-heatmap/02-05-SUMMARY.md: this file
