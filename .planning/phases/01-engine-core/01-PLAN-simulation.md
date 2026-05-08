---
phase: 01-engine-core
plan: 03
type: execute
wave: 3
depends_on:
  - 01-PLAN-agents-sniffers
files_modified:
  - crowd_mvp/simulation.py
autonomous: true
requirements:
  - SIM-06
  - SIM-07
  - LOOP-01
  - LOOP-02

must_haves:
  truths:
    - "Simulation class initialises all agents at the entrance POI and all sniffers at zone centres"
    - "sim.update(dt) advances all agents one frame and ticks sniffers every 60 frames"
    - "sim.update() stops calling agent updates after SIM_DURATION seconds have elapsed"
    - "sim.draw(surface) renders the map background, zones, POI labels, agents, and sniffer icons"
    - "sim.is_complete property returns True after duration expires"
  artifacts:
    - path: "crowd_mvp/simulation.py"
      provides: "Simulation class orchestrating the full engine"
      exports: ["Simulation"]
      contains: "class Simulation:"
  key_links:
    - from: "crowd_mvp/main.py (Wave 4)"
      to: "crowd_mvp/simulation.py"
      via: "sim = Simulation(map_def, n_people, sigma, duration)"
      pattern: "from crowd_mvp.simulation import Simulation"
    - from: "crowd_mvp/simulation.py"
      to: "crowd_mvp/people.py"
      via: "Agent(spawn, poi_list, map_size)"
      pattern: "from crowd_mvp.people import Agent"
    - from: "crowd_mvp/simulation.py"
      to: "crowd_mvp/sniffers.py"
      via: "Sniffer(zone_id, pos, sigma)"
      pattern: "from crowd_mvp.sniffers import Sniffer"
---

<objective>
Implement the Simulation class that owns all agents and sniffers, drives the per-frame update cycle (LOOP-01), handles the 60-frame sniffer tick (LOOP-02), enforces auto-stop at duration (SIM-07), and renders the full scene including map, zones, POI, agents, and sniffer icons (VIZ-04).

Purpose: This is the central orchestrator. main.py (Wave 4) needs only to call sim.update() and sim.draw() — it should contain no simulation logic itself.
Output: crowd_mvp/simulation.py with Simulation class, fully working without main.py.
</objective>

<execution_context>
@C:/Users/AlessandroBenassi/.claude/get-shit-done/workflows/execute-plan.md
@C:/Users/AlessandroBenassi/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/01-engine-core/01-CONTEXT.md
@.planning/REQUIREMENTS.md

<interfaces>
<!-- From crowd_mvp/config.py -->
FPS = 60
N_PEOPLE = 50
SIM_DURATION = 300               # seconds
SIGMA_ERROR = 2.0
SNIFFER_TICK_FRAMES = 60
AGENT_RADIUS = 4
COLOUR_BG = (240, 240, 240)
COLOUR_ZONE_FILL = (220, 220, 220)
COLOUR_ZONE_BORDER = (160, 160, 160)
COLOUR_AGENT = (180, 220, 255)
COLOUR_SNIFFER = (60, 120, 200)
COLOUR_POI_ENTRANCE = (80, 200, 80)
COLOUR_POI_EXIT = (200, 80, 80)
COLOUR_POI_BAR = (255, 180, 0)
COLOUR_POI_STAND = (180, 100, 220)
COLOUR_POI_BATHROOM = (80, 180, 200)
COLOUR_OVERLAY_BG = (20, 20, 20, 180)
COLOUR_TEXT = (255, 255, 255)
COLOUR_LABEL = (40, 40, 40)
FONT_SIZE_LABEL = 11
FONT_SIZE_OVERLAY = 28

<!-- From crowd_mvp/maps.py -->
SMALL_MAP = { 'size': (600, 400), 'zones': [...], 'poi': [...] }
def get_sniffer_positions(map_def) -> list[dict]  # [{'zone_id': 'A', 'pos': (150,100)}, ...]

<!-- From crowd_mvp/people.py -->
class Agent:
    def __init__(self, spawn_pos, poi_list, map_size): ...
    def update(self): ...
    @property x: int
    @property y: int

