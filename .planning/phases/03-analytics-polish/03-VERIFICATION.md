---
phase: 03-analytics-polish
verified: 2026-05-09T12:00:00Z
status: human_needed
score: 4/5 must-haves verified
overrides_applied: 0
gaps:
  - truth: "CTR-04: Input/slider durata simulazione (default 300 secondi) — user-adjustable duration"
    status: failed
    reason: "REQUIREMENTS.md CTR-04 specifies a slider or input for simulation duration. The implementation uses only a hardcoded constant SIM_DURATION=300 in config.py. No UI control for duration exists. The plan objective re-interpreted CTR-04 as merely 'SIM_DURATION constant confirmed/used' — this narrows the requirement. The requirement as written is not satisfied."
    artifacts:
      - path: "crowd_mvp/main.py"
        issue: "No duration slider defined; SIM_DURATION is always 300, never user-settable"
      - path: "crowd_mvp/config.py"
        issue: "SIM_DURATION = 300 hardcoded, no range constants defined for a duration slider"
    missing:
      - "Add a duration slider (or input field) in the control panel with a range e.g. 60–600 s, default 300 s"
      - "Wire slider value into build_sim() so Simulation is constructed with user-chosen duration"
human_verification:
  - test: "Visual quality of Tab 2 zone-fill comparison"
    expected: "When sigma_error slider is moved high (e.g. 8.0), the left and right panels show noticeably different viridis colours per zone — the pitch moment is immediately legible in under 30 seconds"
    why_human: "Cannot assess visual impact, colour perceptibility, or 30-second demo readability programmatically"
  - test: "Tab 3 trajectory light-painting effect"
    expected: "After ~30 seconds of simulation the right panel of Tab 3 shows trajectory lines that visibly brighten where agents pass repeatedly — the 'long-exposure' effect is perceptible, not just a faint uniform glow"
    why_human: "BLEND_RGBA_ADD accumulation quality depends on agent density, history length, and screen calibration — not verifiable by grep"
  - test: "Overall UI layout pitch readiness (ROADMAP SC5)"
    expected: "The 1200x520 window has consistent colours, readable labels, no overlapping UI elements — presentable to investors without apology"
    why_human: "Subjective visual polish cannot be evaluated programmatically; requires human judgment with actual window open"
  - test: "Pause / Resume button visual feedback"
    expected: "Button shows 'Pause' (blue) while running, switches to 'Resume' (amber) while paused; clicking toggles correctly; timer in status bar stops advancing while paused"
    why_human: "Requires interactive window session to verify toggle behavior and timer freeze in real time"
---

# Phase 3: Analytics + Polish Verification Report

**Phase Goal:** Analytics + Polish — Tab 2 compare viz, Tab 3 traffic viz, Start/Pause/Resume controls, timer, end-of-sim overlay. Pitch-ready demo at 300 s.
**Verified:** 2026-05-09T12:00:00Z
**Status:** human_needed (1 gap on CTR-04 + 4 human verification items)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Tab 2 left panel shows each zone flood-filled with viridis colour proportional to real count; right panel with estimated count | VERIFIED | `compare.py` `build_compare_panels()` fills each zone rect using `_viridis_colour(real_norm)` on left, `_viridis_colour(est_norm)` on right. Headless test confirms 4 zones returned by `get_zone_counts()`. |
| 2 | Both panels share the same viridis normalisation (max of real and estimated combined) | VERIFIED | `compare.py` line 56-57: `all_counts = list(real_counts.values()) + list(estimated_counts.values())` then `norm_max = max(...)`. Single shared `_VIRIDIS` instance. |
| 3 | Tab 3 shows NxN plasma-colormap matrix and trajectory density-trace with light-painting effect | VERIFIED (technical) | `traffic.py` `_draw_matrix_panel()` uses `_PLASMA` colormap; `_draw_trajectory_panel()` uses `BLEND_RGBA_ADD` accumulation. After 120 frames: 9–22 transitions accumulated, 10–15 tracked agents with 121 history entries each. Light-painting visual quality needs human check. |
| 4 | Pause stops agent movement, sniffer ticks, timer; Resume restores; button label flips | VERIFIED | `main.py` line 316: `if not paused: sim.update()`; line 320: `if not paused and sim.frame_count % 60 == 0:`. `paused = False` at startup (auto-run). `pause_label = "Resume" if paused else "Pause"` at line 458. Toggle handler at line 270. |
| 5 | At 300 s, semi-transparent overlay appears over both panels; Reset clears it | VERIFIED | `_draw_end_overlay()` at line 98-119 in `main.py`. SRCALPHA surface covers `(WINDOW_W, CANVAS_H)`. Triggered `if sim.is_complete:` line 403. Reset re-runs `build_sim()`. Headless test confirms `is_complete=True` after `duration * FPS + 5` frames. |
| 6 | CTR-04: User-adjustable simulation duration input/slider | FAILED | `SIM_DURATION = 300` hardcoded in `config.py`. No slider, input, or range constants for duration exist in `main.py`. The plan re-interpreted CTR-04 as "confirm SIM_DURATION is used" — this does not satisfy the REQUIREMENTS.md specification. |

