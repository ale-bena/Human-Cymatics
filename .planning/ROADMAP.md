# Roadmap: Human Cymatics — Crowd Monitoring Simulator MVP

## Overview

Three phases over 1-2 days. Phase 1 builds the runnable skeleton: a small map, wandering people, noisy sniffer reads, and a basic render loop — enough to confirm the engine works. Phase 2 expands to all maps, all behaviors, the control panel, and the KDE heatmap that is the visual centrepiece of the pitch. Phase 3 completes the analytics story with the ground-truth comparison, traffic matrix, full playback controls, and UI polish — making the 30-second demo visually convincing.

## Phases

- [x] **Phase 1: Engine Core** - Runnable simulation with small map, wanderers, sniffer network, 60 FPS render loop
- [x] **Phase 2: Full Venue + Heatmap** - All 3 maps, all 3 behaviors, control panel, Tab 1 KDE heatmap
- [x] **Phase 3: Analytics + Polish** - Tab 2 comparison, Tab 3 traffic, Start/Pause/Reset, timer, UI polish

## Phase Details

### Phase 1: Engine Core
**Goal**: A runnable Pygame window shows people moving on the small map, sniffer icons visible, noisy counts updating every second at 60 FPS
**Depends on**: Nothing (first phase)
**Requirements**: SIM-01, SIM-02, SIM-05, SIM-06, SIM-07, SNF-01, SNF-02, SNF-03, SNF-04, VIZ-04, LOOP-01, LOOP-02
**Success Criteria** (what must be TRUE):
  1. Running `python main.py` opens a Pygame window without errors
  2. Agents (dots) move continuously within the map boundary — none escape the edges
  3. Sniffer icons are visible at zone centres and update their estimated count every second
  4. The window sustains 60 FPS with 50 people on the small map (no visible freeze)
  5. After the configured duration the simulation stops and displays "Simulation complete"
**Plans**: 4 plans
Plans:
- [x] 01-PLAN-foundations.md — Package structure, config constants, SMALL_MAP data dict, viz placeholder
- [x] 01-PLAN-agents-sniffers.md — Agent wanderer class and Sniffer noisy-count class
- [x] 01-PLAN-simulation.md — Simulation orchestrator with update/draw cycle
- [x] 01-PLAN-main.md — Pygame entry point and 60 FPS event loop
**UI hint**: yes

### Phase 2: Full Venue + Heatmap
**Goal**: Users can switch between all three venue sizes, choose any behavior, adjust parameters via sliders, and see the live KDE heatmap overlaid on the map
**Depends on**: Phase 1
**Requirements**: MAP-01, MAP-02, MAP-03, MAP-04, MAP-05, SIM-03, SIM-04, CTR-01, VIZ-01, VIZ-05
**Success Criteria** (what must be TRUE):
  1. User can select small / medium / large map from the control panel and the simulation resets to that layout immediately
  2. Switching behavior to "Goal-oriented" causes people to walk toward POI and linger; switching to "Social/clusterer" causes visible crowd formation
  3. Dragging the n_people slider changes the agent count on Reset; dragging σ_error visibly changes how noisy the sniffer estimates are
  4. Tab 1 shows a smooth colour heatmap (viridis or hot) blended over the map that updates as people move
  5. Pressing keys 1 / 2 / 3 or clicking tab buttons switches the active visualisation pane
**Plans**: 5 plans
Plans:
- [x] 02-01-PLAN.md — Phase 2 config constants + MEDIUM_MAP + LARGE_MAP definitions
- [x] 02-02-PLAN.md — GoalAgent and SocialAgent classes (+ WandererAgent alias)
- [x] 02-03-PLAN.md — KDE heatmap implementation in viz/heatmap.py (viridis + scipy)
- [x] 02-04-PLAN.md — Simulation behavior param + get_heatmap_data() + all-map support
- [x] 02-05-PLAN.md — Full main.py rewrite: 1200x520 window, dual panels, tab bar, control panel
**UI hint**: yes

### Phase 3: Analytics + Polish
**Goal**: The full pitch demo runs end-to-end — ground truth vs estimate comparison, traffic matrix, playback controls, timer, and a visually polished layout that communicates the product story in under 30 seconds
**Depends on**: Phase 2
**Requirements**: VIZ-02, VIZ-03, CTR-02, CTR-03, CTR-04
**Success Criteria** (what must be TRUE):
  1. Tab 2 shows side-by-side (or overlay) of real zone densities vs sniffer estimates — the colour difference is immediately visible when σ_error is high
  2. Tab 3 shows the accumulated traffic matrix as a heatmap and draws coloured trajectory lines for a subset of agents
  3. Start / Pause / Reset buttons work correctly: Pause freezes movement, Reset returns to initial state with current settings
  4. The timer display shows elapsed / total time and counts down accurately
  5. The overall layout looks clean enough to present to investors without apology — consistent colours, readable labels, no overlapping UI elements
**Plans**: 3 plans
Plans:
- [x] 03-01-PLAN.md — Tab 2 ground-truth vs estimate dual-panel zone-fill heatmap (VIZ-02)
- [x] 03-02-PLAN.md — Tab 3 traffic matrix heatmap + trajectory density-trace offscreen render (VIZ-03)
- [x] 03-03-PLAN.md — Start/Pause/Resume button, full-freeze pause, end-overlay (CTR-02, CTR-03, CTR-04)
**UI hint**: yes

## Progress

**Execution Order:** 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Engine Core | 4/4 | Complete | 2026-05-08 |
| 2. Full Venue + Heatmap | 5/5 | Complete | 2026-05-08 |
| 3. Analytics + Polish | 3/3 | Complete | 2026-05-09 |
