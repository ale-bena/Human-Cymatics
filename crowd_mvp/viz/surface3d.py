# crowd_mvp/viz/surface3d.py
# Renders a 2D density grid as a matplotlib 3D surface into a pygame.Surface.
# Uses FigureCanvasAgg (non-interactive Agg backend) — no plt.show() / display needed.

import numpy as np
import pygame
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg


def build_3d_surface_pygame(density_grid, canvas_w, canvas_h,
                             title="", cmap='plasma', elev=35, azim=-50):
    """Render density_grid as a 3D surface and return a pygame.Surface.

    Args:
        density_grid: np.ndarray (H, W) float — raw density values (not normalised)
        canvas_w, canvas_h: output pixel dimensions
        title: subplot title string
        cmap: matplotlib colormap name
        elev, azim: 3D viewing angles in degrees

    Returns:
        pygame.Surface of size (canvas_w, canvas_h), RGB
    """
    dpi = 100
    fig = Figure(figsize=(canvas_w / dpi, canvas_h / dpi), dpi=dpi,
                 facecolor='#12122a')
    agg = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#12122a')

    h, w = density_grid.shape
    X = np.linspace(0, 1, w)
    Y = np.linspace(0, 1, h)
    X, Y = np.meshgrid(X, Y)

    ax.plot_surface(X, Y, density_grid, cmap=cmap,
                    linewidth=0, antialiased=True, alpha=0.92)

    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, color='#cccce8', fontsize=9, pad=4)

    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.label.set_color('#778899')
        axis.label.set_fontsize(7)
        axis.pane.fill = False
        axis.pane.set_edgecolor('#2a2a4a')
    ax.tick_params(colors='#667788', labelsize=5)
    ax.grid(True, color='#252540', linewidth=0.4)
    ax.set_xlabel('X', labelpad=1)
    ax.set_ylabel('Y', labelpad=1)
    ax.set_zlabel('ρ', labelpad=1)

    fig.tight_layout(pad=0.5)
    agg.draw()

    w_px, h_px = agg.get_width_height()
    buf = np.frombuffer(agg.buffer_rgba(), dtype=np.uint8).copy()
    buf = buf.reshape(h_px, w_px, 4)
    rgb = np.ascontiguousarray(buf[:, :, :3].transpose(1, 0, 2))
    return pygame.surfarray.make_surface(rgb)
