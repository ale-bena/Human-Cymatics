---
phase: 02-full-venue-heatmap
plan: "03"
subsystem: viz
tags: [pygame, scipy, gaussian_kde, numpy, matplotlib, viridis, heatmap, surfarray]

requires:
  - phase: 01-engine-core
    provides: "viz/heatmap.py stub with build_heatmap_surface() signature"

provides:
  - "build_heatmap_surface() — fully implemented KDE bivariate heatmap as pygame.Surface"
  - "SRCALPHA Surface with viridis colormap, callable in 60 FPS game loop"
  - "Graceful D-14 fallback: all-zeros input returns flat deep-blue surface"

affects: [02-05, main.py, Tab1 heatmap rendering]

tech-stack:
  added: [matplotlib (colormaps.viridis), scipy.stats.gaussian_kde]
  patterns:
    - "KDE evaluated on 60x40 internal grid, upscaled via numpy.repeat to map_size — no matplotlib GUI"
    - "Bandwidth bw = sigma_kernel / max(std_x, std_y) converts pixel-space sigma to KDE scalar"
    - "np.maximum(weights, 0.0) clamps negative sniffer counts before KDE"

key-files:
  created: []
  modified:
    - crowd_mvp/viz/heatmap.py

key-decisions:
  - "60x40 internal grid chosen for KDE evaluation — fast enough per sniffer tick, enough resolution for visual impact"
  - "bw_method = sigma_kernel / max(std_x, std_y) — translates native-pixel sigma into gaussian_kde scalar bandwidth"
  - "set_alpha(200) on final surface — keeps map geometry visible through heatmap overlay (D-17)"
  - "matplotlib installed as deviation Rule 3 — was in project stack spec but not yet installed in environment"

patterns-established:
  - "Heatmap pipeline: KDE grid → normalize → viridis RGBA → numpy repeat upscale → surfarray.make_surface → convert_alpha"
  - "_compute_density returns zeros when total_weight < 1e-6 or fewer than 2 positions (D-14 graceful degradation)"

requirements-completed: [VIZ-01]

duration: 5min
completed: 2026-05-08
---

# Phase 2 Plan 03: KDE Heatmap Surface Builder Summary

**scipy gaussian_kde bivariate heatmap rendered to SRCALPHA pygame.Surface via viridis colormap, replacing Phase 1 NotImplementedError stub**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-05-08T00:00:00Z
- **Completed:** 2026-05-08T00:05:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Replaced NotImplementedError stub with full KDE heatmap pipeline using scipy.stats.gaussian_kde
- All-zeros sniffer counts returns flat deep-blue viridis surface (D-14 graceful degradation)
- Non-uniform counts produces visible colour gradient showing density variation
- Function safe to call every sniffer tick (60 frames) with 60x40 grid evaluation — negligible CPU cost
- All three size assertions pass: 600x400, 600x400, 900x600

## Task Commits

1. **Task 1: Implement build_heatmap_surface() with scipy KDE + viridis** - `c9827ce` (feat)

**Plan metadata:** (docs commit pending)

## Files Created/Modified

- `crowd_mvp/viz/heatmap.py` - Full KDE heatmap implementation: _compute_density() with gaussian_kde, viridis colormap, numpy upscale, SRCALPHA Surface

## Decisions Made

- 60x40 internal grid: fast per-tick evaluation, sufficient visual resolution
- bw_method = sigma_kernel / max(std_x, std_y): translates pixel-space D-12 sigma into scalar KDE bandwidth
- set_alpha(200): partial transparency so underlying map geometry remains visible through heatmap (D-17)
- try/except around KDE call: graceful fallback to zeros on degenerate input (T-02-03-02 mitigation)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing matplotlib dependency**
- **Found during:** Task 1 (implementation + verification)
- **Issue:** `from matplotlib import colormaps` raised ModuleNotFoundError — matplotlib was in project stack spec but not installed in environment
- **Fix:** Ran `pip install matplotlib`
- **Files modified:** environment only (no code files)
- **Verification:** `python -c "import matplotlib; print(matplotlib.__version__)"` prints 3.10.9
- **Committed in:** not a code commit (pip install only)

---

**Total deviations:** 1 auto-fixed (1 blocking dependency)
**Impact on plan:** matplotlib is explicitly in the project stack (CLAUDE.md: "matplotlib"). Install was necessary to unblock task. No scope creep.

## Issues Encountered

None beyond the missing matplotlib package (handled via Rule 3 above).

## Threat Surface Scan

No new network endpoints, auth paths, file access patterns, or schema changes introduced. All data flows are internal simulation values (sniffer counts). Threat mitigations from plan applied:
- T-02-03-02: try/except wraps gaussian_kde call — fallback returns zeros on exception
- T-02-03-03: np.maximum(weights, 0.0) clamps negative counts before KDE

## Known Stubs

None — build_heatmap_surface() is fully implemented. No placeholder returns, no hardcoded empty values.

## Next Phase Readiness

- viz/heatmap.py is fully functional and ready for integration in main.py Tab 1 rendering (02-05)
- Function signature preserved exactly per D-16: `build_heatmap_surface(sniffer_positions, sniffer_counts, map_size, sigma_kernel=20.0)`
- sigma_kernel parameter supports live D-12 slider updates

## Self-Check: PASSED

- `crowd_mvp/viz/heatmap.py` exists and contains implementation
- Commit `c9827ce` exists in git log
- Verification script printed "heatmap ok" and exited 0
- All acceptance criteria passed: 0 NotImplementedError, 6 gaussian_kde references, 3 viridis references, 2 surfarray references

---
*Phase: 02-full-venue-heatmap*
*Completed: 2026-05-08*
