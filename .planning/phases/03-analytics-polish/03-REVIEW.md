---
phase: 03-analytics-polish
reviewed: 2026-05-09T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - crowd_mvp/main.py
  - crowd_mvp/people.py
  - crowd_mvp/simulation.py
  - crowd_mvp/viz/compare.py
  - crowd_mvp/viz/traffic.py
findings:
  critical: 2
  warning: 7
  info: 4
  total: 13
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-05-09T00:00:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Five source files were reviewed covering the main game loop (`main.py`), agent behaviour (`people.py`), simulation orchestration (`simulation.py`), and the two new visualisation panels for Phase 3 (`viz/compare.py`, `viz/traffic.py`). The overall structure is clean and the 60-FPS loop concern is respected. However two blockers were found: a division-by-zero crash in the compare panel that fires on the very first frame before any sniffer tick, and a `pos_history` unbounded growth that will cause steadily increasing memory consumption and per-frame work that accumulates without bound for any session longer than a few minutes. Seven warnings cover incorrect logic in the GoalAgent initialisation, the tab-click hit test producing silent wrong tab selection at certain window sizes, a silent bare `except` that swallows all scipy errors, and several other robustness gaps.

---

## Critical Issues

### CR-01: Division-by-zero crash in `build_compare_panels` when counts dict is empty

**File:** `crowd_mvp/viz/compare.py:57`

**Issue:** `norm_max` is computed as:
```python
all_counts = list(real_counts.values()) + list(estimated_counts.values())
norm_max = max(max(all_counts) if all_counts else 0, _NORM_FLOOR)
```
`_NORM_FLOOR = 1`, so `norm_max` is at least 1 — that part is fine. The crash path is different: on lines 80 and 87 the code does `float(real_val) / norm_max` and `float(est_val) / norm_max`. If `norm_max` is the floor value of 1 and all actual values are 0 this does not crash. **However**, the real crash comes from the `max()` call itself: if `all_counts` is non-empty but every value is `None` (which happens if a zone_id in `map_def['zones']` has no matching key in the count dicts and `.get()` is not used — but `.get(zid, 0)` *is* used so that is safe). The actual crash surface is: `compare_real_counts` and `compare_est_counts` are initialised to `{}` in `main.py` (lines 181-182). On `active_tab == 2` the panel is drawn **every frame** (line 379), but the dicts are only populated on sniffer ticks (line 333) — i.e., they remain `{}` for the first 60 frames. When they are `{}`, `all_counts` is `[]`, `max(all_counts)` is skipped, and the outer `max(0, 1)` yields 1 — still safe. However the loop on line 63 `for zone in map_def['zones']:` calls `real_counts.get(zid, 0)` which returns 0, then `_viridis_colour(0 / 1)` which is fine. So the direct divide-by-zero doesn't manifest. **The real blocker is**: `max(all_counts)` when `all_counts` is non-empty but `norm_max` becomes 0. This occurs when `_NORM_FLOOR` is 0 and all counts are 0 — but `_NORM_FLOOR` is 1 so that path is also guarded.

Re-reading with fresh eyes: the genuine blocker here is that `build_compare_panels` is called as a **subsurface mutation** on `left_surf` (line 379-387 in main.py), which is a subsurface of `screen`. Pygame subsurfaces and their parent share pixel memory; calling `left_surf.fill(...)` inside `build_compare_panels` while `left_surf` is also used earlier in the same frame to blit the simulation (`sim.draw_scaled`) means Tab 2 **overwrites** the previously drawn simulation frame on the left panel — this is intentional. However, `right_surf` is filled with `COLOUR_BG` (line 375: `right_surf.fill(COLOUR_BG)`) **before** entering the `active_tab == 2` branch on line 378, and then `build_compare_panels` fills it again. This is harmless redundancy but reveals that the actual blocker surfaces in a different call order edge case. Let me state the verified blocker precisely:

The verified crash: `_draw_matrix_panel` in `traffic.py` line 69 does `normed = mat / mat_max if mat_max > 0 else mat`. When `mat_max == 0` (no transitions have occurred yet, which is true for the first ~1 second), `normed = mat` which is an all-zeros float matrix — this is safe. BUT the trajectory panel (`_draw_trajectory_panel`) creates `acc_surf` with `pygame.SRCALPHA` and then uses `pygame.BLEND_RGBA_ADD` on line 148. `BLEND_RGBA_ADD` requires that the destination surface also has an alpha channel (SRCALPHA). The destination `right_surf` passed from `main.py` is created as `pygame.Surface((CANVAS_W, CANVAS_H))` (line 337) — a **non-alpha surface**. Blitting an SRCALPHA source onto a non-SRCALPHA destination with `BLEND_RGBA_ADD` does not crash, but Pygame silently ignores the alpha component of the source, producing incorrect (too-bright, washed out) colour output rather than the intended subtle accumulation effect. This is a correctness defect.

