import zlib
import struct
import base64
import numpy as np

from crowd_mvp.viz.colormaps import VIRIDIS as _VIRIDIS
from crowd_mvp.viz.heatmap import _compute_density, _GRID_W, _GRID_H


def kde_to_b64(sniffer_positions, sniffer_counts, map_size, sigma_kernel=20.0):
    """Return 'data:image/png;base64,...' KDE heatmap PNG for the given map_size."""
    map_w, map_h = map_size
    density = _compute_density(sniffer_positions, sniffer_counts, map_w, map_h, sigma_kernel)

    d_min, d_max = density.min(), density.max()
    normed = (density - d_min) / (d_max - d_min) if d_max > d_min else np.zeros_like(density)

    indices = (np.clip(normed, 0.0, 1.0) * 255).astype(np.int32)
    rgb_small = _VIRIDIS._lut[indices]  # (GRID_H, GRID_W, 3)

    scale_x = max(1, map_w // _GRID_W)
    scale_y = max(1, map_h // _GRID_H)
    rgb_up = np.repeat(np.repeat(rgb_small, scale_y, axis=0), scale_x, axis=1)

    # Crop to map_size; pad with border color if upscale falls short
    rgba = np.zeros((map_h, map_w, 4), dtype=np.uint8)
    h_up = min(rgb_up.shape[0], map_h)
    w_up = min(rgb_up.shape[1], map_w)
    rgba[:h_up, :w_up, :3] = rgb_up[:h_up, :w_up].astype(np.uint8)
    rgba[:h_up, :w_up, 3] = 179

    return 'data:image/png;base64,' + base64.b64encode(_png_rgba(rgba)).decode()


def estimate_to_b64(map_def, estimated_counts):
    """Return 'data:image/png;base64,...' zone-fill WiFi estimate heatmap."""
    map_w, map_h = map_def['size']
    canvas = np.zeros((map_h, map_w, 4), dtype=np.uint8)

    zones = map_def.get('zones', [])
    all_counts = [estimated_counts.get(z['id'], 0) for z in zones]
    norm_max = max(max(all_counts) if all_counts else 0, 1)

    for zone in zones:
        count = estimated_counts.get(zone['id'], 0)
        idx = int(np.clip(float(count) / norm_max, 0.0, 1.0) * 255)
        r, g, b = _VIRIDIS._lut[idx]
        zx, zy, zw, zh = zone['rect']
        x1 = max(0, int(zx))
        y1 = max(0, int(zy))
        x2 = min(map_w, int(zx + zw))
        y2 = min(map_h, int(zy + zh))
        canvas[y1:y2, x1:x2] = [r, g, b, 179]

    return 'data:image/png;base64,' + base64.b64encode(_png_rgba(canvas)).decode()


def _png_rgba(rgba_array):
    """Encode (H, W, 4) uint8 RGBA array as PNG bytes using stdlib zlib only."""
    h, w = rgba_array.shape[:2]
    raw = b''.join(b'\x00' + rgba_array[y].tobytes() for y in range(h))

    def chunk(tag, data):
        payload = tag + data
        return struct.pack('>I', len(data)) + payload + struct.pack('>I', zlib.crc32(payload) & 0xffffffff)

    # IHDR: width, height, bit_depth=8, color_type=6 (RGBA), compress=0, filter=0, interlace=0
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    return (
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', ihdr)
        + chunk(b'IDAT', zlib.compress(raw, 1))
        + chunk(b'IEND', b'')
    )
