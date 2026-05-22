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

# ---------------------------------------------------------------------------
# ROOMED_MAP — 5 rooms of different sizes connected by narrow doors.
# Agents must route through doors (A* on room graph) so congestion emerges at
# doorways — the architectural pattern the WiFi heatmap is meant to surface.
# Canvas 1000x700. Zones mirror rooms for sniffer placement.
# ---------------------------------------------------------------------------

ROOMED_MAP = {
    'size': (1000, 700),
    'rooms': [
        {'id': 'lobby', 'name': 'Lobby',     'rect': (0,   0,   250, 700)},  # medium
        {'id': 'hall',  'name': 'Expo Hall', 'rect': (250, 0,   450, 700)},  # largest
        {'id': 'bar',   'name': 'Bar',       'rect': (700, 0,   300, 280)},  # small-medium
        {'id': 'vip',   'name': 'VIP',       'rect': (700, 280, 300, 220)},  # small
        {'id': 'rest',  'name': 'Restrooms', 'rect': (700, 500, 300, 200)},  # smallest
    ],
    'walls': [
        # Vertical wall lobby <-> hall at x=250 (door gap y=320..380)
        {'x0': 250, 'y0': 0,   'x1': 250, 'y1': 320},
        {'x0': 250, 'y0': 380, 'x1': 250, 'y1': 700},
        # Vertical wall hall <-> right column at x=700 (door gaps y=100..140, 370..400, 580..620)
        {'x0': 700, 'y0': 0,   'x1': 700, 'y1': 100},
        {'x0': 700, 'y0': 140, 'x1': 700, 'y1': 370},
        {'x0': 700, 'y0': 400, 'x1': 700, 'y1': 580},
        {'x0': 700, 'y0': 620, 'x1': 700, 'y1': 700},
        # Horizontal wall bar <-> vip at y=280
        {'x0': 700, 'y0': 280, 'x1': 1000, 'y1': 280},
        # Horizontal wall vip <-> rest at y=500
        {'x0': 700, 'y0': 500, 'x1': 1000, 'y1': 500},
    ],
    'doors': [
        {'id': 'd_lobby_hall', 'rooms': ('lobby', 'hall'),
         'x0': 250, 'y0': 320, 'x1': 250, 'y1': 380, 'center': (250, 350)},
        {'id': 'd_hall_bar',   'rooms': ('hall', 'bar'),
         'x0': 700, 'y0': 100, 'x1': 700, 'y1': 140, 'center': (700, 120)},
        {'id': 'd_hall_vip',   'rooms': ('hall', 'vip'),   # narrowest — congestion point
         'x0': 700, 'y0': 370, 'x1': 700, 'y1': 400, 'center': (700, 385)},
        {'id': 'd_hall_rest',  'rooms': ('hall', 'rest'),
         'x0': 700, 'y0': 580, 'x1': 700, 'y1': 620, 'center': (700, 600)},
    ],
    'zones': [   # sniffer regions = rooms for the roomed map
        {'id': 'lobby', 'rect': (0,   0,   250, 700)},
        {'id': 'hall',  'rect': (250, 0,   450, 700)},
        {'id': 'bar',   'rect': (700, 0,   300, 280)},
        {'id': 'vip',   'rect': (700, 280, 300, 220)},
        {'id': 'rest',  'rect': (700, 500, 300, 200)},
    ],
    # Furniture that blocks movement. Each obstacle rect is expanded into 4
    # wall segments at sim init so the existing clip_to_walls handles them.
    # 'type' drives rendering (color + label) in render.py.
    'obstacles': [
        # ---- Lobby (info-desk + badge-pickup as long counters) ----
        {'id': 'info_desk',   'type': 'counter', 'label': 'Info',  'rect': (60,  100, 130, 30)},
        {'id': 'badge_desk',  'type': 'counter', 'label': 'Badge', 'rect': (60,  570, 130, 30)},
        # ---- Expo Hall: 6 sponsor booths in 2 rows ----
        {'id': 'booth_A1', 'type': 'booth', 'label': 'A1', 'rect': (300, 120, 100, 60)},
        {'id': 'booth_A2', 'type': 'booth', 'label': 'A2', 'rect': (430, 120, 100, 60)},
        {'id': 'booth_A3', 'type': 'booth', 'label': 'A3', 'rect': (560, 120, 100, 60)},
        {'id': 'booth_B1', 'type': 'booth', 'label': 'B1', 'rect': (300, 440, 100, 60)},
        {'id': 'booth_B2', 'type': 'booth', 'label': 'B2', 'rect': (430, 440, 100, 60)},
        {'id': 'booth_B3', 'type': 'booth', 'label': 'B3', 'rect': (560, 440, 100, 60)},
        # ---- Bar (long counter along the lower wall) ----
        {'id': 'bar_counter', 'type': 'bar_counter', 'label': 'Bar', 'rect': (740, 220, 220, 25)},
        # ---- VIP (two sofas flanking the sponsor stand) ----
        {'id': 'sofa_L', 'type': 'sofa', 'label': '', 'rect': (730, 410, 70, 30)},
        {'id': 'sofa_R', 'type': 'sofa', 'label': '', 'rect': (900, 410, 70, 30)},
        # ---- Restrooms (sink counter) ----
        {'id': 'sinks',   'type': 'sink',   'label': 'Sinks', 'rect': (720, 520, 100, 25)},
    ],
    # Visual-only flourishes — drawn but not collidable.
    'decor': [
        # Bar stools (small circles in front of the bar counter)
        {'id': 'stool_1', 'type': 'stool', 'pos': (760, 260), 'r': 6},
        {'id': 'stool_2', 'type': 'stool', 'pos': (800, 260), 'r': 6},
        {'id': 'stool_3', 'type': 'stool', 'pos': (840, 260), 'r': 6},
        {'id': 'stool_4', 'type': 'stool', 'pos': (880, 260), 'r': 6},
        {'id': 'stool_5', 'type': 'stool', 'pos': (920, 260), 'r': 6},
        # VIP coffee tables (small rects between sofas)
        {'id': 'coffee_table', 'type': 'table', 'rect': (830, 460, 40, 22)},
        # Restroom stall partitions (vertical thin segments — 4 stalls)
        {'id': 'stall_1', 'type': 'partition', 'line': (840, 560, 840, 690)},
        {'id': 'stall_2', 'type': 'partition', 'line': (885, 560, 885, 690)},
        {'id': 'stall_3', 'type': 'partition', 'line': (930, 560, 930, 690)},
        {'id': 'stall_4', 'type': 'partition', 'line': (975, 560, 975, 690)},
        # Lobby decorative plants (small circles at corners)
        {'id': 'plant_1', 'type': 'plant', 'pos': (25, 25), 'r': 10},
        {'id': 'plant_2', 'type': 'plant', 'pos': (225, 25), 'r': 10},
        {'id': 'plant_3', 'type': 'plant', 'pos': (25, 675), 'r': 10},
        {'id': 'plant_4', 'type': 'plant', 'pos': (225, 675), 'r': 10},
    ],
    'poi': [
        {'id': 'entrance', 'category': 'entrance',      'pos': (30,  660)},  # lobby bottom-left
        {'id': 'exit',     'category': 'exit',          'pos': (30,  40)},   # lobby top-left
        {'id': 'bar_1',    'category': 'bar',           'pos': (850, 140)},  # bar, above counter
        {'id': 'stand_1',  'category': 'sponsor_stand', 'pos': (475, 290)},  # hall main aisle
        {'id': 'stand_2',  'category': 'sponsor_stand', 'pos': (850, 340)},  # VIP, between sofas
        {'id': 'bathroom', 'category': 'bathroom',      'pos': (870, 620)},  # rest, in cubicles
    ],
}