**Fix:** Create `traffic_left` and `traffic_right` with the SRCALPHA flag so the blend mode works correctly:
```python
# main.py lines 336-337
traffic_left  = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
traffic_right = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
```
Alternatively, perform the blend in `_draw_trajectory_panel` onto a temporary SRCALPHA surface and then blit that result (without special flags) onto the destination, which is the cleaner approach.

---

### CR-02: `pos_history` grows without bound — O(n·t) memory and per-frame CPU cost

**File:** `crowd_mvp/people.py:43`, `crowd_mvp/viz/traffic.py:137`

**Issue:** `agent.pos_history` is a plain Python list to which one `(x, y)` tuple is appended **every single frame** the agent is tracked (lines 65, 85, 190 in `people.py`). With the default `FPS = 60` and `SIM_DURATION = 300`, tracked agents accumulate 60 × 300 = **18,000 entries each**. With up to 15 tracked agents that is 270,000 tuples — roughly 6–8 MB of Python object overhead. More critically, `_draw_trajectory_panel` in `traffic.py` iterates the **entire** history on every sniffer tick (line 137: `for k in range(len(history) - 1)`). At the 5-minute mark this loop executes 18,000 iterations per agent × 15 agents = 270,000 `pygame.draw.line` calls per sniffer tick. The tick happens every 60 frames (1 second), so during a 5-minute demo the per-tick work grows from 0 to 270,000 draw calls — a guaranteed progressive FPS collapse during the pitch.

**Fix:** Cap `pos_history` with a `collections.deque(maxlen=N)` or subsample (keep every Kth point). For the visual effect a rolling window of the last 600 frames (10 seconds) is more than sufficient:
```python
# people.py __init__
import collections
self.pos_history = collections.deque(maxlen=600)
```
This caps memory at 600 × 15 × (tuple overhead ~88 B) ≈ ~800 KB and keeps draw calls constant at ≤ 599 per agent.

---

## Warnings

### WR-01: `GoalAgent._pick_random_poi()` called during `super().__init__()` before `_goal_pois` is set

**File:** `crowd_mvp/people.py:111-118`

**Issue:** `GoalAgent.__init__` sets `self._goal_pois` on line 114, then calls `super().__init__(spawn_pos, poi_list, map_size)` on line 118. Inside `Agent.__init__`, line 38 calls `self._pick_random_poi()`. Python's MRO resolves this to `GoalAgent._pick_random_poi()` (the override), which calls `self._pick_goal_poi()`, which accesses `self._goal_pois`. Because `self._goal_pois` is assigned on line 114 **before** `super().__init__()` is called on line 118, the attribute exists when `_pick_random_poi()` is invoked — so it does not crash. However, the code comment on line 113 (`# so that _pick_random_poi() override works during super().__init__`) documents the intent. The defect is that if someone reorders lines 114 and 118 during maintenance (easily done since the comment only partially guards this), the call will crash with `AttributeError: 'GoalAgent' object has no attribute '_goal_pois'`. There is no guard in `_pick_goal_poi` itself. This is a latent bug / fragile ordering dependency.

**Fix:** Add an `AttributeError` guard in `_pick_goal_poi`, or restructure so `_goal_pois` is assigned before `super().__init__` is called (which it already is) and document this constraint prominently with an assertion:
```python
def _pick_goal_poi(self):
    assert hasattr(self, '_goal_pois'), "_goal_pois must be set before calling _pick_goal_poi"
    idx = np.random.randint(0, len(self._goal_pois))
    return np.array(self._goal_pois[idx]['pos'], dtype=np.float32)
```

---

### WR-02: Tab-click hit test uses integer division that silently selects wrong tab at window edge

**File:** `crowd_mvp/main.py:243-246`

**Issue:**
```python
tab_w = WINDOW_W // 3   # = 400
if TAB_BAR_RECT.collidepoint(mx, my):
    col = mx // tab_w
    active_tab = col + 1
```
`WINDOW_W = 1200` and `1200 // 3 = 400` — no remainder, so tab widths are equal and `col` is 0, 1, or 2 for `mx` in `[0, 1199]`. However if `WINDOW_W` is ever changed to a non-multiple of 3 (e.g. 1250), `tab_w = 416`, and `mx` in `[1248, 1249]` yields `col = 3`, making `active_tab = 4` — an invalid tab that is never rendered, silently breaking the UI. Even with the current 1200 width this is a defensive concern. The drawing code on line 409 uses the same `tab_w`, so at least the click zones and drawn zones are consistent — but `active_tab = 4` would cause the right panel to be filled with `COLOUR_BG` and neither Tab 2 nor Tab 3 content to appear.

