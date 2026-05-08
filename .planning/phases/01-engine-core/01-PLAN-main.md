---
phase: 01-engine-core
plan: 04
type: execute
wave: 4
depends_on:
  - 01-PLAN-simulation
files_modified:
  - crowd_mvp/main.py
autonomous: false
requirements:
  - LOOP-01
  - LOOP-02
  - SIM-06
  - SIM-07
  - VIZ-04

must_haves:
  truths:
    - "Running `python crowd_mvp/main.py` opens a Pygame window showing the small map with agents and sniffers"
    - "Agents (dots) move continuously — none escape the map edges"
    - "Sniffer icons are visible and their count labels update every second"
    - "Window sustains 60 FPS with 50 agents on the small map"
    - "After 300 seconds (default) the window shows 'Simulation complete' overlay"
  artifacts:
    - path: "crowd_mvp/main.py"
      provides: "Entry point — Pygame event loop calling sim.update() + sim.draw()"
      contains: "def main():"
  key_links:
    - from: "crowd_mvp/main.py"
      to: "crowd_mvp/simulation.py"
      via: "sim = Simulation(SMALL_MAP)"
      pattern: "from crowd_mvp.simulation import Simulation"
    - from: "crowd_mvp/main.py"
      to: "crowd_mvp/maps.py"
      via: "import SMALL_MAP"
      pattern: "from crowd_mvp.maps import SMALL_MAP"
---

<objective>
Create the Pygame entry point: crowd_mvp/main.py. This is the thin orchestration layer that initialises Pygame, creates a Simulation instance, runs the 60 FPS event loop, and displays the FPS counter. No simulation logic belongs here.

Purpose: Without main.py the project cannot be run. This is the final piece that completes Phase 1 and produces a working, launchable demo.
Output: crowd_mvp/main.py entry point; `python crowd_mvp/main.py` opens a working window.
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
SIM_DURATION = 300
WINDOW_TITLE = "Human Cymatics — Crowd Monitor"
COLOUR_BG = (240, 240, 240)

<!-- From crowd_mvp/maps.py -->
SMALL_MAP = { 'size': (600, 400), 'zones': [...], 'poi': [...] }

<!-- From crowd_mvp/simulation.py -->
class Simulation:
    def __init__(self, map_def, n_people=N_PEOPLE, sigma=SIGMA_ERROR, duration=SIM_DURATION): ...
    def update(self): ...
    def draw(self, surface): ...
    @property is_complete: bool
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create main.py entry point</name>
  <files>crowd_mvp/main.py</files>

  <read_first>
    - .planning/phases/01-engine-core/01-CONTEXT.md (D-09, D-11 — Simulation class usage pattern)
    - .planning/REQUIREMENTS.md (LOOP-01, LOOP-02, SIM-07)
    - crowd_mvp/config.py (FPS, WINDOW_TITLE, N_PEOPLE, SIM_DURATION)
    - crowd_mvp/maps.py (SMALL_MAP)
    - crowd_mvp/simulation.py (Simulation class interface)
  </read_first>

  <action>
Create crowd_mvp/main.py. This file is the entry point: `python crowd_mvp/main.py`. Keep it thin — all logic lives in Simulation.

```python
# crowd_mvp/main.py
# Entry point for the Human Cymatics crowd monitoring simulator.
# Usage: python crowd_mvp/main.py
#
# Architecture (D-09):
#   main() creates Simulation and calls sim.update() + sim.draw() each frame.
#   No simulation logic lives here — only the Pygame event loop and clock.

import sys
import pygame

from crowd_mvp.config import FPS, N_PEOPLE, SIM_DURATION, SIGMA_ERROR, WINDOW_TITLE
from crowd_mvp.maps import SMALL_MAP
from crowd_mvp.simulation import Simulation


def main():
    pygame.init()

    map_w, map_h = SMALL_MAP['size']  # 600 × 400

    # Window: map area + small status bar at bottom (20px)
    STATUS_BAR_H = 20
    screen = pygame.display.set_mode((map_w, map_h + STATUS_BAR_H))
    pygame.display.set_caption(WINDOW_TITLE)

    clock = pygame.time.Clock()
    font_status = pygame.font.SysFont(None, 16)

    # Create simulation with defaults (SIM-06: 50 people, SNF-03: sigma=2.0)
    sim = Simulation(SMALL_MAP, n_people=N_PEOPLE, sigma=SIGMA_ERROR, duration=SIM_DURATION)

    # Map surface: simulation draws onto this sub-surface (keeps coordinate system clean)
    map_surface = screen.subsurface(pygame.Rect(0, 0, map_w, map_h))

    running = True
    while running:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # --- Update (LOOP-01: update every frame) ---
        # sim.update() is a no-op after is_complete (SIM-07)
        sim.update()

        # --- Draw (LOOP-01: render every frame) ---
        sim.draw(map_surface)

        # Status bar: FPS display
        fps_now = clock.get_fps()
        elapsed_frames = sim.frame_count
        elapsed_sec = elapsed_frames / FPS
        status = f"FPS: {fps_now:.0f}  |  Time: {elapsed_sec:.0f}/{SIM_DURATION}s  |  Agents: {N_PEOPLE}"
        status_surf = font_status.render(status, True, (80, 80, 80))
        # Fill status bar area
        screen.fill((200, 200, 200), pygame.Rect(0, map_h, map_w, STATUS_BAR_H))
        screen.blit(status_surf, (4, map_h + 3))

        pygame.display.flip()
        clock.tick(FPS)  # Cap at 60 FPS (LOOP-01)

    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()
```

