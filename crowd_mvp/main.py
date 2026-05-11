# crowd_mvp/main.py
# Phase 2: Full interactive interface.
# Window: 1200x520 — dual panels + tab bar + control panel + status bar.
# Usage: python crowd_mvp/main.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from crowd_mvp.config import (
    FPS, SIM_DURATION, WINDOW_TITLE,
    WINDOW_W, WINDOW_H, CANVAS_W, CANVAS_H,
    TAB_BAR_H, CONTROL_PANEL_H, STATUS_BAR_H,
    N_PEOPLE_MIN, N_PEOPLE_MAX, N_PEOPLE_DEFAULT,
    SIGMA_ERROR, SIGMA_ERROR_MIN, SIGMA_ERROR_MAX,
    SIGMA_KERNEL_DEFAULT, SIGMA_KERNEL_MIN, SIGMA_KERNEL_MAX,
    COLOUR_BG, COLOUR_LABEL, COLOUR_TEXT,
    COLOUR_TAB_ACTIVE, COLOUR_TAB_INACTIVE,
    COLOUR_BTN_ACTIVE, COLOUR_BTN_INACTIVE,
    COLOUR_CONTROL_BG, COLOUR_SLIDER_TRACK, COLOUR_SLIDER_THUMB,
)
from crowd_mvp.maps import SMALL_MAP, MEDIUM_MAP, LARGE_MAP, ALL_MAPS
from crowd_mvp.simulation import Simulation
from crowd_mvp.viz.heatmap import build_heatmap_surface, compute_density_grid
from crowd_mvp.viz.compare import build_compare_panels
from crowd_mvp.viz.traffic import build_traffic_panels
from crowd_mvp.viz.surface3d import build_3d_surface_pygame


# ---------------------------------------------------------------------------
# Layout constants (absolute pixel positions in the 1200x520 window)
# ---------------------------------------------------------------------------
LEFT_PANEL_RECT  = pygame.Rect(0,      0,      CANVAS_W, CANVAS_H)
RIGHT_PANEL_RECT = pygame.Rect(CANVAS_W, 0,    CANVAS_W, CANVAS_H)
TAB_BAR_RECT     = pygame.Rect(0,      CANVAS_H, WINDOW_W, TAB_BAR_H)
CTRL_RECT        = pygame.Rect(0,      CANVAS_H + TAB_BAR_H, WINDOW_W, CONTROL_PANEL_H)
STATUS_RECT      = pygame.Rect(0,      CANVAS_H + TAB_BAR_H + CONTROL_PANEL_H, WINDOW_W, STATUS_BAR_H)


# ---------------------------------------------------------------------------
# Simple UI helpers
# ---------------------------------------------------------------------------