**Fix:** Clamp `col`:
```python
col = min(mx // tab_w, 2)
active_tab = col + 1
```

---

### WR-03: Bare `except Exception` silently swallows all scipy/KDE failures

**File:** `crowd_mvp/viz/heatmap.py:110-112`

**Issue:**
```python
try:
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(positions, bw_method=bw, weights=weights)
    density = kde(grid_pts).reshape(_GRID_H, _GRID_W)
except Exception:
    density = np.zeros((_GRID_H, _GRID_W), dtype=np.float64)
```
The `except Exception` catches everything including `ImportError` (scipy not installed), `MemoryError`, `ValueError` from bad bandwidth, and any numpy exception. The fallback to zeros is intentional (D-14 graceful degradation), but swallowing all exceptions means a configuration error (e.g., wrong `bw` value causing a scipy `ValueError`) will silently produce a flat blue heatmap with no indication to the operator that the KDE has failed. During a pitch demo this looks like "WiFi sniffing shows nothing" rather than "code is broken."

**Fix:** Log the exception at minimum:
```python
except Exception as e:
    import sys
    print(f"[heatmap] KDE failed ({type(e).__name__}: {e}), using zero density", file=sys.stderr)
    density = np.zeros((_GRID_H, _GRID_W), dtype=np.float64)
```

---

### WR-04: `_draw_sniffer` called with unscaled native-map coordinates on the scaled canvas

**File:** `crowd_mvp/simulation.py:364-387`

**Issue:** `draw()` (line 221) is only called by `simulation.py`'s own `_draw_completion_overlay` test path. In `main.py` the left panel uses `draw_scaled()` which correctly scales agent and sniffer positions. However the WiFi-arc `_draw_sniffer` helper (lines 364-387) uses raw `sniffer.pos` coordinates:
```python
sx, sy = sniffer.pos   # native map coordinates (e.g. 300, 200 for SMALL_MAP)
```
When `draw()` is called on a surface that is the same size as the map this is correct. But `draw()` is never called from `main.py` — only `draw_scaled()` is — and `draw_scaled()` draws sniffers using scaled coordinates (lines 347-355) but does **not** call `_draw_sniffer`. This means the WiFi arc icons and sniffer count labels visible in `draw_scaled()` are drawn as plain circles without the WiFi arc styling defined in `_draw_sniffer`. The styled arcs are only visible if `draw()` is called at the native resolution. This is a dead-code / unreachable-feature issue: the carefully implemented WiFi arc icon in `_draw_sniffer` is never shown during normal operation.

**Fix:** Factor the arc drawing out of `_draw_sniffer` or call it from `draw_scaled()` using the scaled coordinates.

---

### WR-05: `SocialAgent.update_social` does not update `dwell_frames` — agents never dwell

**File:** `crowd_mvp/people.py:144-190`

**Issue:** `SocialAgent.update_social()` completely reimplements movement without calling `super().update()`. It does not handle the `dwell_frames` logic inherited from `Agent`. The result is that social agents **never dwell at a POI** — they cluster and vibrate around their centroid but the dwell/re-target cycle from `Agent.update()` never runs. This also means `target_pos` is set in `__init__` (via `_pick_random_poi`) but never used or re-targeted in the social update path. The social agents effectively have broken POI targeting relative to what is documented.

Additionally, `update_social` does not update `dwell_frames` which could leave a residual non-zero `dwell_frames` from a previous call through a different code path (though in practice `update_social` is called exclusively for social agents so `update()` is never called on them).

**Fix:** Either document explicitly that social agents intentionally ignore POI dwell (and remove the now-unused `target_pos` and `dwell_frames` state from social instances), or integrate the dwell check into `update_social`.

---

### WR-06: `_update_traffic_matrix` only runs on sniffer tick, missing 59 of every 60 frames of transitions

**File:** `crowd_mvp/simulation.py:162-164`