**Score:** 4/5 roadmap success criteria verified (SC1-SC4 pass; SC5 needs human; CTR-04 requirement gap)

Note: ROADMAP SC5 (visual polish) is correctly classified as human verification, not FAILED — it requires a subjective visual judgment.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `crowd_mvp/viz/compare.py` | Tab 2 dual-panel zone-fill renderer | VERIFIED | 119 lines, substantive implementation; `build_compare_panels()`, `_viridis_colour()`, `_draw_zone_label()` all present and functional |
| `crowd_mvp/viz/traffic.py` | Tab 3 traffic matrix + trajectory renderer | VERIFIED | 154 lines; `build_traffic_panels()`, `_draw_matrix_panel()`, `_draw_trajectory_panel()`, `_PLASMA`, `_SEG_ALPHA`, `BLEND_RGBA_ADD` all present |
| `crowd_mvp/simulation.py` (get_zone_counts) | Returns real + estimated counts per zone | VERIFIED | `get_zone_counts()` at line 205; `_update_traffic_matrix()` at line 177; `traffic_matrix` and `tracked_agents` initialised at `__init__` |
| `crowd_mvp/people.py` (pos_history) | Agent position history for trajectory tracking | VERIFIED | `self._track = False`, `self.pos_history = []` at lines 42-43; tracking in all 3 update paths (dwell branch, movement branch, `SocialAgent.update_social()`) |
| `crowd_mvp/main.py` (pause controls) | Pause/Resume toggle, paused flag gate | VERIFIED | `paused = False` line 185; `pause_rect` line 218; toggle handler line 270; `if not paused:` gate lines 316, 320 |
| `crowd_mvp/main.py` (_draw_end_overlay) | End-of-sim overlay over both panels | VERIFIED | Module-level function at line 98; called at line 404; "Simulation complete" and "press Reset to restart" rendered |
| `crowd_mvp/config.py` (SIM_DURATION slider range) | Duration slider support (CTR-04) | MISSING | Only `SIM_DURATION = 300` constant; no `SIM_DURATION_MIN/MAX` range constants; no duration slider in `main.py` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `main.py` | `viz/compare.py` | `build_compare_panels()` | WIRED | Imported line 27; called in draw loop line 379; `compare_real_counts` updated on sniffer tick line 333 |
| `main.py` | `viz/traffic.py` | `build_traffic_panels()` | WIRED | Imported line 28; called in sniffer-tick block line 338; cached result blitted in Tab 3 draw block lines 396-397 |
| `main.py` | `simulation.get_zone_counts()` | sniffer-tick block | WIRED | Called line 333 inside `if not paused and sim.frame_count % 60 == 0:` |
| `main.py` | `simulation.traffic_matrix` + `tracked_agents` | `build_traffic_panels` args | WIRED | Passed at lines 339-340 |
| `simulation.py` | `people.py._track` | `Simulation.__init__` | WIRED | Lines 128-129: sets `a._track = True` and seeds `a.pos_history` for tracked agents |
| `simulation.py` | `_update_traffic_matrix()` | sniffer tick | WIRED | Line 164: called inside `if self.frame_count % SNIFFER_TICK_FRAMES == 0:` |
| pause button | `sim.update()` gate | `paused` flag | WIRED | Lines 316, 320; timer freeze emergent via `frame_count` not advancing |
| `sim.is_complete` | `_draw_end_overlay` | draw loop | WIRED | Line 403-404 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|-------------------|--------|
| `viz/compare.py` | `real_counts`, `estimated_counts` | `sim.get_zone_counts()` → `s.real_count`, `s.estimated_count` per sniffer | Yes — sniffers count agents in zones with Gaussian noise | FLOWING |
| `viz/traffic.py` (matrix) | `traffic_matrix` | `Simulation._update_traffic_matrix()` — increments on zone transitions | Yes — 9-22 transitions after 120 frames in headless test | FLOWING |
| `viz/traffic.py` (trajectory) | `tracked_agents[*].pos_history` | `Agent.update()` appends `(int(pos[0]), int(pos[1]))` each frame | Yes — 121 entries per tracked agent after 120 frames | FLOWING |
| `main.py` status bar timer | `elapsed = sim.frame_count / FPS` | `sim.frame_count` increments in `update()` | Yes — freezes when `paused=True` gates `sim.update()` | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| compare module imports cleanly | `python -c "import crowd_mvp.viz.compare; print('OK')"` | import OK | PASS |
| traffic module imports cleanly | `python -c "import crowd_mvp.viz.traffic; print('OK')"` | import OK | PASS |
| get_zone_counts returns 4-zone dict | headless sim 1 frame, assert `len(rc)==4` | `{'A': 14, 'B': 12, 'C': 12, 'D': 12}` | PASS |
| traffic_matrix accumulates transitions | headless sim 120 frames | 9 transitions, 10 tracked agents, 121 history entries | PASS |
| sim.is_complete after 3s headless | headless sim `duration=3`, `3*FPS+5` frames | `is_complete=True`, 22 transitions, 12 tracked agents | PASS |
| main module imports without error | `python -c "import crowd_mvp.main; print('OK')"` | main import OK | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| VIZ-02 | 03-01 | Tab 2 — ground truth vs estimate zone-fill comparison | SATISFIED | `compare.py` `build_compare_panels()` renders dual viridis zone-fill panels; wired in `main.py` Tab 2 block |
| VIZ-03 | 03-02 | Tab 3 — accumulated traffic matrix heatmap (plasma) + coloured trajectory lines | SATISFIED | `traffic.py` `_draw_matrix_panel()` + `_draw_trajectory_panel()` with `BLEND_RGBA_ADD`; wired in `main.py` Tab 3 block with per-tick cache |
| CTR-02 | 03-03 | Buttons Start/Pause/Reset working | SATISFIED (Pause/Reset) | `pause_rect` and `reset_rect` defined; pause toggles `paused` flag; reset calls `build_sim()`; visual feedback in button label/colour |
| CTR-03 | 03-03 | Timer display elapsed/total | SATISFIED | Status bar at line 470: `f"FPS: {fps_now:.0f}  |  Time: {elapsed:.0f}/{SIM_DURATION}s  ..."` freezes when paused |
| CTR-04 | 03-03 | Input/slider for simulation duration (default 300 s) | BLOCKED | Only `SIM_DURATION = 300` hardcoded constant. No UI slider or input for duration exists. Plan objective re-scoped this to "confirm constant used" — narrower than the requirement. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `crowd_mvp/main.py` | 374-375 | `else: right_surf.fill(COLOUR_BG)` before Tab 2/3 blocks | Info | Intentional: fills right panel with BG colour only for Tab 1 overlay cases; Tab 2/3 then overwrite via `build_compare_panels`/cache blit. Not a stub. |