Implementation notes:
- `screen.subsurface(...)` creates a sub-surface sharing the screen's pixel buffer. Simulation draws to map_surface, which directly updates the corresponding region of screen. This avoids an extra blit per frame and is the correct Pygame pattern for partitioned rendering.
- The status bar (20px) sits below the 600×400 map. Total window: 600×420.
- `clock.tick(FPS)` caps frame rate at 60. `clock.get_fps()` returns the smoothed actual FPS.
- ESC key quits for demo convenience.
  </action>

  <verify>
    <automated>python -c "
import sys; sys.path.insert(0, '.')
# Verify file exists and is syntactically valid Python
import ast, pathlib
src = pathlib.Path('crowd_mvp/main.py').read_text()
ast.parse(src)
# Verify key contents
assert 'def main():' in src
assert 'sim.update()' in src
assert 'sim.draw(map_surface)' in src
assert 'clock.tick(FPS)' in src
assert 'pygame.display.flip()' in src
assert 'Simulation(SMALL_MAP' in src
print('main.py syntax and structure OK')
"</automated>
  </verify>

  <acceptance_criteria>
    - crowd_mvp/main.py contains `def main():`
    - crowd_mvp/main.py contains `sim = Simulation(SMALL_MAP`
    - crowd_mvp/main.py contains `sim.update()`
    - crowd_mvp/main.py contains `sim.draw(map_surface)`
    - crowd_mvp/main.py contains `clock.tick(FPS)`
    - crowd_mvp/main.py contains `pygame.display.flip()`
    - crowd_mvp/main.py contains `if __name__ == '__main__':`
    - crowd_mvp/main.py contains `from crowd_mvp.simulation import Simulation`
    - crowd_mvp/main.py contains `from crowd_mvp.maps import SMALL_MAP`
    - `python -c "import ast, pathlib; ast.parse(pathlib.Path('crowd_mvp/main.py').read_text()); print('OK')"` exits 0
    - File has no import of crowd_mvb (typo) — only crowd_mvp
  </acceptance_criteria>

  <done>main.py is syntactically valid, imports correct modules, runs Pygame loop calling sim.update() + sim.draw() at 60 FPS</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Pygame event queue | Keyboard/window events are the only external input; only QUIT and K_ESCAPE are handled |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-01 | Denial of Service | pygame.event flood | accept | Single-process local app; event queue is rate-limited by OS; attacker must have local access |
| T-04-02 | Tampering | sys.exit(0) from ESC | accept | Intended behavior; local-only demo app |
</threat_model>

<verification>
After task completes:
- `python -c "import ast, pathlib; ast.parse(pathlib.Path('crowd_mvp/main.py').read_text())"` exits 0 (syntax check)
- crowd_mvp/ contains all 6 files: __init__.py, config.py, maps.py, people.py, sniffers.py, simulation.py, main.py plus viz/__init__.py and viz/heatmap.py
- `python crowd_mvp/main.py` opens a 600×420 Pygame window (manual verification in checkpoint)
</verification>

<success_criteria>
- main.py created and syntactically valid
- Entry point follows D-09 pattern exactly: thin loop, sim.update() + sim.draw() per frame
- Status bar shows FPS, elapsed time, agent count
- ESC key and window close both quit cleanly
</success_criteria>

<output>
After completion, create `.planning/phases/01-engine-core/01-04-SUMMARY.md` with:
- Window dimensions used
- Status bar contents
- Any adjustments made to main loop
- Any deviations from plan
</output>

</tasks>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
    The complete Phase 1 engine: config.py + maps.py + people.py + sniffers.py + simulation.py + main.py + viz/heatmap.py placeholder. Entry point is `python crowd_mvp/main.py`.
  </what-built>
  <how-to-verify>
    1. Open a terminal in the project root (Human-Cymatics/)
    2. Run: `python crowd_mvp/main.py`
    3. Confirm window opens showing a light grey floor plan with 4 darker zones and thin borders
    4. Confirm 5 small coloured squares (POI icons) are visible: green EN near left edge, red EX near right, amber BAR top-left area, purple STD top-right area, teal WC bottom-centre
    5. Confirm 50 blue dots appear near the entrance (left-centre) and begin spreading across the map
    6. Wait 5 seconds — confirm sniffer WiFi arc icons are visible at zone centres and their count numbers change
    7. Check the status bar at the bottom shows FPS near 60
    8. Let it run for 30 seconds — confirm agents keep moving and never disappear outside the window
    9. If you want to test auto-stop: temporarily edit config.py SIM_DURATION = 5, re-run, confirm "Simulation complete" overlay appears after 5 seconds
    10. Press ESC or close the window to quit

    Expected result at step 5-6: agents are visible as light blue circles (~4px radius), sniffer icons are WiFi-arc shapes at (150,100), (450,100), (150,300), (450,300), count labels below each icon.
    Expected FPS: >= 55 FPS (slight variation is normal).
  </how-to-verify>
  <resume-signal>Type "approved" if the window looks correct, or describe any visual issues (wrong colours, missing elements, freeze, errors)</resume-signal>
</task>

