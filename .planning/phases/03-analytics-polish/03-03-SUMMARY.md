---
phase: 3
plan: "03-03"
subsystem: playback-controls
tags: [pause, resume, overlay, timer, controls]
dependency_graph:
  requires: [03-01, 03-02]
  provides: [pause-resume-toggle, end-overlay, timer-freeze]
  affects: [crowd_mvp/main.py]
tech_stack:
  added: []
  patterns: [SRCALPHA-overlay, paused-flag-gate]
key_files:
  created: []
  modified:
    - crowd_mvp/main.py
decisions:
  - "Pause button at x=1002, Reset at x=1080 — clear of sigma_kernel slider ending at x=990"
  - "Overlay uses pygame.SRCALPHA surface blit so last data frame stays visible beneath dim"
  - "sim.is_complete freeze handled by simulation.py internal guard (returns early if _complete) — no extra paused=True needed"
  - "Timer freeze is emergent: sim.frame_count stops incrementing when gated behind not paused and sim stops updating at completion"
metrics:
  duration: "4 min"
  completed: "2026-05-09"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 1
---

# Phase 3 Plan 03: Pause/Resume Controls + End Overlay Summary

Pause/Resume toggle with full-freeze logic, amber/blue visual cue button, and semi-transparent dual-panel end-of-simulation overlay with "Simulation complete / press Reset to restart" message.

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| T01 | Add paused state, pause_rect, event handling, gated sim.update | f8d3bf1 |
| T02 | Add _draw_end_overlay helper + draw call in main loop | e50f1be |

## What Was Built

**T01 — Pause/Resume control system:**
- `paused = False` state variable (auto-starts running per D-09 must-have)
- `pause_rect = pygame.Rect(1002, cp_top + 16, 70, 26)` — left of reset_rect at x=1080, clear of sigma_kernel slider
- MOUSEBUTTONDOWN handler: toggles `paused` only when `not sim.is_complete`
- `sim.update()` gated on `if not paused:` — agents, sniffers, frame_count all freeze
- Heatmap, Tab 2 compare counts, Tab 3 traffic panels all gated on same `not paused` condition
- Reset handler extended: clears `paused`, `compare_real_counts`, `compare_est_counts` before `build_sim()`
- Draw: "Pause" (blue) / "Resume" (amber) label/colour flips based on `paused` flag

**T02 — End-of-simulation overlay:**
- `_draw_end_overlay(screen, font, canvas_w, canvas_h)` function defined at module level near other helpers
- SRCALPHA pygame.Surface covers `(WINDOW_W, canvas_h)` — dual panels only, tab bar and control panel unaffected
- COLOUR_OVERLAY_BG `(20, 20, 20, 180)` gives semi-transparent dark dim (last frame remains visible)
- Two centred lines: "Simulation complete" (white) and "press Reset to restart" (light green)
- Called in draw loop after all tab content is drawn, before tab bar rendering
- Timer freeze: sim.frame_count stops at 300s because sim.update() returns early when _complete; no explicit paused=True needed

## Verification Results

```
main import OK                             # import smoke test
is_complete OK: True                       # 3-second headless sim completes correctly
traffic_matrix has transitions: 21        # zone transitions accumulated
tracked agents with history: 12           # subset tracked for Tab 3
```

All 12 acceptance criteria: PASSED.

## Deviations from Plan

None — plan executed exactly as written. The button positions (pause_rect x=1002, reset_rect x=1080) match the plan's recommended values. Timer freeze and sim completion freeze both work via the emergent gating approach described in the plan.

## Known Stubs

None. All controls are fully wired and functional.

## Threat Flags

None. No new network endpoints, auth paths, file access patterns, or schema changes introduced. This is a purely local UI change.

## Self-Check: PASSED

- crowd_mvp/main.py: FOUND (modified in-place)
- Commit f8d3bf1: FOUND (T01 — pause controls)
- Commit e50f1be: FOUND (T02 — end overlay)
- All 12 acceptance criteria checks: PASSED
