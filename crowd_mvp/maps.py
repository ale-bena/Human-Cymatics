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


MEDIUM_MAP = {
    'size': (900, 600),
    'zones': [
        {'id': 'A', 'rect': (0,   0,   225, 300)},  # top-left
        {'id': 'B', 'rect': (225, 0,   225, 300)},  # top col-2
        {'id': 'C', 'rect': (450, 0,   225, 300)},  # top col-3
        {'id': 'D', 'rect': (675, 0,   225, 300)},  # top-right
        {'id': 'E', 'rect': (0,   300, 225, 300)},  # bottom-left
        {'id': 'F', 'rect': (225, 300, 225, 300)},  # bottom col-2
        {'id': 'G', 'rect': (450, 300, 225, 300)},  # bottom col-3
        {'id': 'H', 'rect': (675, 300, 225, 300)},  # bottom-right
    ],
    'poi': [
        {'id': 'entrance',   'category': 'entrance',      'pos': (50,  300)},
        {'id': 'exit',       'category': 'exit',          'pos': (850, 300)},
        {'id': 'bar_1',      'category': 'bar',           'pos': (225, 150)},
        {'id': 'bar_2',      'category': 'bar',           'pos': (675, 450)},
        {'id': 'stand_1',    'category': 'sponsor_stand', 'pos': (450, 150)},
        {'id': 'stand_2',    'category': 'sponsor_stand', 'pos': (225, 450)},
        {'id': 'bathroom_1', 'category': 'bathroom',      'pos': (675, 150)},
        {'id': 'bathroom_2', 'category': 'bathroom',      'pos': (450, 450)},
        {'id': 'bar_3',      'category': 'bar',           'pos': (112, 450)},
        {'id': 'stand_3',    'category': 'sponsor_stand', 'pos': (787, 150)},
    ]
}

LARGE_MAP = {
    'size': (1200, 800),
    'zones': [
        {'id': 'A', 'rect': (0,   0,   300, 266)},  # row 0 col 0
        {'id': 'B', 'rect': (300, 0,   300, 266)},  # row 0 col 1
        {'id': 'C', 'rect': (600, 0,   300, 266)},  # row 0 col 2
        {'id': 'D', 'rect': (900, 0,   300, 266)},  # row 0 col 3
        {'id': 'E', 'rect': (0,   266, 300, 266)},  # row 1 col 0
        {'id': 'F', 'rect': (300, 266, 300, 266)},  # row 1 col 1
        {'id': 'G', 'rect': (600, 266, 300, 266)},  # row 1 col 2
        {'id': 'H', 'rect': (900, 266, 300, 266)},  # row 1 col 3
        {'id': 'I', 'rect': (0,   532, 300, 268)},  # row 2 col 0
        {'id': 'J', 'rect': (300, 532, 300, 268)},  # row 2 col 1
        {'id': 'K', 'rect': (600, 532, 300, 268)},  # row 2 col 2
        {'id': 'L', 'rect': (900, 532, 300, 268)},  # row 2 col 3
    ],
    'poi': [
        {'id': 'entrance',   'category': 'entrance',      'pos': (60,   400)},
        {'id': 'exit',       'category': 'exit',          'pos': (1140, 400)},
        {'id': 'bar_1',      'category': 'bar',           'pos': (300,  133)},
        {'id': 'bar_2',      'category': 'bar',           'pos': (900,  133)},
        {'id': 'bar_3',      'category': 'bar',           'pos': (600,  666)},
        {'id': 'stand_1',    'category': 'sponsor_stand', 'pos': (600,  133)},
        {'id': 'stand_2',    'category': 'sponsor_stand', 'pos': (300,  666)},
        {'id': 'stand_3',    'category': 'sponsor_stand', 'pos': (900,  666)},
        {'id': 'bathroom_1', 'category': 'bathroom',      'pos': (150,  266)},
        {'id': 'bathroom_2', 'category': 'bathroom',      'pos': (750,  400)},
        {'id': 'bathroom_3', 'category': 'bathroom',      'pos': (1050, 532)},
        {'id': 'bar_4',      'category': 'bar',           'pos': (450,  400)},
        {'id': 'stand_4',    'category': 'sponsor_stand', 'pos': (150,  666)},
        {'id': 'bar_5',      'category': 'bar',           'pos': (1050, 266)},
        {'id': 'stand_5',    'category': 'sponsor_stand', 'pos': (750,  133)},
    ]
}

import os as _os
_PROJECT_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

VENUE_MAP = {
    'size': (1375, 1144),
    'bg_image': _os.path.join(_PROJECT_ROOT, 'Planimetria_map4.png'),
    'bg_colour': (245, 244, 240),
    'zones': [
        # Top narrow section (staircase top-left of building)
        {'id': 'Ingresso',  'label': 'Ingresso',    'rect': (305,  45, 195, 100), 'colour': (80,  200, 120, 130)},
        # Top expanded corridor (full building width reached at ~row 150)
        {'id': 'Corr_N',   'label': 'Corr. Nord',  'rect': (305, 155, 600, 115), 'colour': (70,  130, 210, 130)},
        # Upper-right room (reachable once building widens past col 960)
        {'id': 'Sala_NE',  'label': 'Sala NE',     'rect': (960, 155, 255, 130), 'colour': (160,  90, 200, 130)},
        # Large central-left hall
        {'id': 'Atrio',    'label': 'Atrio',        'rect': (270, 280, 420, 430), 'colour': (210, 175,  65, 130)},
        # Central-right hall
        {'id': 'Sala_E',   'label': 'Sala Est',    'rect': (730, 280, 430, 380), 'colour': (200, 105,  85, 130)},
        # Horizontal connecting corridor (mid-building)
        {'id': 'Corr_C',   'label': 'Corr. Centr.','rect': (215, 720, 760, 105), 'colour': ( 95, 195, 195, 130)},
        # Bottom-left room
        {'id': 'Sala_SO',  'label': 'Sala SW',     'rect': (195, 845, 205, 150), 'colour': (205, 140,  80, 130)},
        # Bottom-center room
        {'id': 'Sala_S',   'label': 'Sala Sud',    'rect': (460, 845, 300, 150), 'colour': (115, 200, 115, 130)},
        # Bottom-right room
        {'id': 'Sala_SE',  'label': 'Sala SE',     'rect': (820, 845, 210, 110), 'colour': (170, 120, 200, 130)},
    ],
    'poi': [
        {'id': 'entrance',   'category': 'entrance',      'pos': (340,  80)},
        {'id': 'exit',       'category': 'exit',          'pos': (215, 920)},
        {'id': 'bar_1',      'category': 'bar',           'pos': (510, 200)},
        {'id': 'bar_2',      'category': 'bar',           'pos': (880, 420)},
        {'id': 'bar_3',      'category': 'bar',           'pos': (590, 900)},
        {'id': 'stand_1',    'category': 'sponsor_stand', 'pos': (1060, 190)},
        {'id': 'stand_2',    'category': 'sponsor_stand', 'pos': (380,  470)},
        {'id': 'bathroom_1', 'category': 'bathroom',      'pos': (990,  210)},
        {'id': 'bathroom_2', 'category': 'bathroom',      'pos': (670,  760)},
        {'id': 'bathroom_3', 'category': 'bathroom',      'pos': (310,  870)},
    ],
}

ALL_MAPS = {'S': SMALL_MAP, 'M': MEDIUM_MAP, 'L': LARGE_MAP, '4': VENUE_MAP}


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
