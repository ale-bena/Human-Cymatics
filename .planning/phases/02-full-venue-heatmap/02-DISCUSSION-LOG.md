# Phase 2: Full Venue + Heatmap - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 2-Full-Venue-Heatmap
**Areas discussed:** Window layout, Behavior semantics, Slider effect timing, Heatmap appearance

---

## Window Layout

### Q1: Where should the control panel live?

| Option | Description | Selected |
|--------|-------------|----------|
| Right side panel | Fixed panel to the right of the map | ✓ (initial) |
| Bottom panel | Horizontal bar below the map | — |
| Left side panel | Panel to the left of the map | — |

**Note:** This was later superseded by the dual-panel decision (see Heatmap section), which changed the layout to two equal map panels with the control panel at the bottom.

---

### Q2: How should the window handle larger maps?

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed map area, maps scale down | All maps render to 600×400; window never resizes | ✓ |
| Window resizes per map | Window grows to native map resolution | — |

**User's choice:** Fixed map canvas, all maps scale to 600×400.

---

### Q3: Where should the tab buttons live?

| Option | Description | Selected |
|--------|-------------|----------|
| Above the map area | Thin tab bar at top | — |
| Bottom of map area | Tab bar below maps, above status bar | ✓ |
| Inside the right panel | Tabs at top of control panel | — |

**User's choice:** Bottom of the map area.

---

## Behavior Semantics

### Q4: What should Goal-oriented agents do after visiting all POIs?

| Option | Description | Selected |
|--------|-------------|----------|
| Loop randomly forever | Pick new random POI after each visit | ✓ |
| Stop at exit after N visits | Agent walks to exit and stays | — |
| Same as Wanderer but faster | Speed increase toward POIs only | — |

**User's choice:** Loop randomly forever.

---

### Q5: What algorithm drives Social/clusterer behavior?

| Option | Description | Selected |
|--------|-------------|----------|
| Centroid attraction | Steer toward average of K nearest neighbors | ✓ |
| Density gradient following | Steer up local density gradient | — |
| Boids-style flocking | Separation + alignment + cohesion rules | — |

**User's choice:** Centroid attraction (K nearest neighbors).

---

### Q6: Which visual contrast matters most for the pitch?

| Option | Description | Selected |
|--------|-------------|----------|
| Distribution shape | Wanderer=spread, Goal=POI trails, Social=clusters | ✓ |
| Agent speed | Different speeds signal different behaviors | — |
| Both shape + speed | Combine distribution and speed differences | — |

**User's choice:** Distribution shape.

---

## Slider Effect Timing

### Q7: When do map and n_people changes take effect?

| Option | Description | Selected |
|--------|-------------|----------|
| On Reset only | Changes staged, apply on Reset | ✓ |
| Immediately on change | Instant rebuild on slider move | — |
| Prompt before applying | Confirmation dialog | — |

**User's choice:** On Reset only.

---

### Q8: How does the user trigger Reset in Phase 2?

| Option | Description | Selected |
|--------|-------------|----------|
| Add basic Reset button in Phase 2 | Reset button in control panel | ✓ |
| Keyboard shortcut R | No UI button until Phase 3 | — |
| Changes apply live where possible | σ sliders live, map/n_people deferred | — |

**User's choice:** Add a Reset button to the Phase 2 control panel.

---

### Q9: Should σ_error and σ_kernel update live?

| Option | Description | Selected |
|--------|-------------|----------|
| Both live | Both update immediately on drag | ✓ |
| Both on Reset only | Consistent staged behavior | — |
| σ_error live, σ_kernel on Reset | Split approach | — |

**User's choice:** Both σ sliders update live.

---

## Heatmap Appearance

### Q10: Which colormap?

| Option | Description | Selected |
|--------|-------------|----------|
| Hot (white→yellow→red) | Dramatic, visceral crowd heatmap look | — |
| Viridis (blue→green→yellow) | Perceptually uniform, analytical | ✓ |
| User-switchable via panel | Toggle in control panel | — |

**User's choice:** Viridis.

---

### Q11: How should the heatmap be displayed? (opacity)

**User's free-text response:** "I want the heatmap aside of the map, so duplicate the map and one has the simulation and one the heatmap"

This overrode the opacity question entirely. The user wants a **side-by-side dual-panel layout**, not an overlay. This also changed the window layout from Q1 (right-side control panel → bottom horizontal control panel).

---

### Q12: Split-screen layout — what does each panel show?

| Option | Description | Selected |
|--------|-------------|----------|
| Left: simulation \| Right: heatmap | Agents on left, KDE viridis on right | ✓ |
| Single view: heatmap only | VIZ-01 original overlay approach | — |
| Tab 1: overlay, Tab 2: split-screen | Overlap with Phase 3 VIZ-02 | — |

**User's choice:** Dual-panel: left = live agents, right = sniffer KDE heatmap.

---

### Q13: Where does the control panel go in the dual-panel layout?

| Option | Description | Selected |
|--------|-------------|----------|
| Below both panels as horizontal bar | Full-width control panel under maps | ✓ |
| Right side panel (stays right) | Both maps scaled down to fit | — |

**User's choice:** Horizontal control panel below both 600×400 map panels. Window = 1200×520.

---

### Q14: Initial heatmap state before first sniffer tick?

| Option | Description | Selected |
|--------|-------------|----------|
| Empty panel with "Waiting for data..." text | Clean initial state | — |
| Flat low-intensity heatmap from frame 0 | All-zeros = uniform minimum color | ✓ |
| Appear only after 3+ ticks | Delayed for stability | — |

**User's choice:** Flat low-intensity viridis from frame 0.

---

## Claude's Discretion

- Exact pixel heights of tab bar and control panel rows within the 520px window budget
- Exact POI positions for MEDIUM_MAP and LARGE_MAP
- KDE bandwidth units (native pixels vs. scaled canvas pixels)
- Visual style of selector button states (active/inactive highlight colors)
- Exact slider track and thumb pixel dimensions

## Deferred Ideas

- Heatmap opacity slider — initially considered, replaced by dual-panel layout decision
- Hot colormap as alternative — viridis chosen; hot available as future enhancement
- Per-agent behavior mix (SIM-V2-01) — v2 requirement, not Phase 2
