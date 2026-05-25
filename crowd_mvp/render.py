# crowd_mvp/render.py
# All pygame drawing for the main simulation panel and right-panel underlay.
# Simulation is headless (no pygame) — this module reads sim state and renders.

import math
import pygame

from crowd_mvp.config import (
    AGENT_RADIUS,
    COLOUR_BG, COLOUR_ZONE_FILL, COLOUR_ZONE_BORDER,
    COLOUR_AGENT, COLOUR_SNIFFER,
    COLOUR_POI_ENTRANCE, COLOUR_POI_EXIT, COLOUR_POI_BAR,
    COLOUR_POI_STAND, COLOUR_POI_BATHROOM, COLOUR_POI_TABLE,
    COLOUR_LABEL,
    FONT_SIZE_LABEL,
    WALL_THICKNESS, WALL_COLOR,
    DOOR_COLOR, DOOR_THICKNESS,
    ROOM_LABEL_SIZE, ROOM_FILL_A, ROOM_FILL_B, ROOM_BORDER,
    OBSTACLE_COLORS, OBSTACLE_BORDER, OBSTACLE_LABEL_SIZE, OBSTACLE_LABEL_COLOR,
    DECOR_STOOL_COLOR, DECOR_TABLE_COLOR, DECOR_PARTITION_COLOR, DECOR_PLANT_COLOR,
)


_POI_COLOURS = {
    'entrance':      COLOUR_POI_ENTRANCE,
    'exit':          COLOUR_POI_EXIT,
    'bar':           COLOUR_POI_BAR,
    'sponsor_stand': COLOUR_POI_STAND,
    'bathroom':      COLOUR_POI_BATHROOM,
    'table':         COLOUR_POI_TABLE,
}

_POI_LABELS = {
    'entrance':      'IN',
    'exit':          'OUT',
    'bar':           'BAR',
    'sponsor_stand': 'STD',
    'bathroom':      'WC',
    'table':         'T',
}


# Module-level font cache so we initialise SysFont once per process.
_FONTS = {}


def _font(size):
    if size not in _FONTS:
        _FONTS[size] = pygame.font.SysFont(None, size)
    return _FONTS[size]


def _scale_offset(map_size, canvas_w, canvas_h):
    """Uniform fit transform: returns (scale, offset_x, offset_y)."""
    mw, mh = map_size
    scale = min(canvas_w / mw, canvas_h / mh)
    ox = int((canvas_w - mw * scale) / 2)
    oy = int((canvas_h - mh * scale) / 2)
    return scale, ox, oy


def _tx(x, scale, ox):
    return int(x * scale) + ox


def _ty(y, scale, oy):
    return int(y * scale) + oy


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def draw_scene(surface, sim, canvas_w, canvas_h):
    """Render the full live scene (left panel) — replacement for sim.draw_scaled.

    Layer order, back to front:
        background -> rooms (or zones) -> decor -> obstacles -> walls -> doors ->
        POIs -> agents -> sniffers.
    """
    map_def = sim.map_def
    scale, ox, oy = _scale_offset(map_def['size'], canvas_w, canvas_h)
    surface.fill(COLOUR_BG)

    _draw_rooms_or_zones(surface, map_def, scale, ox, oy, with_labels=True)
    _draw_decor(surface, map_def.get('decor', []), scale, ox, oy)
    _draw_obstacles(surface, map_def.get('obstacles', []), scale, ox, oy)
    _draw_walls(surface, map_def.get('walls', []), scale, ox, oy)
    _draw_doors(surface, map_def.get('doors', []), scale, ox, oy)
    _draw_pois(surface, map_def.get('poi', []), scale, ox, oy)
    _draw_agents(surface, sim.agents, scale, ox, oy)
    _draw_sniffers(surface, sim.sniffers, scale, ox, oy)


