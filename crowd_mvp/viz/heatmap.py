# crowd_mvp/viz/heatmap.py
# KDE bivariate heatmap rendered as a pygame.Surface.
# Phase 2: implements the stub from Phase 1.
#
# Pipeline:
#   1. gaussian_kde on sniffer positions weighted by estimated_count
#   2. Evaluate KDE on a downsampled grid (GRID_W x GRID_H)
#   3. Normalise to [0, 1], apply viridis colormap
#   4. Upscale to map_size via numpy repeat
#   5. Convert to pygame.Surface with SRCALPHA for blending
#
# NO plt.show() / plt.figure() — matplotlib used only for colormap lookup.

import numpy as np
import pygame
from matplotlib import colormaps


# Internal grid resolution. Lower = faster; 60x40 is plenty for sniffer-count KDE.
_GRID_W = 60
_GRID_H = 40

# Viridis colormap — looked up once at import time
_VIRIDIS = colormaps['viridis']


def build_heatmap_surface(sniffer_positions, sniffer_counts, map_size, sigma_kernel=20.0):
    """Build a pygame.Surface KDE heatmap from sniffer estimated counts.

    Args:
        sniffer_positions: list of (x, y) tuples in native map pixels
        sniffer_counts:    list of float estimated counts (same order as positions)
        map_size:          (width, height) of the target canvas in pixels
        sigma_kernel:      KDE bandwidth in native map pixels (D-12: live-updated)

    Returns:
        pygame.Surface with SRCALPHA flag, size == map_size.
        Deep blue when all counts are zero; yellow peaks at high-density zones.
    """
    map_w, map_h = map_size

    # Step 1 — Build density grid via gaussian_kde or fallback to zeros
    density = _compute_density(sniffer_positions, sniffer_counts, map_w, map_h, sigma_kernel)

    # Step 2 — Normalise to [0, 1]
    d_min, d_max = density.min(), density.max()
    if d_max > d_min:
        normed = (density - d_min) / (d_max - d_min)
    else:
        # All-zeros case (D-14): uniform minimum → deep blue
        normed = np.zeros_like(density)

    # Step 3 — Apply viridis: normed is (GRID_H, GRID_W) float → RGBA uint8
    rgba_small = (_VIRIDIS(normed) * 255).astype(np.uint8)  # (GRID_H, GRID_W, 4)

    # Step 4 — Upscale to map_size via numpy (no scipy/PIL dependency)
    scale_x = map_w // _GRID_W
    scale_y = map_h // _GRID_H
    # Use np.repeat for integer upscale; crop to exact map_size
    rgb_up = rgba_small[:, :, :3]                        # (GRID_H, GRID_W, 3)
    rgb_up = np.repeat(rgb_up, scale_y, axis=0)          # (GRID_H*scale_y, GRID_W, 3)
    rgb_up = np.repeat(rgb_up, scale_x, axis=1)          # (GRID_H*scale_y, GRID_W*scale_x, 3)
    # Crop/pad to exact map_size
    rgb_up = rgb_up[:map_h, :map_w, :]                   # (map_h, map_w, 3)

    # Step 5 — Convert to pygame Surface with alpha
    # pygame.surfarray.make_surface expects (W, H, 3) — transpose axes 0 and 1
    surf_rgb = np.ascontiguousarray(rgb_up.transpose(1, 0, 2))  # (map_w, map_h, 3)
    surface = pygame.surfarray.make_surface(surf_rgb)
    surface = surface.convert_alpha()
    surface.set_alpha(200)  # slight transparency so map geometry shows through (D-17)

    return surface


def _compute_density(sniffer_positions, sniffer_counts, map_w, map_h, sigma_kernel):
    """Evaluate gaussian_kde on a GRID_W x GRID_H grid.

    Returns:
        np.ndarray of shape (GRID_H, GRID_W) float64
    """
    # Grid of evaluation points in native map coordinates
    xs = np.linspace(0, map_w, _GRID_W)
    ys = np.linspace(0, map_h, _GRID_H)
    grid_x, grid_y = np.meshgrid(xs, ys)            # each (GRID_H, GRID_W)
    grid_pts = np.vstack([grid_x.ravel(), grid_y.ravel()])  # (2, GRID_H*GRID_W)

    # Weights: use counts; ensure at least 1 so KDE doesn't crash
    weights = np.array(sniffer_counts, dtype=np.float64)
    weights = np.maximum(weights, 0.0)
    total_weight = weights.sum()

    if total_weight < 1e-6 or len(sniffer_positions) < 2:
        # D-14: no data yet — return zeros (renders as flat deep blue)
        return np.zeros((_GRID_H, _GRID_W), dtype=np.float64)

    positions = np.array(sniffer_positions, dtype=np.float64).T  # (2, N_sniffers)

    # sigma_kernel is in native map pixels. Convert to KDE bandwidth factor:
    # gaussian_kde bw_method='silverman' uses N^(-1/6) * std as bandwidth.
    # To use a fixed pixel sigma, set bw_method = sigma_pixel / std(data).
    std_x = positions[0].std() if positions[0].std() > 1e-6 else 1.0
    std_y = positions[1].std() if positions[1].std() > 1e-6 else 1.0
    bw = sigma_kernel / max(std_x, std_y)

    try:
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(positions, bw_method=bw, weights=weights)
        density = kde(grid_pts).reshape(_GRID_H, _GRID_W)
    except Exception:
        # Fallback: zero grid (D-14 graceful degradation)
        density = np.zeros((_GRID_H, _GRID_W), dtype=np.float64)

    return density
