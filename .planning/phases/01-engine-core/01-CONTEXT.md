# Phase 1: Engine Core - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a runnable Pygame window: 50 wandering agents on the small map (600×400, 4 zones, 5 POI), sniffer network ticking every second with Gaussian noise, and a 60 FPS render loop. No control panel, no tabs, no KDE heatmap — those are Phase 2. This phase proves the engine core works and looks convincing enough to demo.

</domain>

<decisions>
## Implementation Decisions

### Wanderer Movement (SIM-01, SIM-02)
- **D-01:** Movement model: steering toward target POI. Each frame, agent normalizes direction to target, moves at fixed speed + small jitter. On arrival, dwells then re-targets.
- **D-02:** Speed ~1.5 px/frame, noise ~0.3 px/frame. Gentle drift, not frantic — calibrated for pitch visibility at 60 FPS.
- **D-03:** Dwell time at POI: 1–3 seconds random per arrival. Each agent rolls independently.
- **D-04:** Spawn point: all agents start at the entrance POI position. They scatter naturally from there.

### Agent + Sniffer Visuals (VIZ-04)
- **D-05:** Agent rendering: small filled circles, single color (light blue ~`(180, 220, 255)`), radius ~4px. All agents same color. Performance-first.
- **D-06:** Sniffer icon: WiFi arc shape — 3 concentric arcs of increasing radius (~6, 10, 14px) drawn with `pygame.draw.arc`.
- **D-07:** Sniffer count label: estimated count rendered as small text directly below the WiFi icon, updated every sniffer tick. Format: the raw integer (e.g. `12`).
- **D-08:** Map background: light grey canvas, darker grey fills for zone areas. Zone borders drawn as thin lines. Classic floor-plan aesthetic.

### Game Loop Architecture (LOOP-01, LOOP-02)
- **D-09:** Simulation state lives in a `Simulation` class (`crowd_mvp/simulation.py`). `main.py` creates an instance and calls `sim.update(dt)` + `sim.draw(surface)` each frame. Makes Phase 3 Reset/Pause straightforward.
- **D-10:** Sniffer tick: frame counter. `if self.frame_count % 60 == 0: self._tick_sniffers()`. Simple, deterministic. FPS target is 60 so 60 frames ≈ 1 second.
- **D-11:** Simulation end (SIM-07): centered semi-transparent overlay with "Simulation complete" text. Loop stops calling `sim.update()` but keeps rendering the final frozen state.

### Map Zone Layout (SNF-01, MAP-04, MAP-05)
- **D-12:** Zone layout: 2×2 equal grid. 600×400 map → Zone A `(0,0)-(300,200)`, Zone B `(300,0)-(600,200)`, Zone C `(0,200)-(300,400)`, Zone D `(300,200)-(600,400)`. Sniffer centered in each zone.
- **D-13:** POI definition: hardcoded data dict in `maps.py` (`SMALL_MAP` dict with `size`, `zones`, `poi` keys). 5 POI with `id`, `category`, `pos` fields. Categories: entrance, exit, bar, sponsor_stand, bathroom.
- **D-14:** POI rendering: small colored squares/circles with a short label (EN, EX, BAR, STD, WC) drawn on the map. Rendered in Phase 1 so the viewer understands venue layout immediately.

### Claude's Discretion
- Exact POI pixel positions within the map (use the example from discussion as a starting point: entrance `(50,200)`, exit `(550,200)`, bar `(150,100)`, stand `(450,100)`, bathroom `(300,350)`)
- Exact color values for zone fills, POI icon colors, sniffer icon color
- Font size for sniffer count labels and POI labels
- Exact light grey / dark grey hex values for the floor-plan palette

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Requirements
- `.planning/REQUIREMENTS.md` — Full Phase 1 requirements: SIM-01, SIM-02, SIM-05, SIM-06, SIM-07, SNF-01–SNF-04, VIZ-04, LOOP-01, LOOP-02
- `.planning/ROADMAP.md` §Phase 1 — Success criteria (5 items), dependency list
- `.planning/PROJECT.md` — Stack constraints, file layout suggestion, key decisions already locked

### No external specs
No external ADRs or design docs — all requirements captured in REQUIREMENTS.md and decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — project is fresh. No existing code.

### Established Patterns
- Stack is locked: Python 3.10+, Pygame, NumPy, SciPy. No web dependencies.
- KDE heatmap via NumPy→Surface (not matplotlib embed). Not needed in Phase 1 but planner should structure `viz/heatmap.py` as a placeholder.
- All agents share one behavior type per run (global setting). In Phase 1 this is always Wanderer.
- σ uniform across all sniffers (one global value). Hook for per-node σ should be visible in `sniffers.py` as a comment but default stays uniform.

### Integration Points
- `main.py` → instantiates `Simulation`, runs Pygame event loop, calls `sim.update()` + `sim.draw()`
- `simulation.py` → holds agents list, sniffers list, frame counter, elapsed time, simulation state (running/complete)
- `maps.py` → defines `SMALL_MAP` dict (used by both simulation init and renderer)
- `people.py` → `Agent` class with position, velocity, target POI, dwell timer
- `sniffers.py` → `Sniffer` class with zone reference, estimated_count, last_tick; σ hook comment

</code_context>

<specifics>
## Specific Ideas

- The wanderer steering pattern from discussion: `agent_pos += normalize(target - pos) * speed + noise`. On arrival (distance < threshold), roll dwell frames, then pick new random POI.
- Map data structure example from discussion:
  ```python
  SMALL_MAP = {
    'size': (600, 400),
    'zones': [
      {'id': 'A', 'rect': (0, 0, 300, 200)},
      {'id': 'B', 'rect': (300, 0, 300, 200)},
      {'id': 'C', 'rect': (0, 200, 300, 200)},
      {'id': 'D', 'rect': (300, 200, 300, 200)},
    ],
    'poi': [
      {'id': 'entrance', 'category': 'entrance', 'pos': (50, 200)},
      {'id': 'exit',     'category': 'exit',     'pos': (550, 200)},
      {'id': 'bar',      'category': 'bar',      'pos': (150, 100)},
      {'id': 'stand',    'category': 'sponsor_stand', 'pos': (450, 100)},
      {'id': 'bathroom', 'category': 'bathroom', 'pos': (300, 350)},
    ]
  }
  ```
- WiFi arc icon: 3 arcs at radii 6, 10, 14 using `pygame.draw.arc`.
- Sniffer tick: `if self.frame_count % 60 == 0: self._tick_sniffers()` in `Simulation.update()`.
- End state overlay: semi-transparent dark rect + centered white text "Simulation complete".

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 1 scope.

</deferred>

---

*Phase: 1-Engine Core*
*Context gathered: 2026-05-08*