def draw_map_scaled(surface, map_def, canvas_w, canvas_h):
    """Render map geometry only — used as heatmap underlay (right panel, tab 1).

    Replacement for sim.draw_map_scaled. No agents, no sniffers.
    """
    scale, ox, oy = _scale_offset(map_def['size'], canvas_w, canvas_h)
    surface.fill(COLOUR_BG)
    _draw_rooms_or_zones(surface, map_def, scale, ox, oy, with_labels=False)
    _draw_decor(surface, map_def.get('decor', []), scale, ox, oy)
    _draw_obstacles(surface, map_def.get('obstacles', []), scale, ox, oy)
    _draw_walls(surface, map_def.get('walls', []), scale, ox, oy)
    _draw_doors(surface, map_def.get('doors', []), scale, ox, oy)

    # POIs as small dots (smaller than on the main panel so they don't dominate)
    for poi in map_def.get('poi', []):
        px, py = poi['pos']
        colour = _POI_COLOURS.get(poi['category'], (200, 200, 200))
        pygame.draw.circle(
            surface, colour,
            (_tx(px, scale, ox), _ty(py, scale, oy)),
            max(3, int(6 * scale))
        )


# ---------------------------------------------------------------------------
# Layers
# ---------------------------------------------------------------------------

def _draw_rooms_or_zones(surface, map_def, scale, ox, oy, with_labels):
    """Draw rooms (with names) if the map defines them, else fall back to zones."""
    rooms = map_def.get('rooms', [])
    if rooms:
        label_font = _font(ROOM_LABEL_SIZE)
        for i, room in enumerate(rooms):
            x, y, w, h = room['rect']
            rect = pygame.Rect(
                _tx(x, scale, ox), _ty(y, scale, oy),
                max(1, int(w * scale)), max(1, int(h * scale)),
            )
            fill = ROOM_FILL_A if i % 2 == 0 else ROOM_FILL_B
            pygame.draw.rect(surface, fill, rect)
            pygame.draw.rect(surface, ROOM_BORDER, rect, 1)

            if with_labels and rect.width > 40 and rect.height > 24:
                name = room.get('name', room['id'])
                surf = label_font.render(name, True, (90, 95, 110))
                surface.blit(
                    surf,
                    (rect.centerx - surf.get_width() // 2,
                     rect.y + 6),
                )
        return

    # Legacy: zone fills + borders (S/M/L maps)
    for zone in map_def.get('zones', []):
        x, y, w, h = zone['rect']
        rect = pygame.Rect(
            _tx(x, scale, ox), _ty(y, scale, oy),
            max(1, int(w * scale)), max(1, int(h * scale)),
        )
        pygame.draw.rect(surface, COLOUR_ZONE_FILL, rect)
        pygame.draw.rect(surface, COLOUR_ZONE_BORDER, rect, 1)


def _draw_walls(surface, walls, scale, ox, oy):
    if not walls:
        return
    thickness = max(1, int(WALL_THICKNESS * scale)) if scale < 1 else WALL_THICKNESS
    for w in walls:
        p0 = (_tx(w['x0'], scale, ox), _ty(w['y0'], scale, oy))
        p1 = (_tx(w['x1'], scale, ox), _ty(w['y1'], scale, oy))
        pygame.draw.line(surface, WALL_COLOR, p0, p1, thickness)


def _draw_doors(surface, doors, scale, ox, oy):
    if not doors:
        return
    thickness = max(2, int(DOOR_THICKNESS * scale)) if scale < 1 else DOOR_THICKNESS
    for d in doors:
        p0 = (_tx(d['x0'], scale, ox), _ty(d['y0'], scale, oy))
        p1 = (_tx(d['x1'], scale, ox), _ty(d['y1'], scale, oy))
        pygame.draw.line(surface, DOOR_COLOR, p0, p1, thickness)


