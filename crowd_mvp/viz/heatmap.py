# crowd_mvp/viz/heatmap.py
# Phase 2 placeholder — KDE bivariate heatmap rendered via NumPy -> Pygame Surface.
# NOT imported in Phase 1. Added here as a structural placeholder.
#
# Phase 2 implementation notes:
#   - Use scipy.stats.gaussian_kde on sniffer estimated_count-weighted positions
#   - Render to numpy array using viridis/hot colormap from matplotlib.cm
#   - Convert array to pygame.Surface with pygame.surfarray.make_surface
#   - Alpha-blend over map surface using Surface.blit with BLEND_RGBA_MULT
#   - Do NOT call plt.show() or embed matplotlib figure in the game loop


def build_heatmap_surface(sniffer_positions, sniffer_counts, map_size, sigma_kernel=20.0):
    """
    Phase 2: Build a pygame.Surface heatmap from sniffer data.

    Args:
        sniffer_positions: list of (x, y) tuples
        sniffer_counts:    list of float estimated counts (weights)
        map_size:          (width, height) tuple
        sigma_kernel:      KDE bandwidth in pixels

    Returns:
        pygame.Surface with RGBA heatmap, same size as map_size
    """
    raise NotImplementedError("Phase 2 — not implemented in Phase 1")
