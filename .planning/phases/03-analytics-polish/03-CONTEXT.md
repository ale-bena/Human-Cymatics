# Phase 3: Analytics + Polish - Context

**Gathered:** 2026-05-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Complete the pitch demo end-to-end: wire Tab 2 (ground-truth vs estimate comparison), Tab 3 (traffic matrix + density-trace trajectories), and add Start/Pause/Reset controls with a full-freeze pause. Phase 3 replaces the two stub panels with working analytics visualizations and makes the overall layout polished enough to present to investors without apology. No scope creep — simulation engine, heatmap, and control panel sliders are done and not touched here beyond adding the two new buttons.

</domain>

<decisions>
## Implementation Decisions

### Tab 2 — Ground Truth vs Estimate

- **D-01:** Dual-panel layout for Tab 2: left panel = real zone densities (zones filled by actual agent count, viridis colormap), right panel = sniffer estimated counts (same viridis scale). Reuses the existing LEFT_PANEL_RECT / RIGHT_PANEL_RECT subsurface pattern.
- **D-02:** Both panels render the map geometry (zone rectangles + sniffer icons) with zones flood-filled in viridis using the same normalisation scale so mismatches are visually obvious.
- **D-03:** Each zone displays its count as a text label in the zone centre (e.g., "[12]" left, "[~9]" right). Agent dots are visible on the left panel only.
- **D-04:** Updates live on every sniffer tick (every 60 frames / 1 second) — same cadence as the heatmap. No extra computation required; data is already computed.

### Tab 3 — Traffic Matrix + Trajectories

- **D-05:** Traffic matrix tracks zone-to-zone transitions: `matrix[i][j]` increments each time an agent moves from zone i to zone j. Accumulated cumulatively from simulation start.
- **D-06:** Dual-panel for Tab 3: left panel = NxN plasma-colormap matrix heatmap, right panel = map with density-trace trajectory lines.
- **D-07:** Trajectory subset: track a fixed set of ~10–15 randomly selected agents. Full cumulative history from simulation start.
- **D-08:** Trajectory rendering: additive density-trace effect. All trajectory segments are drawn onto a dark offscreen surface with low alpha per segment. Areas where many paths overlap become brighter, following the plasma colormap applied on top. Achieves a "long-exposure light-painting" look. The offscreen surface is rebuilt each frame (or each sniffer tick) from the full history.

### Start / Pause / Reset Controls

- **D-09:** Simulation auto-starts on window open (same behaviour as Phase 2). The Start/Pause button toggles — "Pause" when running, "Resume" when frozen.
- **D-10:** Pause freezes everything: agent movement, sniffer ticks, timer, heatmap updates, Tab 2 updates, Tab 3 matrix accumulation. Full freeze — no state drifts while paused.
- **D-11:** Start/Pause button is placed in the existing horizontal control panel row, to the left of the existing Reset button. No new layout rows added.
- **D-12:** Duration is hardcoded at 300 s (SIM_DURATION constant). No duration slider in Phase 3.

### End-of-Simulation State

- **D-13:** When the simulation reaches 300 s, movement and ticking stop. A semi-transparent overlay is drawn over the dual panels with the message "Simulation complete — press Reset to restart". The last heatmap frame, Tab 2 state, and Tab 3 state remain visible beneath the overlay. Reset clears the overlay and restarts.

### UI Polish

- **D-14:** No in-window title bar or branding header. "Human Cymatics" appears in the Pygame window title only. Map area stays full-height.
- **D-15:** Claude has discretion over exact colours, font sizes, button widths, and spacing within the constraints of the existing theme (COLOUR_* constants in config.py). Consistency with Phase 2 visual style takes priority.

### Claude's Discretion