def _draw_pois(surface, pois, scale, ox, oy):
    label_font = _font(FONT_SIZE_LABEL)
    for poi in pois:
        colour = _POI_COLOURS.get(poi['category'], (200, 200, 200))
        px, py = poi['pos']
        sx, sy = _tx(px, scale, ox), _ty(py, scale, oy)
        poi_rect = pygame.Rect(sx - 4, sy - 4, 8, 8)
        pygame.draw.rect(surface, colour, poi_rect)

        label = _POI_LABELS.get(poi['category'], '?')
        txt = label_font.render(label, True, COLOUR_LABEL)
        surface.blit(txt, (sx - txt.get_width() // 2, sy + 6))


def _draw_agents(surface, agents, scale, ox, oy):
    r = max(2, int(AGENT_RADIUS * scale)) if scale < 1 else AGENT_RADIUS
    for agent in agents:
        sx = _tx(agent.x, scale, ox)
        sy = _ty(agent.y, scale, oy)
        pygame.draw.circle(surface, COLOUR_AGENT, (sx, sy), r)


def _draw_obstacles(surface, obstacles, scale, ox, oy):
    """Filled rectangles representing furniture that blocks agent movement."""
    if not obstacles:
        return
    label_font = _font(OBSTACLE_LABEL_SIZE)
    for o in obstacles:
        x, y, w, h = o['rect']
        rect = pygame.Rect(
            _tx(x, scale, ox), _ty(y, scale, oy),
            max(1, int(w * scale)), max(1, int(h * scale)),
        )
        color = OBSTACLE_COLORS.get(o.get('type'), (160, 160, 160))
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, OBSTACLE_BORDER, rect, 1)

        # Optional label centered inside the rect (skipped if too small to fit)
        label = o.get('label')
        if label and rect.width > 18 and rect.height > 12:
            txt = label_font.render(label, True, OBSTACLE_LABEL_COLOR)
            if txt.get_width() <= rect.width - 4 and txt.get_height() <= rect.height - 2:
                surface.blit(
                    txt,
                    (rect.centerx - txt.get_width() // 2,
                     rect.centery - txt.get_height() // 2),
                )


def _draw_decor(surface, decor, scale, ox, oy):
    """Visual-only flourishes — stools, tables, partitions, plants."""
    if not decor:
        return
    for d in decor:
        t = d.get('type')
        if t == 'stool':
            cx, cy = d['pos']
            r = max(2, int(d.get('r', 5) * scale)) if scale < 1 else d.get('r', 5)
            pygame.draw.circle(
                surface, DECOR_STOOL_COLOR,
                (_tx(cx, scale, ox), _ty(cy, scale, oy)), r,
            )
        elif t == 'plant':
            cx, cy = d['pos']
            r = max(3, int(d.get('r', 8) * scale)) if scale < 1 else d.get('r', 8)
            pygame.draw.circle(
                surface, DECOR_PLANT_COLOR,
                (_tx(cx, scale, ox), _ty(cy, scale, oy)), r,
            )
        elif t == 'table':
            x, y, w, h = d['rect']
            rect = pygame.Rect(
                _tx(x, scale, ox), _ty(y, scale, oy),
                max(1, int(w * scale)), max(1, int(h * scale)),
            )
            pygame.draw.rect(surface, DECOR_TABLE_COLOR, rect)
            pygame.draw.rect(surface, OBSTACLE_BORDER, rect, 1)
        elif t == 'partition':
            x0, y0, x1, y1 = d['line']
            pygame.draw.line(
                surface, DECOR_PARTITION_COLOR,
                (_tx(x0, scale, ox), _ty(y0, scale, oy)),
                (_tx(x1, scale, ox), _ty(y1, scale, oy)),
                1,
            )


def _draw_sniffers(surface, sniffers, scale, ox, oy):
    """WiFi fan icon + estimated-count label per sniffer."""
    label_font = _font(FONT_SIZE_LABEL)
    for s in sniffers:
        sx = _tx(s.pos[0], scale, ox)
        sy = _ty(s.pos[1], scale, oy)
        # Three concentric upward arcs
        for radius in (6, 10, 14):
            rect = pygame.Rect(sx - radius, sy - radius, radius * 2, radius * 2)
            pygame.draw.arc(
                surface, COLOUR_SNIFFER, rect,
                math.radians(225), math.radians(315), 2,
            )
        pygame.draw.circle(surface, COLOUR_SNIFFER, (sx, sy), 3)

        count_str = str(s.estimated_count)
        txt = label_font.render(count_str, True, COLOUR_SNIFFER)
        surface.blit(txt, (sx - txt.get_width() // 2, sy + 16))
