# crowd_mvp/maps.py
# Map data definitions. SMALL_MAP is the Phase 1 map.
# Zones are 2x2 equal grid covering the 600x400 canvas (D-12).
# POI categories: entrance, exit, bar, sponsor_stand, bathroom (D-13, MAP-05).

SMALL_MAP = {
    'size': (600, 400),
    'zones': [
        {'id': 'A', 'rect': (0,   0,   300, 200)},  # top-left
        {'id': 'B', 'rect': (300, 0,   300, 200)},  # top-right
        {'id': 'C', 'rect': (0,   200, 300, 200)},  # bottom-left
        {'id': 'D', 'rect': (300, 200, 300, 200)},  # bottom-right
    ],
    'poi': [
        {'id': 'entrance', 'category': 'entrance',     'pos': (50,  200)},
        {'id': 'exit',     'category': 'exit',         'pos': (550, 200)},
        {'id': 'bar',      'category': 'bar',          'pos': (150, 100)},
        {'id': 'stand',    'category': 'sponsor_stand','pos': (450, 100)},
        {'id': 'bathroom', 'category': 'bathroom',     'pos': (300, 350)},
    ]
}


def get_sniffer_positions(map_def):
    """Return list of (zone_id, center_x, center_y) for each zone.
    Sniffer is placed at the geometric centre of its zone (SNF-01).
    """
    positions = []
    for zone in map_def['zones']:
        x, y, w, h = zone['rect']
        cx = x + w // 2
        cy = y + h // 2
        positions.append({'zone_id': zone['id'], 'pos': (cx, cy)})
    return positions


def get_map_bounds(map_def):
    """Return (width, height) of map canvas."""
    return map_def['size']


def find_zone_for_point(map_def, px, py):
    """Return zone id for a point (px, py), or None if out of bounds."""
    for zone in map_def['zones']:
        x, y, w, h = zone['rect']
        if x <= px < x + w and y <= py < y + h:
            return zone['id']
    return None
