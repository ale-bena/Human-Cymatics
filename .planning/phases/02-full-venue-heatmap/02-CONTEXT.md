# Phase 2: Full Venue + Heatmap - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a dual-panel interactive simulator: left panel shows the live simulation (agents moving on the map), right panel shows the KDE heatmap built from sniffer estimated counts — the "realtà vs stima" story in real time. Users can switch between all three venue sizes, choose any of three behaviors (Wanderer / Goal-oriented / Social), and adjust parameters via a horizontal control panel. Tab 1 is the dual-panel view; Tabs 2 and 3 are structural placeholders for Phase 3.

No Start/Pause (Phase 3). No ground-truth comparison tab (Phase 3). No traffic matrix (Phase 3). This phase proves the visualization centrepiece works and looks convincing in 30 seconds.

</domain>

<decisions>
## Implementation Decisions

### Window Layout
- **D-01:** Dual-panel layout for Tab 1: left panel = live simulation (agents as dots), right panel = KDE heatmap (viridis colormap). Both panels update live.
- **D-02:** Window size: 1200×520px. Two 600×400 map canvases side by side, plus a ~25px tab bar below the maps, plus a ~70px horizontal control panel at the bottom, plus the existing 20px status bar (total height ~515px, round to 520).
- **D-03:** Control panel: horizontal bar spanning the full 1200px width, below the tab bar. Contents: Map selector buttons [S][M][L], Behavior selector buttons [W][G][C], n_people slider, σ_error slider, σ_kernel slider, Reset button.
- **D-04:** Tab bar: thin horizontal strip at the bottom of the map panels area (between map panels and control panel). Three tab buttons [Tab 1][Tab 2][Tab 3]. Keys 1/2/3 also trigger tab switching (VIZ-05).
- **D-05:** Fixed map canvas — all three venue maps render to 600×400 regardless of native resolution. Scale factor = min(600/map_w, 400/map_h). Agent and sniffer positions are transformed to scaled coordinates for rendering (simulation always runs in native map coordinates).

### Agent Behaviors
- **D-06:** Goal-oriented behavior (SIM-03): agent picks a random POI, steers toward it at `AGENT_SPEED`, dwells for 1–3 seconds on arrival (same dwell logic as Wanderer), then picks a new random POI. Loops forever. No exit mechanic.
- **D-07:** Social/clusterer behavior (SIM-04): centroid attraction. Each agent computes the average position of its K nearest neighbors (K=10) and steers toward that centroid. Retains a small random jitter so agents don't freeze. Creates visibly tight clusters.
- **D-08:** Visual contrast priority: distribution shape. The three behaviors should produce distinguishably different spatial distributions visible in both the agent panel and the heatmap — Wanderer = spread uniformly, Goal-oriented = concentrated around POIs, Social = tight clusters.
- **D-09:** Behavior is global per run (all agents share one behavior type). Changing behavior via the panel takes effect on Reset.

### Slider Effect Timing
- **D-10:** Map selection and n_people slider: changes are staged — they apply on Reset. The simulation continues unchanged while the user adjusts these.
- **D-11:** Phase 2 adds a Reset button to the control panel. Reset rebuilds the Simulation with the currently staged settings. Phase 3 (CTR-02) adds Start/Pause on top.
- **D-12:** σ_error and σ_kernel: live update — apply immediately on slider drag. σ_error: sniffer noise changes on the next sniffer tick (~1 second). σ_kernel: KDE bandwidth changes on the next heatmap render (~1 second). No rebuild required.

### Heatmap (VIZ-01)
- **D-13:** Colormap: viridis (blue→green→yellow). Clean, analytical look on the grey map background.
- **D-14:** Initial heatmap state: flat low-intensity viridis (all-zeros input → uniform minimum color deep blue). Transitions smoothly when sniffer data arrives after the first tick. No "waiting" text.
- **D-15:** KDE update rate: recalculated on every sniffer tick (every 60 frames / 1 second). Not every frame — only when sniffer data changes. This keeps 60 FPS achievable even on larger maps.
- **D-16:** KDE input: sniffer estimated_count values at sniffer positions. The `build_heatmap_surface()` stub in `viz/heatmap.py` already defines the correct interface — implement it here.
- **D-17:** Heatmap Surface blended onto the right panel map background (not the agent panel). The right panel shows ONLY the heatmap; the left panel shows ONLY agents + map geometry.

### Maps
- **D-18:** MEDIUM_MAP: 900×600px native, 8 zones (4×2 grid or 2×4), 10 POI (2 per category spread across zones). Sniffers at zone centroids.
- **D-19:** LARGE_MAP: 1200×800px native, 12 zones (4×3 grid), 15 POI (3 per category). Sniffers at zone centroids.
- **D-20:** POI category distribution: entrance and exit are single (1 each). Bar, sponsor_stand, bathroom scale up with map size (2 each for medium, 3 each for large) to fill 10/15 POI targets.

