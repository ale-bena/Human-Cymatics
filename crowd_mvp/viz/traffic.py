# crowd_mvp/viz/traffic.py
# Tab 3: traffic matrix heatmap (left) + density-trace trajectory (right).
#
# Left panel  — NxN plasma colormap matrix: matrix[i][j] = transitions zone i -> zone j.
# Right panel — Dark map underlay + accumulated trajectory segments for tracked agents.
#               Segments drawn with low alpha to a persistent offscreen Surface so
#               overlapping paths brighten — "long-exposure light-painting" effect (D-08).
#
# NO plt.show() — matplotlib used only for colormap lookup.

import pygame
import numpy as np
from matplotlib import colormaps

_PLASMA  = colormaps['plasma']
_VIRIDIS = colormaps['viridis']

# Cell size in pixels for the matrix grid (left panel)
_CELL = 40
# Alpha per trajectory segment (low = subtle accumulation; 12/255 ≈ 5%)
_SEG_ALPHA = 12
# Background colour for trajectory surface (very dark navy)
_TRAJ_BG = (8, 8, 20)


def build_traffic_panels(
    left_surf,
    right_surf,
    map_def,
    traffic_matrix,
    tracked_agents,
    canvas_w,
    canvas_h,
    font_label,
):
    """Render the Tab 3 dual panels.

    Args:
        left_surf:       pygame.Surface — screen subsurface for left panel
        right_surf:      pygame.Surface — screen subsurface for right panel
        map_def:         map definition dict with 'zones' list and 'size' tuple
        traffic_matrix:  dict[zone_id -> dict[zone_id -> int]] accumulated transitions
        tracked_agents:  list of Agent — each has .pos_history list of (x,y) tuples
        canvas_w/h:      int — panel pixel dimensions
        font_label:      pygame.font.Font for axis labels
    """
    # Left panel: NxN matrix heatmap
    _draw_matrix_panel(left_surf, traffic_matrix, map_def, canvas_w, canvas_h, font_label)
    # Right panel: trajectory density trace
    _draw_trajectory_panel(right_surf, map_def, tracked_agents, canvas_w, canvas_h)


def _draw_matrix_panel(surface, traffic_matrix, map_def, canvas_w, canvas_h, font):
    """Draw the NxN plasma-colormap matrix on surface (D-06)."""
    zone_ids = [z['id'] for z in map_def['zones']]
    n = len(zone_ids)
    if n == 0:
        surface.fill((20, 20, 30))
        return

    # Build numpy matrix
    mat = np.array(
        [[traffic_matrix.get(zi, {}).get(zj, 0) for zj in zone_ids] for zi in zone_ids],
        dtype=np.float64,
    )

    # Normalise to [0, 1]
    mat_max = mat.max()
    normed = mat / mat_max if mat_max > 0 else mat

    # Determine cell size to fit in canvas
    # Leave margin: 20px left (row labels) + 20px top (col labels)
    margin = 20
    available = min(canvas_w - margin, canvas_h - margin)
    cell = max(4, available // n)
    grid_size = cell * n

    surface.fill((15, 15, 25))

    # Draw matrix cells
    for i, zi in enumerate(zone_ids):
        for j, zj in enumerate(zone_ids):
            val = normed[i, j]
            r, g, b, _ = _PLASMA(val)
            col = (int(r * 255), int(g * 255), int(b * 255))
            rect = pygame.Rect(margin + j * cell, margin + i * cell, cell - 1, cell - 1)
            pygame.draw.rect(surface, col, rect)

    # Row labels (zone i = from)
    for i, zi in enumerate(zone_ids):
        lbl = font.render(zi, True, (180, 180, 200))
        cy = margin + i * cell + cell // 2 - lbl.get_height() // 2
        surface.blit(lbl, (margin - lbl.get_width() - 2, cy))

    # Column labels (zone j = to) — drawn at top, rotated or abbreviated
    for j, zj in enumerate(zone_ids):
        lbl = font.render(zj, True, (180, 180, 200))
        cx = margin + j * cell + cell // 2 - lbl.get_width() // 2
        surface.blit(lbl, (cx, margin - lbl.get_height() - 2))

    # Title
    title = font.render("Traffic Matrix (zone transitions)", True, (200, 200, 220))
    surface.blit(title, (canvas_w // 2 - title.get_width() // 2, canvas_h - 18))


def _draw_trajectory_panel(surface, map_def, tracked_agents, canvas_w, canvas_h):
    """Draw trajectory density-trace on surface (D-07, D-08).

    Technique: accumulate all segments onto a persistent dark SRCALPHA surface
    with low per-segment alpha. Overlapping paths sum to brighter values.
    Then apply plasma colormap by extracting the brightness channel.
    """
    map_w, map_h = map_def['size']
    scale = min(canvas_w / map_w, canvas_h / map_h)
    ox = int((canvas_w - map_w * scale) / 2)
    oy = int((canvas_h - map_h * scale) / 2)

    # Dark background
    surface.fill(_TRAJ_BG)

    # Draw map zone outlines as subtle reference geometry
    for zone in map_def.get('zones', []):
        zx, zy, zw, zh = zone['rect']
        r = pygame.Rect(int(zx * scale) + ox, int(zy * scale) + oy,
                        max(1, int(zw * scale)), max(1, int(zh * scale)))
        pygame.draw.rect(surface, (25, 25, 40), r, 1)

    # Build an accumulation surface (greyscale brightness via alpha=0 base)
    acc_surf = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    acc_surf.fill((0, 0, 0, 0))

    # Draw each agent's trajectory segments with low alpha
    for agent in tracked_agents:
        history = agent.pos_history
        if len(history) < 2:
            continue
        for k in range(len(history) - 1):
            x0, y0 = history[k]
            x1, y1 = history[k + 1]
            sx0 = int(x0 * scale) + ox
            sy0 = int(y0 * scale) + oy
            sx1 = int(x1 * scale) + ox
            sy1 = int(y1 * scale) + oy
            pygame.draw.line(acc_surf, (255, 200, 80, _SEG_ALPHA), (sx0, sy0), (sx1, sy1), 1)

    # Blit accumulation surface onto the dark background
    # This creates the additive brightness effect (D-08)
    surface.blit(acc_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Panel label
    lbl_font = pygame.font.SysFont(None, 15)
    lbl = lbl_font.render(f"Trajectories ({len(tracked_agents)} agents, cumulative)", True, (140, 140, 180))
    surface.blit(lbl, (canvas_w // 2 - lbl.get_width() // 2, canvas_h - 18))