<!-- From crowd_mvp/sniffers.py -->
class Sniffer:
    def __init__(self, zone_id, pos, sigma=SIGMA_ERROR): ...
    def tick(self, agents, map_def, frame_number): ...
    @property data: tuple  # (zone_id, pos, estimated_count, timestamp)
    zone_id: str
    pos: tuple
    estimated_count: int
    real_count: int
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Implement Simulation class with update logic</name>
  <files>crowd_mvp/simulation.py</files>

  <read_first>
    - .planning/phases/01-engine-core/01-CONTEXT.md (D-09, D-10, D-11, D-04 and the sniffer tick formula)
    - .planning/REQUIREMENTS.md (LOOP-01, LOOP-02, SIM-06, SIM-07)
    - crowd_mvp/config.py (all constants)
    - crowd_mvp/maps.py (SMALL_MAP, get_sniffer_positions)
    - crowd_mvp/people.py (Agent class signature)
    - crowd_mvp/sniffers.py (Sniffer class signature)
  </read_first>

  <action>
Create crowd_mvp/simulation.py. This file contains the Simulation class that owns the update loop, render, and state machine. Implement the full class as described below.

```python
# crowd_mvp/simulation.py
# Simulation class: owns agents, sniffers, frame counter, and scene render.
# D-09: main.py creates Simulation and calls sim.update(dt) + sim.draw(surface) each frame.
# LOOP-01: update advances positions + renders map + agents + sniffers every frame.
# LOOP-02: every SNIFFER_TICK_FRAMES frames, sniffers recount and update estimates.
# SIM-07: after duration seconds, sim stops updating and shows "Simulation complete".

import pygame
import numpy as np

from crowd_mvp.config import (
    FPS, N_PEOPLE, SIM_DURATION, SIGMA_ERROR, SNIFFER_TICK_FRAMES,
    AGENT_RADIUS,
    COLOUR_BG, COLOUR_ZONE_FILL, COLOUR_ZONE_BORDER,
    COLOUR_AGENT, COLOUR_SNIFFER,
    COLOUR_POI_ENTRANCE, COLOUR_POI_EXIT, COLOUR_POI_BAR,
    COLOUR_POI_STAND, COLOUR_POI_BATHROOM,
    COLOUR_OVERLAY_BG, COLOUR_TEXT, COLOUR_LABEL,
    FONT_SIZE_LABEL, FONT_SIZE_OVERLAY,
)
from crowd_mvp.maps import get_sniffer_positions
from crowd_mvp.people import Agent
from crowd_mvp.sniffers import Sniffer


# POI category → colour lookup
_POI_COLOURS = {
    'entrance':     COLOUR_POI_ENTRANCE,
    'exit':         COLOUR_POI_EXIT,
    'bar':          COLOUR_POI_BAR,
    'sponsor_stand': COLOUR_POI_STAND,
    'bathroom':     COLOUR_POI_BATHROOM,
}

# POI category → short label text
_POI_LABELS = {
    'entrance': 'EN',
    'exit':     'EX',
    'bar':      'BAR',
    'sponsor_stand': 'STD',
    'bathroom': 'WC',
}


class Simulation:
    """Central simulation orchestrator.

    Usage:
        sim = Simulation(map_def, n_people=50, sigma=2.0, duration=300)
        # each frame:
        sim.update()
        sim.draw(screen_surface)
        if sim.is_complete:
            ...
    """

    def __init__(self, map_def, n_people=N_PEOPLE, sigma=SIGMA_ERROR, duration=SIM_DURATION):
        """
        Args:
            map_def:   map definition dict (SMALL_MAP or future maps)
            n_people:  number of agents to spawn (SIM-06)
            sigma:     Gaussian noise std dev for all sniffers (SNF-03)
            duration:  seconds before auto-stop (SIM-07)
        """
        self.map_def = map_def
        self.n_people = n_people
        self.sigma = sigma
        self.duration = duration
        self.duration_frames = int(duration * FPS)

        self.frame_count = 0
        self._complete = False

        # Pygame font — initialised lazily on first draw() call
        self._font_label = None
        self._font_overlay = None

        # Spawn all agents at entrance POI (D-04)
        entrance = next(
            p for p in map_def['poi'] if p['category'] == 'entrance'
        )
        spawn_pos = entrance['pos']
        map_size = map_def['size']
        poi_list = map_def['poi']

        self.agents = [
            Agent(spawn_pos, poi_list, map_size)
            for _ in range(n_people)
        ]

        # Create sniffers at zone centres (SNF-01)
        sniffer_defs = get_sniffer_positions(map_def)
        self.sniffers = [
            Sniffer(s['zone_id'], s['pos'], sigma=sigma)
            for s in sniffer_defs
        ]

    @property
    def is_complete(self):
        """True after duration has elapsed (SIM-07)."""
        return self._complete

    def update(self):
        """Advance simulation one frame (LOOP-01).

        - If complete, do nothing.
        - Update all agent positions.
        - Every SNIFFER_TICK_FRAMES, tick all sniffers (LOOP-02).
        - Check for end condition (SIM-07).
        """
        if self._complete:
            return

        # Advance all agents
        for agent in self.agents:
            agent.update()

        # Sniffer tick every ~1 second (D-10, LOOP-02)
        if self.frame_count % SNIFFER_TICK_FRAMES == 0:
            self._tick_sniffers()

        self.frame_count += 1

        # Auto-stop check (SIM-07)
        if self.frame_count >= self.duration_frames:
            self._complete = True

    def _tick_sniffers(self):
        """Recount agents per zone and update noisy estimates (LOOP-02)."""
        for sniffer in self.sniffers:
            sniffer.tick(self.agents, self.map_def, self.frame_count)

    def draw(self, surface):
        """Render entire scene to surface (LOOP-01).

        Draw order (back-to-front):
          1. Background fill
          2. Zone fills and borders
          3. POI icons and labels
          4. Agent dots
          5. Sniffer WiFi icons and count labels
          6. Completion overlay (if complete)
        """
        self._ensure_fonts()

        # 1. Background
        surface.fill(COLOUR_BG)

        map_w, map_h = self.map_def['size']

        # 2. Zones (D-08)
        for zone in self.map_def['zones']:
            x, y, w, h = zone['rect']
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(surface, COLOUR_ZONE_FILL, rect)
            pygame.draw.rect(surface, COLOUR_ZONE_BORDER, rect, 1)

        # 3. POI icons and labels (D-14)
        for poi in self.map_def['poi']:
            colour = _POI_COLOURS.get(poi['category'], (200, 200, 200))
            px, py = poi['pos']
            # Small filled square, 8×8 px centred on pos
            poi_rect = pygame.Rect(px - 4, py - 4, 8, 8)
            pygame.draw.rect(surface, colour, poi_rect)
            # Short label below
            label = _POI_LABELS.get(poi['category'], '?')
            txt_surf = self._font_label.render(label, True, COLOUR_LABEL)
            surface.blit(txt_surf, (px - txt_surf.get_width() // 2, py + 6))

        # 4. Agents — filled circles (D-05)
        for agent in self.agents:
            pygame.draw.circle(surface, COLOUR_AGENT, (agent.x, agent.y), AGENT_RADIUS)

        # 5. Sniffer icons and count labels (D-06, D-07, VIZ-04)
        for sniffer in self.sniffers:
            self._draw_sniffer(surface, sniffer)

        # 6. End overlay (D-11, SIM-07)
        if self._complete:
            self._draw_completion_overlay(surface, map_w, map_h)

    def _ensure_fonts(self):
        """Initialise fonts on first draw call (Pygame must already be initialised)."""
        if self._font_label is None:
            self._font_label = pygame.font.SysFont(None, FONT_SIZE_LABEL)
        if self._font_overlay is None:
            self._font_overlay = pygame.font.SysFont(None, FONT_SIZE_OVERLAY)

    def _draw_sniffer(self, surface, sniffer):
        """Draw WiFi arc icon + count label for one sniffer (D-06, D-07, VIZ-04).

        WiFi icon: 3 concentric arcs at radii 6, 10, 14 px, centred on sniffer.pos.
        Arcs span ~180° (π radians) upward from the icon centre.
        Count label: estimated_count integer drawn directly below icon (D-07).
        """
        import math
        sx, sy = sniffer.pos

        # Draw 3 arcs of increasing radius (D-06)
        for r in (6, 10, 14):
            rect = pygame.Rect(sx - r, sy - r, r * 2, r * 2)
            # Arc from 45° to 135° (upward fan) in radians
            pygame.draw.arc(surface, COLOUR_SNIFFER, rect,
                            math.radians(225), math.radians(315), 2)

        # Centre dot
        pygame.draw.circle(surface, COLOUR_SNIFFER, (sx, sy), 3)

        # Count label (D-07): raw integer below icon
        count_str = str(sniffer.estimated_count)
        txt_surf = self._font_label.render(count_str, True, COLOUR_SNIFFER)
        surface.blit(txt_surf, (sx - txt_surf.get_width() // 2, sy + 16))

    def _draw_completion_overlay(self, surface, map_w, map_h):
        """Semi-transparent dark overlay with 'Simulation complete' text (D-11)."""
        overlay = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
        overlay.fill(COLOUR_OVERLAY_BG)
        surface.blit(overlay, (0, 0))

        msg = self._font_overlay.render("Simulation complete", True, COLOUR_TEXT)
        cx = map_w // 2 - msg.get_width() // 2
        cy = map_h // 2 - msg.get_height() // 2
        surface.blit(msg, (cx, cy))
```

