# Phase 1: Engine Core - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 1-Engine Core
**Areas discussed:** Wanderer movement, Agent + sniffer visuals, Game loop architecture, Map zone layout

---

## Wanderer Movement

### Q1: Movement model toward POI

| Option | Description | Selected |
|--------|-------------|----------|
| Steering toward target | Normalize direction to POI, move at fixed speed + jitter. Dwell, retarget. | ✓ |
| Pure random walk | Random drift each frame, no destination. | |
| You decide | Planner chooses based on visual impact. | |

**User's choice:** Steering toward target
**Notes:** Agreed on the code pattern: `agent_pos += normalize(dx, dy) * speed + noise`

---

### Q2: Speed and noise values

| Option | Description | Selected |
|--------|-------------|----------|
| Slow + low noise | speed ~1.5 px/frame, noise ~0.3 px/frame | ✓ |
| Medium + medium noise | speed ~2.5 px/frame, noise ~0.8 px/frame | |
| You decide | Planner calibrates. | |

**User's choice:** Slow + low noise
**Notes:** Gentle drift, visible but not frantic. Good default for pitch.

---

### Q3: Dwell time at POI

| Option | Description | Selected |
|--------|-------------|----------|
| 1–3 seconds random | Each agent rolls a random dwell on arrival. | ✓ |
| Fixed 2 seconds | All agents dwell same amount. | |
| No pause | Immediate retarget. | |

**User's choice:** 1–3 seconds random

---

### Q4: Spawn position

| Option | Description | Selected |
|--------|-------------|----------|
| Spawn at entrance POI | Agents start at entrance, scatter naturally. | ✓ |
| Random positions | Agents distributed randomly at start. | |
| You decide | Planner picks whichever looks better. | |

**User's choice:** Spawn at entrance POI

---

## Agent + Sniffer Visuals

### Q1: Agent appearance

| Option | Description | Selected |
|--------|-------------|----------|
| Small filled circles, single color | Radius ~4px, light blue. Simple, fast. | ✓ |
| Colored by zone | Color changes per zone. | |
| Small dots with outline | Circle + 1px border. | |

**User's choice:** Small filled circles, single color (`(180, 220, 255)`)

---

### Q2: Sniffer icon

| Option | Description | Selected |
|--------|-------------|----------|
| WiFi arc icon | 3 concentric arcs via pygame.draw.arc. | ✓ |
| Circle with dot center | Filled circle + white center dot. | |
| Square icon | Small square with border. | |

**User's choice:** WiFi arc icon

---

### Q3: Sniffer count display

| Option | Description | Selected |
|--------|-------------|----------|
| Number label below icon | Small font, estimated count below WiFi icon, updates every tick. | ✓ |
| Tooltip on hover | Count only on mouse hover. | |
| No count in Phase 1 | Skip to Phase 2. | |

**User's choice:** Number label below icon

---

### Q4: Map background style

| Option | Description | Selected |
|--------|-------------|----------|
| Dark background, colored zone borders | Dark canvas, modern pitch aesthetic. | |
| Light grey, darker zone fills | Classic floor plan. More readable. | ✓ |
| You decide | Planner picks palette. | |

**User's choice:** Light grey, darker zone fills

---

## Game Loop Architecture

### Q1: Simulation state location

| Option | Description | Selected |
|--------|-------------|----------|
| Simulation class | Object holds all state; main.py calls update()/draw(). | ✓ |
| Module-level globals | Faster to write, messier for Phase 3 Reset. | |

**User's choice:** Simulation class

---

### Q2: Sniffer tick sync

| Option | Description | Selected |
|--------|-------------|----------|
| Frame counter | `if frame_count % 60 == 0: tick()` — simple, deterministic. | ✓ |
| Elapsed time accumulator | Correct if FPS dips. | |

**User's choice:** Frame counter

---

### Q3: Simulation-end display

| Option | Description | Selected |
|--------|-------------|----------|
| Overlay text on map | Semi-transparent overlay, frozen final state visible. | ✓ |
| Separate end screen | Clears map, shows only message. | |
| Console print + freeze | Not pitch-quality. | |

**User's choice:** Overlay text on the map

---

## Map Zone Layout

### Q1: Zone arrangement

| Option | Description | Selected |
|--------|-------------|----------|
| 2×2 equal grid | 4 equal quadrants, sniffer centered. | ✓ |
| Custom layout (unequal zones) | Realistic venue floor plan. More hardcoded geometry. | |

**User's choice:** 2×2 equal grid (600×400 → four 300×200 zones)

---

### Q2: POI definition

| Option | Description | Selected |
|--------|-------------|----------|
| Hardcoded data dict in maps.py | SMALL_MAP dict with size/zones/poi keys. | ✓ |
| Generated from zone geometry | Computed programmatically. | |

**User's choice:** Hardcoded data dict in maps.py

---

### Q3: POI rendering

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — small labeled icons | Colored shapes + short label (EN, EX, BAR, STD, WC). | ✓ |
| No — just positions in data | POI not rendered in Phase 1. | |

**User's choice:** Yes — small labeled icons

---

## Claude's Discretion

- Exact POI pixel positions (use discussion example as starting point)
- Color values for zone fills, POI icons, sniffer icon
- Font sizes for count labels and POI labels
- Light grey / dark grey hex values for the floor-plan palette

## Deferred Ideas

None — discussion stayed within Phase 1 scope.