ALL_MAPS = {'S': SMALL_MAP, 'M': MEDIUM_MAP, 'L': LARGE_MAP, 'R': ROOMED_MAP}


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


def find_room_for_point(map_def, px, py):
    """Return room id for a point, or None if map has no rooms or point is out of bounds."""
    for room in map_def.get('rooms', []):
        x, y, w, h = room['rect']
        if x <= px < x + w and y <= py < y + h:
            return room['id']
    return None


def build_room_graph(map_def):
    """Return adjacency: {room_id: [(neighbor_room_id, door_id, (cx, cy)), ...]}.

    Each edge carries the door's id and center coordinates — A* uses centers as
    the heuristic / waypoints. Empty dict if the map defines no rooms or doors.
    """
    rooms = map_def.get('rooms', [])
    doors = map_def.get('doors', [])
    graph = {r['id']: [] for r in rooms}
    for d in doors:
        a, b = d['rooms']
        cx, cy = d['center']
        if a in graph:
            graph[a].append((b, d['id'], (cx, cy)))
        if b in graph:
            graph[b].append((a, d['id'], (cx, cy)))
    return graph


def obstacles_to_walls(obstacles):
    """Expand each obstacle rect into 4 wall segments (top/right/bottom/left).

    The simulation appends these to map_def['walls'] so clip_to_walls treats
    booths/counters/sofas as collidable surfaces — agents must navigate
    around them, producing realistic crowd flow inside rooms.
    """
    walls = []
    for o in obstacles:
        x, y, w, h = o['rect']
        walls.append({'x0': x,     'y0': y,     'x1': x + w, 'y1': y})       # top
        walls.append({'x0': x + w, 'y0': y,     'x1': x + w, 'y1': y + h})   # right
        walls.append({'x0': x,     'y0': y + h, 'x1': x + w, 'y1': y + h})   # bottom
        walls.append({'x0': x,     'y0': y,     'x1': x,     'y1': y + h})   # left
    return walls


def get_room_center(map_def, room_id):
    """Return (cx, cy) of the named room, or None if not found."""
    for r in map_def.get('rooms', []):
        if r['id'] == room_id:
            x, y, w, h = r['rect']
            return (x + w // 2, y + h // 2)
    return None