Key implementation notes:
- `_draw_sniffer` imports `math` locally to avoid top-level import ordering issues. Move to top-level import if preferred.
- The arc angle range (225°–315°) draws the WiFi icon pointing upward. Adjust to (45°–135°) if the icon renders inverted — Pygame's arc uses standard math angles (0° = right, CCW positive) but y-axis is flipped on screen.
- `_ensure_fonts()` is called at the start of every draw() — safe to call repeatedly, initialises only once.
  </action>

  <verify>
    <automated>python -c "
import sys; sys.path.insert(0, '.')
import pygame
pygame.init()
from crowd_mvp.maps import SMALL_MAP
from crowd_mvp.simulation import Simulation

sim = Simulation(SMALL_MAP, n_people=10, sigma=2.0, duration=5)
assert not sim.is_complete
assert len(sim.agents) == 10
assert len(sim.sniffers) == 4

# Run 1 second of frames
for _ in range(60):
    sim.update()

# Sniffer tick should have fired at frame 0
assert any(s.timestamp == 0 for s in sim.sniffers)
assert not sim.is_complete  # 5 seconds = 300 frames, only 60 done

# Run to completion
for _ in range(300):
    sim.update()

assert sim.is_complete
print('Simulation logic OK')
pygame.quit()
"</automated>
  </verify>

  <acceptance_criteria>
    - crowd_mvp/simulation.py contains `class Simulation:`
    - crowd_mvp/simulation.py contains `def update(self):`
    - crowd_mvp/simulation.py contains `def draw(self, surface):`
    - crowd_mvp/simulation.py contains `def _tick_sniffers(self):`
    - crowd_mvp/simulation.py contains `def _draw_sniffer(self, surface, sniffer):`
    - crowd_mvp/simulation.py contains `def _draw_completion_overlay(`
    - crowd_mvp/simulation.py contains `if self.frame_count % SNIFFER_TICK_FRAMES == 0` (D-10, LOOP-02)
    - crowd_mvp/simulation.py contains `"Simulation complete"` string (SIM-07, D-11)
    - crowd_mvp/simulation.py contains `pygame.SRCALPHA` (semi-transparent overlay)
    - crowd_mvp/simulation.py contains `from crowd_mvp.people import Agent`
    - crowd_mvp/simulation.py contains `from crowd_mvp.sniffers import Sniffer`
    - After 300 frames with duration=5s (300 frames at 60 FPS), sim.is_complete is True
    - After 60 frames, at least one sniffer has timestamp == 0 (first tick at frame 0)
    - All 10 agents remain within map bounds after 360 update() calls
  </acceptance_criteria>

  <done>Simulation class orchestrates full update/draw cycle; is_complete=True after duration; sniffers tick every 60 frames; draw() renders all scene layers in correct order</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Simulation constructor args | n_people, sigma, duration passed from main.py (Phase 1: hardcoded defaults, no external input) |
