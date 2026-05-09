# Phase 3: Analytics + Polish - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-09
**Phase:** 3-Analytics-Polish
**Areas discussed:** Tab 2 comparison style, Tab 3 traffic matrix, Start/Pause logic, UI polish scope

---

## Tab 2 — Comparison Style

| Option | Description | Selected |
|--------|-------------|----------|
| Dual-panel | Left = real zone counts (viridis), right = sniffer estimated counts (viridis). Reuses dual-panel layout. | ✓ |
| Error delta overlay | Single panel, zones colored by (estimate − real). Green/red/blue error map. | |
| Split-screen + numbers | Left = real + agents, right = estimates + summary table at bottom. | |

**User's choice:** Dual-panel (Recommended)
**Notes:** Color scale question — viridis on both panels chosen for consistent visual language. Live update on sniffer tick chosen (same 1s cadence as Tab 1 heatmap).

---

## Tab 3 — Traffic Matrix

| Option | Description | Selected |
|--------|-------------|----------|
| Zone-to-zone transitions | NxN matrix[i][j] = transitions from zone i to zone j. Plasma heatmap. | ✓ |
| Time-in-zone | Cumulative seconds per zone. Bar chart or colored zone map. | |
| Claude decides | Claude picks what best showcases crowd flow. | |

**User's choice:** Zone-to-zone transitions (Recommended)

**Layout question:**

| Option | Description | Selected |
|--------|-------------|----------|
| Dual-panel: matrix left, map+trajectories right | Left = NxN plasma matrix, right = map + trajectory lines. | ✓ |
| Single panel: map+trajectories + matrix inset | Full-width map, small matrix thumbnail in corner. | |

**User's choice:** Dual-panel (Recommended)

**Trajectory question:**

| Option | Description | Selected |
|--------|-------------|----------|
| Rolling window — last 5s | Only last ~300 frames of positions. Memory-bounded, looks alive. | |
| Full cumulative | Entire path from simulation start. Dense over time. | ✓ (modified) |
| Claude decides | Claude picks window size. | |

**User's choice:** Full cumulative with brightness accumulation — where paths overlap the color becomes brighter following the plasma palette. Implemented as offscreen dark surface + low-alpha segment accumulation + plasma colormap.

**Trajectory rendering question:**

| Option | Description | Selected |
|--------|-------------|----------|
| Accumulate to offscreen surface + plasma | Low-alpha segments on dark surface → plasma colormap. Long-exposure look. | ✓ |
| Additive RGB lines | pygame.BLEND_ADD. Simpler, similar dense-area brightening. | |
| Claude decides | Claude picks approach. | |

**User's choice:** Accumulate to offscreen surface + plasma (Recommended)

---

## Start / Pause Logic

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-start (opens running) | Same as Phase 2. Start button = Pause at launch. Fast pitch demo. | ✓ |
| Paused on open | Simulation starts frozen. User clicks Start to begin. | |

**User's choice:** Auto-start (Recommended)

**Pause scope:**

| Option | Description | Selected |
|--------|-------------|----------|
| Everything — agents + timer + heatmap | Full freeze: all updates stop. Resume from exact state. | ✓ |
| Agents only, timer continues | Agents freeze, timer keeps ticking. | |

**User's choice:** Everything (Recommended)

**Duration control:**

| Option | Description | Selected |
|--------|-------------|----------|
| Slider in control panel | 60–600 s slider, default 300. Staged — applies on Reset. | |
| Hardcoded 300 s only | Fixed. Simpler. No extra slider. | ✓ |

**User's choice:** Hardcoded 300 s. One less control during the pitch.

---

## UI Polish Scope

**Branding:**

| Option | Description | Selected |
|--------|-------------|----------|
| Window title only | "Human Cymatics" in Pygame title bar. No in-window text. | ✓ |
| Header bar with title | Thin 25px header above panels. | |
| Claude decides | Claude picks most professional look. | |

**User's choice:** Window title only (Recommended). Keep map area clean.

**End screen:**

| Option | Description | Selected |
|--------|-------------|----------|
| Overlay message, keep last frame | Semi-transparent overlay over last frame. Press Reset to restart. | ✓ |
| Black screen with text | Clear to black. Loses the visual. | |
| Loop automatically | Auto-reset on completion. | |

**User's choice:** Overlay message, keep last frame (Recommended). Pitch-friendly — data stays visible.

**Start/Pause button placement:**

| Option | Description | Selected |
|--------|-------------|----------|
| Same control panel row, left of Reset | Add to existing horizontal control row. | ✓ |
| Separate row above control panel | Dedicated playback bar. More prominent, uses vertical space. | |

**User's choice:** Same control panel row, left of Reset (Recommended).

---

## Claude's Discretion

- Exact pixel width of Start/Pause button vs Reset button
- Whether the end-screen overlay is a full-panel dim or a centred card
- Normalisation strategy for Tab 2 viridis scale (per-frame max vs global max)
- NxN matrix rendering: cell size, axis labels, colorbar presence
- General colour, font, and spacing consistency within existing COLOUR_* theme

## Deferred Ideas

- Duration slider (CTR-04) — user chose hardcoded 300 s instead
- Hot colormap toggle — carried from Phase 2, still deferred
- Per-agent behaviour mix (SIM-V2-01) — v2 requirement
- Heatmap opacity slider — carried from Phase 2, still deferred
