# crowd_mvp/viz/compare.py
# Tab 2: dual-panel zone-fill comparison heatmap.
# Left panel  = real zone densities (ground truth from sniffer.real_count).
# Right panel = sniffer estimated counts (sniffer.estimated_count).
# Both panels use viridis on a shared normalisation scale so colour differences
# are immediately visible when sigma_error is high (D-01, D-02, D-03).
#
# Pipeline:
#   1. Compute shared max from combined real + estimated counts.
#   2. For each zone: look up viridis colour at normalised count / max.
#   3. Fill zone rect with that colour; draw zone border.
#   4. Draw text label at zone centre: "[N]" left, "[~N]" right.
#   5. On left panel only: draw agent dots.
#
# NO plt.show() — matplotlib used only for colormap lookup.

import pygame
import numpy as np
from matplotlib import colormaps

_VIRIDIS = colormaps['viridis']

# Minimum normalisation max so single-count zones show some colour (not 0/0)
_NORM_FLOOR = 1


def build_compare_panels(
    left_surf,
    right_surf,
    map_def,
    real_counts,
    estimated_counts,
    agents,
    canvas_w,
    canvas_h,
    font_label,
):
    """Render the Tab 2 dual panels directly onto left_surf and right_surf.

    Args:
        left_surf:         pygame.Surface — screen subsurface for left panel (CANVAS_W x CANVAS_H)
        right_surf:        pygame.Surface — screen subsurface for right panel
        map_def:           map definition dict with 'zones' list, 'size' tuple
        real_counts:       dict[zone_id -> int] — ground truth counts
        estimated_counts:  dict[zone_id -> int] — noisy sniffer estimates
        agents:            list of Agent instances (drawn on left panel only)
        canvas_w, canvas_h: int — panel dimensions in pixels
        font_label:        pygame.font.Font — for zone count labels
    """
    map_w, map_h = map_def['size']
    scale = min(canvas_w / map_w, canvas_h / map_h)
    offset_x = int((canvas_w - map_w * scale) / 2)
    offset_y = int((canvas_h - map_h * scale) / 2)

    # Shared normalisation: max across real + estimated combined (D-02)
    all_counts = list(real_counts.values()) + list(estimated_counts.values())
    norm_max = max(max(all_counts) if all_counts else 0, _NORM_FLOOR)

    # Background
    left_surf.fill((30, 30, 40))
    right_surf.fill((30, 30, 40))

    for zone in map_def['zones']:
        zid = zone['id']
        zx, zy, zw, zh = zone['rect']

        # Scale zone rect to canvas
        sx = int(zx * scale) + offset_x
        sy = int(zy * scale) + offset_y
        sw = max(1, int(zw * scale))
        sh = max(1, int(zh * scale))
        scaled_rect = pygame.Rect(sx, sy, sw, sh)

        # Zone centre (for labels)
        cx = sx + sw // 2
        cy = sy + sh // 2

        # Real count colour (left)
        real_val = real_counts.get(zid, 0)
        real_norm = float(real_val) / norm_max
        real_col = _viridis_colour(real_norm)
        pygame.draw.rect(left_surf, real_col, scaled_rect)
        pygame.draw.rect(left_surf, (80, 80, 100), scaled_rect, 1)

        # Estimated count colour (right)
        est_val = estimated_counts.get(zid, 0)
        est_norm = float(est_val) / norm_max
        est_col = _viridis_colour(est_norm)
        pygame.draw.rect(right_surf, est_col, scaled_rect)
        pygame.draw.rect(right_surf, (80, 80, 100), scaled_rect, 1)

        # Zone labels (D-03)
        _draw_zone_label(left_surf, font_label, f"[{real_val}]", cx, cy, real_col)
        _draw_zone_label(right_surf, font_label, f"[~{est_val}]", cx, cy, est_col)

    # Agent dots on left panel only (D-03)
    for agent in agents:
        ax = int(agent.x * scale) + offset_x
        ay = int(agent.y * scale) + offset_y
        pygame.draw.circle(left_surf, (200, 230, 255), (ax, ay), max(2, int(2 * scale)))


def _viridis_colour(norm):
    """Map [0,1] float to an RGB tuple via viridis."""
    norm = max(0.0, min(1.0, norm))
    r, g, b, _ = _VIRIDIS(norm)
    return (int(r * 255), int(g * 255), int(b * 255))


def _draw_zone_label(surface, font, text, cx, cy, zone_col):
    """Draw a count label at zone centre. Colour chosen for contrast against zone fill."""
    # Use white on dark zones (norm < 0.5) and dark on bright zones
    # Estimate zone luminance from RGB
    r, g, b = zone_col
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    text_col = (240, 240, 240) if lum < 140 else (20, 20, 20)
    surf = font.render(text, True, text_col)
    surface.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))