No TODO/FIXME/placeholder comments found in any modified files. No old Phase 3 placeholder strings ("Tab 2 — Ground Truth Comparison (Phase 3)", "Tab 3 — Traffic Matrix (Phase 3)") present in `main.py`.

### Human Verification Required

#### 1. Tab 2 Sigma Visual Contrast

**Test:** Open `python crowd_mvp/main.py`, switch to Tab 2, drag the `sigma_err` slider to ~8.0, observe left vs right panels.
**Expected:** Left panel zones show real density colours; right panel zones show visibly different colours due to noise — the pitch moment ("WiFi estimation error") is immediately legible. The colour difference should be perceptible at a glance within 5 seconds.
**Why human:** Visual contrast and readability under high sigma cannot be evaluated programmatically.

#### 2. Tab 3 Trajectory Light-Painting

**Test:** Open the app, switch to Tab 3, let it run for ~60 seconds, observe the right panel.
**Expected:** Trajectory lines build up over time on the dark background; paths that are traversed more appear brighter (additive alpha accumulation via `BLEND_RGBA_ADD`). The effect should be visible — not a uniform dim fog.
**Why human:** `BLEND_RGBA_ADD` accumulation quality depends on screen gamma, agent count, and history density — no programmatic threshold.

#### 3. Overall UI Polish (ROADMAP SC5)

**Test:** Open the app in 1200x520 window; inspect all three tabs, the control panel, status bar, and buttons.
**Expected:** Consistent colour scheme, readable font sizes, no overlapping elements, no button or label clipping. Layout presentable to investors without apology.
**Why human:** Subjective visual judgment required.

#### 4. Pause / Resume Interactive Behavior

**Test:** Open app, let it run 5 seconds, click Pause, verify timer stops, click Resume, verify timer resumes; click Pause again at ~290s, verify overlay appears at 300s after Resume.
**Expected:** Button label flips Pause ↔ Resume; timer (`elapsed`) freezes while paused and advances while running; end-of-sim overlay appears only when running time reaches 300s (not paused time).
**Why human:** Requires interactive session; timer continuity cannot be tested headlessly without a display.

### Gaps Summary

**1 blocking gap — CTR-04 not implemented as specified.**

REQUIREMENTS.md CTR-04 states: "Input/slider durata simulazione (default 300 secondi)." The 03-03-PLAN re-interpreted this as confirming the `SIM_DURATION = 300` constant is used. The constant exists and is used, but there is no user-facing slider or input for simulation duration. This is a divergence from the stated requirement.

The gap is narrow: the fix is a single additional slider in the control panel (similar to the existing n_people/sigma sliders) with range constants in `config.py` and a wire into `build_sim()`. The rest of the CTR family (CTR-02, CTR-03) is fully implemented.

4 human verification items cover visual quality and interactive behavior that pass technical checks but require a human with the window open to confirm pitch readiness.

---

_Verified: 2026-05-09T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