### Claude's Discretion
- Exact pixel dimensions of the tab bar and control panel row heights within the 520px budget
- Exact POI positions for MEDIUM_MAP and LARGE_MAP
- KDE bandwidth scaling (whether σ_kernel is in native map pixels or scaled canvas pixels)
- Visual style of the selector buttons (highlighted vs. inactive state color scheme)
- Exact slider track and thumb pixel dimensions

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Requirements
- `.planning/REQUIREMENTS.md` — Phase 2 requirements: MAP-01–MAP-05, SIM-03, SIM-04, CTR-01, VIZ-01, VIZ-05
- `.planning/ROADMAP.md` §Phase 2 — Goal, success criteria (5 items), dependencies
- `.planning/PROJECT.md` — Stack constraints, single-process constraint, 60 FPS target

### Existing Phase 1 Code
- `crowd_mvp/config.py` — All constants; Phase 2 will add new constants (window dims, slider ranges, medium/large map defaults)
- `crowd_mvp/maps.py` — SMALL_MAP structure + `get_sniffer_positions()`, `find_zone_for_point()` — patterns to follow for MEDIUM_MAP and LARGE_MAP
- `crowd_mvp/simulation.py` — `Simulation.__init__(map_def, n_people, sigma, duration)` — Phase 2 will extend this class (or wrap it) to support behavior selection and reset
- `crowd_mvp/people.py` — `Agent` class — Phase 2 adds GoalAgent and SocialAgent alongside existing WandererAgent (or extends Agent with behavior enum)
- `crowd_mvp/viz/heatmap.py` — Stub `build_heatmap_surface(sniffer_positions, sniffer_counts, map_size, sigma_kernel)` — implement this in Phase 2
- `crowd_mvp/main.py` — Entry point; Phase 2 will significantly refactor to accommodate new window layout and UI layer

### No external specs
No external ADRs or design docs beyond what's above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Simulation` class (`simulation.py:46`) — takes `map_def` dict directly; swapping maps is a matter of passing a different dict and rebuilding. Phase 2 needs a reset path that calls `Simulation.__init__` with new params.
- `maps.py:get_sniffer_positions()` — returns list of `{zone_id, pos}` dicts from any map def. Reusable for medium/large maps unchanged.
- `maps.py:find_zone_for_point()` — zone lookup by pixel. Needed for Social behavior density queries.
- `viz/heatmap.py:build_heatmap_surface()` — placeholder with correct signature. Implement using `scipy.stats.gaussian_kde` weighted by `sniffer_counts`, render to NumPy array via `matplotlib.cm.viridis`, convert with `pygame.surfarray.make_surface`.
- `config.py` colors — `COLOUR_BG`, `COLOUR_ZONE_FILL`, etc. Reuse for both panels.

### Established Patterns
- Map dict structure: `{'size': (w,h), 'zones': [{'id', 'rect'}...], 'poi': [{'id', 'category', 'pos'}...]}` — add MEDIUM_MAP and LARGE_MAP following this schema exactly.
- `screen.subsurface()` for zero-overhead panel rendering — use for left panel (simulation) and right panel (heatmap) subsurfaces.
- Frame-based timing: `frame_count % 60 == 0` for sniffer ticks — KDE recompute hooks onto the same tick.
- `Simulation.draw(surface)` renders to any pygame Surface — pass left-panel subsurface for simulation, right-panel subsurface for heatmap.

### Integration Points
- `main.py` — needs major refactor: new window size (1200×520), subsurface setup for left/right panels and control bar, UI event handling for sliders and buttons.
- `simulation.py:Simulation` — needs behavior parameter + ability to be torn down and rebuilt on Reset without restarting Pygame.
- `people.py:Agent` — needs GoalAgent and SocialAgent classes (or behavior enum + strategy pattern). Goal/Social behaviors need access to `poi_list` and `agents` list respectively.
- `sniffers.py:Sniffer` — `self.sigma` is already a per-instance attribute (Phase 1 hook). Live σ_error update = assign new sigma to all sniffers without rebuild.

</code_context>

<specifics>
## Specific Ideas

- Dual-panel layout from discussion (verbatim user request): "duplicate the map — one has the simulation and one the heatmap, side by side"
- KDE heatmap from stub notes (`viz/heatmap.py`): `scipy.stats.gaussian_kde` on sniffer positions weighted by estimated counts → NumPy array → `matplotlib.cm.viridis(normalized_array)` → `pygame.surfarray.make_surface`. Alpha blend over map background.
- Social behavior: K=10 nearest neighbors centroid attraction. Each agent steers toward `mean(positions[k_nearest])` + small jitter so clusters stay dynamic.
- Reset flow: staged settings dict in main loop; on Reset click → tear down old `Simulation` instance → create new `Simulation(staged_map, staged_n_people, current_sigma, duration)`.
- For live σ_error update: `for s in sim.sniffers: s.sigma = new_sigma` — no rebuild needed (Phase 1 hook confirmed in sniffers.py).

</specifics>

<deferred>
## Deferred Ideas

- Heatmap opacity slider — user initially considered overlay opacity control; decided on fixed dual-panel instead. Could be added to Phase 3 UI polish if needed.
- Hot colormap option — discussed viridis vs. hot; viridis chosen. Hot can be a future toggle if the pitch needs more visual drama.
- Per-agent behavior mix (SIM-V2-01) — already listed as v2 requirement; not Phase 2.

</deferred>

---

*Phase: 2-Full-Venue-Heatmap*
*Context gathered: 2026-05-08*