def draw_button(surface, font, rect, label, active, active_col, inactive_col):
    """Draw a labelled toggle button. Returns rect for hit testing."""
    colour = active_col if active else inactive_col
    pygame.draw.rect(surface, colour, rect, border_radius=3)
    pygame.draw.rect(surface, (80, 80, 80), rect, 1, border_radius=3)
    txt = font.render(label, True, (255, 255, 255) if active else (40, 40, 40))
    surface.blit(txt, (rect.centerx - txt.get_width() // 2,
                       rect.centery - txt.get_height() // 2))
    return rect


def draw_slider(surface, font, label, rect, value, vmin, vmax, dragging=False):
    """Draw a horizontal slider with label+value text above the track.

    Args:
        rect: pygame.Rect for the full slider widget (track + label area).
              Track occupies the bottom 8px; label row is above.
        value: current float value
        vmin, vmax: slider range

    Returns:
        thumb_rect: pygame.Rect of the thumb (for hit testing)
    """
    # Label + value text
    label_surf = font.render(f"{label}: {value:.1f}", True, COLOUR_LABEL)
    surface.blit(label_surf, (rect.x, rect.y))

    # Track
    track_y = rect.bottom - 8
    track_rect = pygame.Rect(rect.x, track_y, rect.width, 6)
    pygame.draw.rect(surface, COLOUR_SLIDER_TRACK, track_rect, border_radius=3)

    # Thumb position
    frac = (value - vmin) / (vmax - vmin) if vmax > vmin else 0.0
    thumb_x = int(rect.x + frac * rect.width)
    thumb_rect = pygame.Rect(thumb_x - 5, track_y - 3, 10, 12)
    col = COLOUR_TAB_ACTIVE if dragging else COLOUR_SLIDER_THUMB
    pygame.draw.rect(surface, col, thumb_rect, border_radius=3)

    return thumb_rect


def slider_value_from_x(mx, rect, vmin, vmax):
    """Convert mouse x to slider value, clamped to [vmin, vmax]."""
    frac = (mx - rect.x) / rect.width
    frac = max(0.0, min(1.0, frac))
    return vmin + frac * (vmax - vmin)


# ---------------------------------------------------------------------------
# End-of-simulation overlay helper (D-13)
# ---------------------------------------------------------------------------

def _draw_end_overlay(screen, font, canvas_w, canvas_h):
    """Semi-transparent overlay over the dual-panel area (left + right) at sim end (D-13).

    The overlay covers x=0..WINDOW_W, y=0..CANVAS_H (both panels only).
    Uses SRCALPHA so the last data frame remains visible beneath the dim.
    Message centred on the full dual-panel area.
    """
    from crowd_mvp.config import WINDOW_W, COLOUR_OVERLAY_BG
    overlay = pygame.Surface((WINDOW_W, canvas_h), pygame.SRCALPHA)
    # COLOUR_OVERLAY_BG is (20, 20, 20, 180) — semi-transparent dark
    overlay.fill(COLOUR_OVERLAY_BG)
    screen.blit(overlay, (0, 0))

    # Centred message
    msg_font = pygame.font.SysFont(None, 28)
    line1 = msg_font.render("Simulation complete", True, (240, 240, 240))
    line2 = msg_font.render("press Reset to restart", True, (180, 200, 180))
    total_h = line1.get_height() + 6 + line2.get_height()
    cx = WINDOW_W // 2
    cy = canvas_h // 2
    screen.blit(line1, (cx - line1.get_width() // 2, cy - total_h // 2))
    screen.blit(line2, (cx - line2.get_width() // 2, cy - total_h // 2 + line1.get_height() + 6))


# ---------------------------------------------------------------------------
# Scale transform helper (D-05)
# ---------------------------------------------------------------------------

def scale_factor(map_size):
    """Return (sx, sy, offset_x, offset_y) to centre-fit map in CANVAS_W x CANVAS_H."""
    mw, mh = map_size
    sx = CANVAS_W / mw
    sy = CANVAS_H / mh
    s = min(sx, sy)
    ox = (CANVAS_W - mw * s) / 2
    oy = (CANVAS_H - mh * s) / 2
    return s, s, int(ox), int(oy)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.SCALED)
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    font_ui   = pygame.font.SysFont(None, 16)
    font_tab  = pygame.font.SysFont(None, 17)
    font_status = pygame.font.SysFont(None, 15)

    # --- Staged settings (D-10: apply on Reset) ---
    staged_map_key  = 'S'          # 'S' | 'M' | 'L'
    staged_behavior = 'wanderer'   # 'wanderer' | 'goal' | 'social'
    staged_n_people = N_PEOPLE_DEFAULT

    # Live settings (D-12: apply immediately on drag)
    live_sigma_error  = SIGMA_ERROR
    live_sigma_kernel = SIGMA_KERNEL_DEFAULT

    active_tab = 1  # 1, 2, or 3 (D-04)

    # --- Build initial simulation ---
    def build_sim():
        return Simulation(
            ALL_MAPS[staged_map_key],
            n_people=staged_n_people,
            sigma=live_sigma_error,
            duration=SIM_DURATION,
            behavior=staged_behavior,
        )

    sim = build_sim()

    # Heatmap surface — updated every sniffer tick (D-15)
    heatmap_surface = None

    # Tab 3 traffic panels cache — rebuilt every sniffer tick, blitted each frame (D-08 perf fix)
    traffic_panels_cache = None   # tuple (left_surf, right_surf) rebuilt on sniffer tick

    # Tab 2 compare state — updated every sniffer tick (D-04)
    compare_real_counts = {}
    compare_est_counts  = {}

    # Tab 4 — 3D surface density accumulator
    density_acc   = None   # np.ndarray (GRID_H, GRID_W) running sum
    density_ticks = 0      # number of ticks accumulated
    tab4_live_surf = None  # pygame.Surface — current-tick density
    tab4_avg_surf  = None  # pygame.Surface — session average density
    _sim_was_complete = False  # used to detect completion transition

    # Playback state (D-09: auto-starts running)
    paused = False

    # --- Slider drag state ---
    dragging = None   # None | 'n_people' | 'sigma_error' | 'sigma_kernel'

    # --- Define UI element rects (absolute window coords) ---
    # Control panel row: y range CANVAS_H + TAB_BAR_H to CANVAS_H + TAB_BAR_H + CONTROL_PANEL_H
    cp_top = CANVAS_H + TAB_BAR_H   # absolute y of control panel top
    cp_mid = cp_top + CONTROL_PANEL_H // 2

    # Map buttons [S][M][L] — left group
    map_btn_rects = {
        'S': pygame.Rect(10,  cp_top + 8, 28, 22),
        'M': pygame.Rect(42,  cp_top + 8, 28, 22),
        'L': pygame.Rect(74,  cp_top + 8, 28, 22),
    }
    map_label_rect = pygame.Rect(10, cp_top + 2, 60, 12)

    # Behavior buttons [W][G][C]
    beh_btn_rects = {
        'wanderer': pygame.Rect(122, cp_top + 8, 28, 22),
        'goal':     pygame.Rect(154, cp_top + 8, 28, 22),
        'social':   pygame.Rect(186, cp_top + 8, 28, 22),
    }

    # Sliders — horizontal layout in remaining 1200 - 220 - 80 = 900px, split 3 ways
    SL_W = 240   # slider widget width
    SL_H = 35    # widget height (label row + track row)
    sl_n_people    = pygame.Rect(230, cp_top + 20, SL_W, SL_H)
    sl_sigma_error = pygame.Rect(490, cp_top + 20, SL_W, SL_H)
    sl_sigma_kernel= pygame.Rect(750, cp_top + 20, SL_W, SL_H)

    # Pause/Resume and Reset buttons (D-11: Pause left of Reset, same row)
    pause_rect  = pygame.Rect(1002, cp_top + 16, 70, 26)
    reset_rect  = pygame.Rect(1080, cp_top + 16, 70, 26)

    running = True
    while running:
        # ----------------------------------------------------------------
        # Event handling
        # ----------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11 or (
                        event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT):
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_1:
                    active_tab = 1
                elif event.key == pygame.K_2:
                    active_tab = 2
                elif event.key == pygame.K_3:
                    active_tab = 3
                elif event.key == pygame.K_4:
                    active_tab = 4

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Tab buttons
                tab_w = WINDOW_W // 4
                if TAB_BAR_RECT.collidepoint(mx, my):
                    col = mx // tab_w
                    active_tab = min(col + 1, 4)

                # Map selector (D-10: staged)
                for key, rect in map_btn_rects.items():
                    if rect.collidepoint(mx, my):
                        staged_map_key = key

                # Behavior selector (D-09: staged — takes effect on Reset)
                for beh, rect in beh_btn_rects.items():
                    if rect.collidepoint(mx, my):
                        staged_behavior = beh

                # Reset button (D-11)
                if reset_rect.collidepoint(mx, my):
                    sim = build_sim()
                    heatmap_surface = None
                    traffic_panels_cache = None
                    compare_real_counts = {}
                    compare_est_counts  = {}
                    density_acc   = None
                    density_ticks = 0
                    tab4_live_surf = None
                    tab4_avg_surf  = None
                    _sim_was_complete = False
                    paused = False

                # Pause / Resume button (D-09, D-10, D-11)
                if pause_rect.collidepoint(mx, my):
                    if not sim.is_complete:
                        paused = not paused

                # Slider click-to-set + begin drag
                if sl_n_people.collidepoint(mx, my):
                    staged_n_people = int(round(
                        slider_value_from_x(mx, sl_n_people, N_PEOPLE_MIN, N_PEOPLE_MAX)
                    ))
                    dragging = 'n_people'
                elif sl_sigma_error.collidepoint(mx, my):
                    live_sigma_error = slider_value_from_x(
                        mx, sl_sigma_error, SIGMA_ERROR_MIN, SIGMA_ERROR_MAX
                    )
                    # D-12: live update
                    for s in sim.sniffers:
                        s.sigma = live_sigma_error
                    dragging = 'sigma_error'
                elif sl_sigma_kernel.collidepoint(mx, my):
                    live_sigma_kernel = slider_value_from_x(
                        mx, sl_sigma_kernel, SIGMA_KERNEL_MIN, SIGMA_KERNEL_MAX
                    )
                    dragging = 'sigma_kernel'

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = None

            elif event.type == pygame.MOUSEMOTION and dragging:
                mx, my = event.pos
                if dragging == 'n_people':
                    staged_n_people = int(round(
                        slider_value_from_x(mx, sl_n_people, N_PEOPLE_MIN, N_PEOPLE_MAX)
                    ))
                elif dragging == 'sigma_error':
                    live_sigma_error = slider_value_from_x(
                        mx, sl_sigma_error, SIGMA_ERROR_MIN, SIGMA_ERROR_MAX
                    )
                    # D-12: apply immediately
                    for s in sim.sniffers:
                        s.sigma = live_sigma_error
                elif dragging == 'sigma_kernel':
                    live_sigma_kernel = slider_value_from_x(
                        mx, sl_sigma_kernel, SIGMA_KERNEL_MIN, SIGMA_KERNEL_MAX
                    )

        # ----------------------------------------------------------------
        # Simulation update (every frame)
        # ----------------------------------------------------------------
        if not paused:
            sim.update()

        # Heatmap rebuild every sniffer tick — skip while paused (D-10)
        if not paused and sim.frame_count % 60 == 0:
            # Use actual agent positions as KDE input so the heatmap shows real
            # crowd density: flow corridors between POIs, central zones with high
            # footfall, and any natural clustering — not just fixed sniffer blobs.
            # Uniform weights (1.0 per agent) let density emerge from position alone.
            agent_positions = [(a.x, a.y) for a in sim.agents]
            agent_weights = [1.0] * len(agent_positions)
            raw_heatmap = build_heatmap_surface(
                agent_positions, agent_weights, sim.map_size, sigma_kernel=live_sigma_kernel
            )
            heatmap_surface = pygame.transform.scale(raw_heatmap, (CANVAS_W, CANVAS_H))

            # Update Tab 2 data on same sniffer tick cadence (D-04)
            compare_real_counts, compare_est_counts = sim.get_zone_counts()

            # Cache Tab 3 panels — rebuild every tick, not every frame (D-08 performance fix)
            traffic_left  = pygame.Surface((CANVAS_W, CANVAS_H))
            traffic_right = pygame.Surface((CANVAS_W, CANVAS_H))
            build_traffic_panels(
                traffic_left, traffic_right,
                sim.map_def, sim.traffic_matrix, sim.tracked_agents,
                CANVAS_W, CANVAS_H, font_ui,
            )
            traffic_panels_cache = (traffic_left, traffic_right)

            # Tab 4 — accumulate density grid and rebuild 3D surfaces
            grid = compute_density_grid(
                agent_positions, agent_weights, sim.map_size, live_sigma_kernel
            )
            if density_acc is None:
                density_acc = grid.copy()
            else:
                density_acc += grid
            density_ticks += 1

            if active_tab == 4:
                tab4_live_surf = build_3d_surface_pygame(
                    grid, CANVAS_W, CANVAS_H, title="Live Density"
                )
                avg_grid = density_acc / density_ticks
                tab4_avg_surf = build_3d_surface_pygame(
                    avg_grid, CANVAS_W, CANVAS_H, title="Session Average"
                )

        # Detect simulation completion — auto-switch to Tab 4 for the summary view
        if sim.is_complete and not _sim_was_complete:
            _sim_was_complete = True
            active_tab = 4
            if density_acc is not None and density_ticks > 0:
                agent_positions = [(a.x, a.y) for a in sim.agents]
                agent_weights = [1.0] * len(agent_positions)
                grid = compute_density_grid(
                    agent_positions, agent_weights, sim.map_size, live_sigma_kernel
                )
                tab4_live_surf = build_3d_surface_pygame(
                    grid, CANVAS_W, CANVAS_H, title="Final Snapshot"
                )
                avg_grid = density_acc / density_ticks
                tab4_avg_surf = build_3d_surface_pygame(
                    avg_grid, CANVAS_W, CANVAS_H, title="Session Average"
                )

        # ----------------------------------------------------------------
        # Draw
        # ----------------------------------------------------------------
        screen.fill(COLOUR_BG)

        # --- Left panel: simulation scaled to fit canvas (D-05) ---
        left_surf = screen.subsurface(LEFT_PANEL_RECT)
        sim.draw_scaled(left_surf, CANVAS_W, CANVAS_H)

        # --- Right panel: map underlay + KDE heatmap (D-17) ---
        right_surf = screen.subsurface(RIGHT_PANEL_RECT)
        if active_tab == 1:
            # Layer 1: plain map (zones + POI only, no agents/sniffers)
            sim.draw_map_scaled(right_surf, CANVAS_W, CANVAS_H)

            # Layer 2: heatmap at 70% opacity blended over the map
            HEATMAP_ALPHA = 178  # 70% of 255
            if heatmap_surface is not None:
                heatmap_surface.set_alpha(HEATMAP_ALPHA)
                right_surf.blit(heatmap_surface, (0, 0))
            else:
                # D-14: initial state — flat deep blue before first tick
                mw, mh = sim.map_size
                init_raw = build_heatmap_surface(
                    [(mw // 2, mh // 2)], [0.0], sim.map_size, sigma_kernel=live_sigma_kernel
                )
                init_surf = pygame.transform.scale(init_raw, (CANVAS_W, CANVAS_H))
                init_surf.set_alpha(HEATMAP_ALPHA)
                right_surf.blit(init_surf, (0, 0))
        else:
            right_surf.fill(COLOUR_BG)

        # Tab 2/3 content
        if active_tab == 2:
            build_compare_panels(
                left_surf, right_surf,
                sim.map_def,
                compare_real_counts,
                compare_est_counts,
                sim.agents,
                CANVAS_W, CANVAS_H,
                font_ui,
            )
            # Panel column headers (drawn after panels so they appear on top)
            hdr_font = font_tab
            hdr_real = hdr_font.render("Ground Truth", True, (220, 220, 220))
            hdr_est  = hdr_font.render("WiFi Estimate", True, (220, 220, 220))
            left_surf.blit(hdr_real, (CANVAS_W // 2 - hdr_real.get_width() // 2, 4))
            right_surf.blit(hdr_est,  (CANVAS_W // 2 - hdr_est.get_width()  // 2, 4))
        elif active_tab == 3:
            if traffic_panels_cache is not None:
                left_surf.blit(traffic_panels_cache[0], (0, 0))
                right_surf.blit(traffic_panels_cache[1], (0, 0))
            else:
                left_surf.fill((20, 20, 30))
                right_surf.fill((20, 20, 30))
        elif active_tab == 4:
            left_surf.fill((18, 18, 42))
            right_surf.fill((18, 18, 42))
            if tab4_live_surf is not None:
                left_surf.blit(tab4_live_surf, (0, 0))
            else:
                msg = font_tab.render("Waiting for data…", True, (120, 120, 180))
                left_surf.blit(msg, (CANVAS_W // 2 - msg.get_width() // 2,
                                     CANVAS_H // 2 - msg.get_height() // 2))
            if tab4_avg_surf is not None:
                right_surf.blit(tab4_avg_surf, (0, 0))
            else:
                msg = font_tab.render("Waiting for data…", True, (120, 120, 180))
                right_surf.blit(msg, (CANVAS_W // 2 - msg.get_width() // 2,
                                      CANVAS_H // 2 - msg.get_height() // 2))

        # End-of-simulation overlay over both panels — suppressed on Tab 4 (summary is the overlay)
        if sim.is_complete and active_tab != 4:
            _draw_end_overlay(screen, font_tab, CANVAS_W, CANVAS_H)

        # --- Tab bar (D-04) ---
        pygame.draw.rect(screen, (200, 200, 200), TAB_BAR_RECT)
        tab_labels = ['Heatmap', 'Compare', 'Traffic', '3D Surface']
        tab_w = WINDOW_W // 4
        for i, label in enumerate(tab_labels):
            is_active = (active_tab == i + 1)
            tab_rect = pygame.Rect(i * tab_w, CANVAS_H, tab_w, TAB_BAR_H)
            pygame.draw.rect(screen, COLOUR_TAB_ACTIVE if is_active else COLOUR_TAB_INACTIVE, tab_rect)
            pygame.draw.rect(screen, (120, 120, 120), tab_rect, 1)
            txt = font_tab.render(label, True, (255, 255, 255) if is_active else (240, 240, 240))
            screen.blit(txt, (tab_rect.centerx - txt.get_width() // 2,
                              tab_rect.centery - txt.get_height() // 2))

        # --- Control panel (D-03) ---
        pygame.draw.rect(screen, COLOUR_CONTROL_BG, CTRL_RECT)
        pygame.draw.line(screen, (160, 160, 160), (0, cp_top), (WINDOW_W, cp_top), 1)

        # Map label
        ml = font_ui.render("Map:", True, COLOUR_LABEL)
        screen.blit(ml, (10, cp_top + 2))

        # Map buttons
        for key, rect in map_btn_rects.items():
            draw_button(screen, font_ui, rect, key, staged_map_key == key,
                        COLOUR_BTN_ACTIVE, COLOUR_BTN_INACTIVE)

        # Behavior label
        bl = font_ui.render("Behavior:", True, COLOUR_LABEL)
        screen.blit(bl, (118, cp_top + 2))

        # Behavior buttons
        beh_labels = {'wanderer': 'W', 'goal': 'G', 'social': 'C'}
        for beh, rect in beh_btn_rects.items():
            draw_button(screen, font_ui, rect, beh_labels[beh], staged_behavior == beh,
                        COLOUR_BTN_ACTIVE, COLOUR_BTN_INACTIVE)

        # Sliders
        draw_slider(screen, font_ui, "n_people", sl_n_people,
                    staged_n_people, N_PEOPLE_MIN, N_PEOPLE_MAX,
                    dragging == 'n_people')
        draw_slider(screen, font_ui, "sigma_err", sl_sigma_error,
                    live_sigma_error, SIGMA_ERROR_MIN, SIGMA_ERROR_MAX,
                    dragging == 'sigma_error')
        draw_slider(screen, font_ui, "sigma_kern", sl_sigma_kernel,
                    live_sigma_kernel, SIGMA_KERNEL_MIN, SIGMA_KERNEL_MAX,
                    dragging == 'sigma_kernel')

        # Reset button
        draw_button(screen, font_ui, reset_rect, "Reset", False,
                    (200, 80, 60), (200, 80, 60))

        # Pause / Resume button (D-11: left of Reset, same row)
        pause_label = "Resume" if paused else "Pause"
        pause_active_col = (200, 140, 40)   # amber when paused (visual cue)
        pause_inactive_col = (60, 120, 200)  # blue when running
        draw_button(screen, font_ui, pause_rect, pause_label,
                    paused, pause_active_col, pause_inactive_col)

        # --- Status bar ---
        pygame.draw.rect(screen, (190, 190, 190), STATUS_RECT)
        fps_now = clock.get_fps()
        elapsed = sim.frame_count / FPS
        n_actual = len(sim.agents)
        status_txt = (
            f"FPS: {fps_now:.0f}  |  Time: {elapsed:.0f}/{SIM_DURATION}s  "
            f"|  Map: {staged_map_key}  |  Behavior: {staged_behavior}  "
            f"|  Agents: {n_actual}  |  Tab: {active_tab}"
        )
        st_surf = font_status.render(status_txt, True, (60, 60, 60))
        screen.blit(st_surf, (4, STATUS_RECT.y + 3))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()