- Exact pixel width of the Start/Pause button vs Reset button in the control panel row
- Whether the overlay is a full-panel dim or just a centred card
- Normalisation strategy for the Tab 2 viridis scale (per-frame max vs global max)
- NxN matrix rendering: cell size, axis labels, colorbar presence

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` — Phase 3 requirements: VIZ-02, VIZ-03, CTR-02, CTR-03, CTR-04 (note: CTR-04 duration slider deferred — hardcoded 300 s instead)
- `.planning/ROADMAP.md` §Phase 3 — Goal, success criteria (5 items), dependencies

### Project Constraints
- `.planning/PROJECT.md` — Stack (Pygame + NumPy + SciPy + matplotlib), 60 FPS target, single-process, no web deps

### Existing Phase 2 Code (must extend, not replace)
- `crowd_mvp/main.py` — Full Phase 2 interactive interface; Tab 2/3 stubs at lines ~313–327; Start/Pause wires into the main loop here
- `crowd_mvp/config.py` — All layout constants (WINDOW_W, CANVAS_W, CANVAS_H, TAB_BAR_H, CONTROL_PANEL_H, STATUS_BAR_H, COLOUR_* palette)
- `crowd_mvp/simulation.py` — Simulation class; `get_heatmap_data()`, `draw_scaled()`, `map_size` — Phase 3 reads real zone counts from here
- `crowd_mvp/sniffers.py` — Sniffer.estimated_count and zone_id — needed for Tab 2 right panel
- `crowd_mvp/maps.py` — Zone rect data for Tab 2 zone fill rendering
- `crowd_mvp/viz/heatmap.py` — `build_heatmap_surface()` already implemented; Phase 3 adds `build_zone_heatmap_surface()` and trajectory offscreen logic in new viz modules

### Phase 2 Context (locked decisions carried forward)
- `.planning/phases/02-full-venue-heatmap/02-CONTEXT.md` — Dual-panel layout (D-01–D-05), subsurface pattern, scale transform, slider live-update behaviour

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `LEFT_PANEL_RECT` / `RIGHT_PANEL_RECT` subsurfaces (`main.py:34–35`) — Phase 3 Tab 2/3 panels use the exact same subsurface rects, no new layout needed.
- `draw_button()` helper (`main.py:43`) — reuse for the Start/Pause button.
- `sim.get_heatmap_data()` — already returns sniffer positions and estimated counts; need a parallel method or attribute for real zone counts.
- `find_zone_for_point()` (`maps.py`) — used for traffic matrix zone transition tracking (call on every agent tick when zone changes).
- `build_heatmap_surface()` (`viz/heatmap.py`) — reference pattern for new viz modules (`viz/compare.py`, `viz/traffic.py`).
- `COLOUR_*` constants (`config.py`) — viridis, plasma colourmaps via `matplotlib.cm`; same import pattern as heatmap.

### Established Patterns
- `frame_count % 60 == 0` — sniffer tick cadence; Tab 2 and Tab 3 matrix update on the same tick.
- `screen.subsurface()` — zero-overhead sub-panel rendering; all Tab 2/3 draws go to left/right subsurfaces.
- Scale transform via `scale_factor()` (`main.py:96`) — zone rects must be scaled the same way agents are scaled.
- Matplotlib colourmap → NumPy → `pygame.surfarray.make_surface` — established in `viz/heatmap.py`; reuse for zone-fill and matrix renders.

### Integration Points
- `main.py` Tab 2/3 stub block (lines ~313–327): replace placeholder text with calls to new `viz/compare.py` and `viz/traffic.py` draw functions.
- `simulation.py` or `sniffers.py`: expose real per-zone agent counts for Tab 2 left panel (ground truth). Either add `get_zone_counts()` to Simulation or read from `sim.agents` directly.
- Agent position history: `people.py` Agent class needs a position history list (or main loop accumulates it externally per tracked agent).
- Traffic matrix: either live in Simulation or accumulated externally in main loop state.

</code_context>

<specifics>
## Specific Ideas

- Tab 3 trajectory visual (user verbatim): "full cumulative, but when a line is designed and another one is designed above, the color becomes brighter following the bright palette of the heatmap" → implement as offscreen dark surface + low-alpha segment accumulation + plasma colormap normalization.
- Tab 2 dual-panel mirrors the Tab 1 dual-panel exactly (same rect, same subsurface pattern) but fills zones instead of rendering KDE heatmap.
- Start/Pause toggle label: "Pause" when running, "Resume" when paused — not a static "Play/Pause" label.
- End-screen overlay: semi-transparent dark rect over both panels + centred text. Keeps last-frame data visible so presenters can discuss the data while talking.

</specifics>

<deferred>
## Deferred Ideas

- Duration slider (CTR-04) — user explicitly chose hardcoded 300 s. Can be added in a v2 pass.
- Hot colormap toggle — discussed in Phase 2, still deferred.
- Per-agent behaviour mix (SIM-V2-01) — v2 requirement, not Phase 3.
- Heatmap opacity slider — noted as deferred in Phase 2 context.

</deferred>

---

*Phase: 3-Analytics-Polish*
*Context gathered: 2026-05-09*