| Pygame surface | draw() writes to the surface; no input validation needed for render-only operations |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-03-01 | Denial of Service | Simulation(n_people=large) | accept | Phase 1 uses hardcoded default N_PEOPLE=50; slider in Phase 2 will be bounded |
| T-03-02 | Tampering | frame_count overflow | accept | At 60 FPS × 300s = 18,000 frames max; Python int has no overflow |
| T-03-03 | Denial of Service | _ensure_fonts() on every draw() | accept | Font already initialised after first call; subsequent calls return immediately (None check) |
</threat_model>

<verification>
After task completes:
- `python -c "from crowd_mvp.simulation import Simulation; print('import OK')"` exits 0
- Simulation(SMALL_MAP, n_people=10, duration=5) initialises 10 agents at entrance, 4 sniffers
- 300 update() calls with duration=5 → is_complete=True
- 60 update() calls → sniffers[i].timestamp == 0 (first tick at frame 0 of init)
- draw() callable after pygame.init() without exceptions
</verification>

<success_criteria>
- simulation.py: Simulation class with full update/draw cycle
- LOOP-01: draw() renders background + zones + POI + agents + sniffers every call
- LOOP-02: _tick_sniffers() called every SNIFFER_TICK_FRAMES frames
- SIM-06: n_people parameter accepted with default N_PEOPLE=50
- SIM-07: auto-stop at duration_frames, overlay rendered, update() becomes no-op
</success_criteria>

<output>
After completion, create `.planning/phases/01-engine-core/01-03-SUMMARY.md` with:
- Simulation class constructor signature
- Draw order layers
- Sniffer WiFi arc angle values used (and whether they rendered correctly)
- Any deviations from plan
</output>