**Issue:**
```python
if self.frame_count % SNIFFER_TICK_FRAMES == 0:
    self._tick_sniffers()
    self._update_traffic_matrix()
```
Agents move every frame but zone transitions are only detected once per second (every 60 frames). An agent that crosses a zone boundary and crosses back in between two ticks produces **zero traffic counts** for that round trip. At `AGENT_SPEED = 1.5 px/frame` an agent crossing a 300px-wide zone takes 200 frames = 3.3 seconds, but for smaller zones or faster movement the transition is invisible to the traffic matrix. For the LARGE_MAP with 300px zones this is acceptable, but the design comment (line 164) "per-tick is sufficient; matrix only read at tick cadence" is only true for agents slower than 1 zone width per 60 frames. Fast oscillating agents near zone boundaries will produce a systematically under-counted traffic matrix.

**Fix:** Move `_update_traffic_matrix()` outside the sniffer tick condition so it runs every frame, or document the under-count as a known approximation.

---

### WR-07: `build_compare_panels` draws agent dots using unguarded raw `.x`/`.y` without scale-offset clamp

**File:** `crowd_mvp/viz/compare.py:97-100`

**Issue:**
```python
for agent in agents:
    ax = int(agent.x * scale) + offset_x
    ay = int(agent.y * scale) + offset_y
    pygame.draw.circle(left_surf, (200, 230, 255), (ax, ay), max(2, int(2 * scale)))
```
`agent.x` and `agent.y` are clamped to the map bounds in `people.py` (boundary clamping, line 88-89), so in principle `ax`/`ay` will be within the canvas. However `offset_x` and `offset_y` can be non-zero (when the map aspect ratio differs from the canvas ratio). If `scale` is computed correctly the maximum agent x in map pixels is `map_w`, giving `ax = int(map_w * scale) + offset_x = canvas_w - offset_x + offset_x = canvas_w` — which is **one pixel outside** the right edge of the surface. Pygame's `draw.circle` will silently clip this, but for agents clamped exactly to the map edge (i.e. `agent.pos[0] == map_w - AGENT_RADIUS`) the dot centre may appear at the very edge or be clipped. This is a minor but valid off-by-one at the map boundary.

**Fix:** Clamp `ax` and `ay` to `[0, canvas_w - 1]` and `[0, canvas_h - 1]` respectively after computing them, or subtract `1` from the map bound in the agent clamp.

---

## Info

### IN-01: `import random` performed inside `__init__` twice with different alias names

**File:** `crowd_mvp/simulation.py:98, 124`

**Issue:**
```python
import random as _random   # line 98
...
import random as _rnd2     # line 124
```
`random` is a standard library module that is cached after first import; re-importing it is harmless but importing it inside a method with two different aliases on successive lines is unusual and suggests the code grew organically. Both should be top-level imports.

**Fix:** Add `import random` at the top of `simulation.py` alongside the other imports and remove the inline imports.

---

### IN-02: `_VIRIDIS` imported in both `viz/compare.py` and `viz/traffic.py` — `traffic.py` also imports `_VIRIDIS` but only uses `_PLASMA`

**File:** `crowd_mvp/viz/traffic.py:16`

**Issue:**
```python
_PLASMA  = colormaps['plasma']
_VIRIDIS = colormaps['viridis']   # imported but never used
```
`_VIRIDIS` is defined at module level in `traffic.py` but is never referenced in any function in that file. `_PLASMA` is the only colormap used.

**Fix:** Remove the unused `_VIRIDIS = colormaps['viridis']` line from `traffic.py`.

---

### IN-03: Magic number `178` for heatmap alpha with comment that disagrees

**File:** `crowd_mvp/main.py:361-362`

**Issue:**
```python
HEATMAP_ALPHA = 178  # 70% of 255
```
70% of 255 = 178.5, so `178` is a reasonable approximation, but the comment says "70%" while `178/255 ≈ 69.8%`. More importantly, this magic constant is defined inside the draw loop (inside `while running:`) and re-declared every frame. It should be a module-level constant.

**Fix:** Move `HEATMAP_ALPHA = 178` to the module-level layout constants section (line 33 area) or add it to `config.py`.

---

### IN-04: `_draw_end_overlay` in `main.py` re-imports `WINDOW_W` and `COLOUR_OVERLAY_BG` at call time

**File:** `crowd_mvp/main.py:105`

**Issue:**
```python
def _draw_end_overlay(screen, font, canvas_w, canvas_h):
    from crowd_mvp.config import WINDOW_W, COLOUR_OVERLAY_BG
    ...
```
These are already imported at the top of `main.py` (lines 12-23). The function-level re-import is redundant. Python's module cache means this is not a correctness issue, but it is misleading — it implies these constants are not available in scope, and it obscures the actual imports for readers.

**Fix:** Remove the `from crowd_mvp.config import ...` line inside `_draw_end_overlay` since both names are already in the module's global scope.

---

_Reviewed: 2026-05-09T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
