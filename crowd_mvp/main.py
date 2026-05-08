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

    map_w, map_h = SMALL_MAP['size']  # 600 x 400

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
