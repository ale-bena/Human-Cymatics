# crowd_mvp/config.py
# Global simulation constants — defaults calibrated for a convincing pitch demo.

# Display
WINDOW_TITLE = "Human Cymatics — Crowd Monitor"
FPS = 60

# Simulation defaults (SIM-06: configurable via slider, default 50 for small map)
N_PEOPLE = 50
SIM_DURATION = 300  # seconds (SIM-07: auto-stop after this duration)

# Agent movement (D-02)
AGENT_SPEED = 1.5       # pixels per frame
AGENT_NOISE = 0.3       # px/frame random jitter magnitude
AGENT_RADIUS = 4        # render radius in pixels
ARRIVAL_THRESHOLD = 12  # distance in px at which agent considers POI reached
DWELL_MIN_FRAMES = 60   # minimum dwell at POI (1 second at 60 FPS) (D-03)
DWELL_MAX_FRAMES = 180  # maximum dwell at POI (3 seconds at 60 FPS) (D-03)

# Sniffer (SNF-03: σ is a global parameter, same for all nodes)
SIGMA_ERROR = 2.0  # Gaussian noise std dev for sniffer estimates
SNIFFER_TICK_FRAMES = 60  # frames between sniffer ticks (D-10: 60 frames ≈ 1 second)

# Colours (D-05, D-08)
COLOUR_BG = (240, 240, 240)          # light grey canvas
COLOUR_ZONE_FILL = (220, 220, 220)   # darker grey zone areas
COLOUR_ZONE_BORDER = (160, 160, 160) # thin zone border lines
COLOUR_AGENT = (180, 220, 255)       # light blue agents (D-05)
COLOUR_SNIFFER = (60, 120, 200)      # sniffer WiFi icon
COLOUR_POI_ENTRANCE = (80, 200, 80)  # green
COLOUR_POI_EXIT = (200, 80, 80)      # red
COLOUR_POI_BAR = (255, 180, 0)       # amber
COLOUR_POI_STAND = (180, 100, 220)   # purple
COLOUR_POI_BATHROOM = (80, 180, 200) # teal
COLOUR_POI_TABLE = (160, 130, 95)    # warm wood — sit-down tables
COLOUR_OVERLAY_BG = (20, 20, 20, 180) # semi-transparent end overlay (D-11)
COLOUR_TEXT = (255, 255, 255)
COLOUR_LABEL = (40, 40, 40)

# Font sizes
FONT_SIZE_LABEL = 11   # POI and sniffer count labels
FONT_SIZE_OVERLAY = 28 # "Simulation complete" text

# Phase 2 — UI Layout (D-02, D-03, D-04)
WINDOW_W = 1200          # total window width (D-02)
WINDOW_H = 520           # total window height (D-02)
CANVAS_W = 600           # each panel canvas width (D-05)
CANVAS_H = 400           # each panel canvas height (D-05)
TAB_BAR_H = 25           # tab strip height (D-04)
CONTROL_PANEL_H = 75     # horizontal control bar height (D-03)
STATUS_BAR_H = 20        # bottom status bar (existing, now named)

# Phase 2 — Slider ranges (CTR-01)
N_PEOPLE_MIN = 10
N_PEOPLE_MAX = 700
N_PEOPLE_DEFAULT = 50       # small map default
N_PEOPLE_DEFAULT_M = 150    # medium map default
N_PEOPLE_DEFAULT_L = 300    # large map default
SIGMA_ERROR_MIN = 0.1
SIGMA_ERROR_MAX = 10.0
SIGMA_KERNEL_MIN = 10.0
SIGMA_KERNEL_MAX = 100.0
SIGMA_KERNEL_DEFAULT = 30.0  # KDE bandwidth in native map pixels

# Phase 2 — UI Colours
COLOUR_TAB_ACTIVE   = (60,  120, 200)   # same as COLOUR_SNIFFER — blue
COLOUR_TAB_INACTIVE = (160, 160, 160)
COLOUR_BTN_ACTIVE   = (60,  180, 80)    # green for selected map/behavior
COLOUR_BTN_INACTIVE = (180, 180, 180)
COLOUR_CONTROL_BG   = (230, 230, 230)   # control panel background
COLOUR_SLIDER_TRACK = (160, 160, 160)
COLOUR_SLIDER_THUMB = (60,  120, 200)

# Rooms / walls / doors — rendered when a map defines them (e.g. ROOMED_MAP)
WALL_THICKNESS  = 3
WALL_COLOR      = (55, 55, 70)
DOOR_COLOR      = (80, 200, 80)        # bright green — visible "where to cross"
DOOR_THICKNESS  = 4
ROOM_LABEL_SIZE = 16
ROOM_FILL_A     = (245, 245, 250)      # subtle alternating fills so adjacent
ROOM_FILL_B     = (232, 236, 246)      # rooms read as distinct spaces
ROOM_BORDER     = (180, 185, 200)

# Obstacles (block movement) — colored by 'type' field on the obstacle dict
OBSTACLE_COLORS = {
    'booth':       (218, 165, 95),   # warm orange — sponsor stands
    'counter':     (130, 145, 175),  # blue-gray — info/badge desks
    'bar_counter': (120,  85,  60),  # dark wood — bar
    'sofa':        (170, 105, 105),  # muted red — VIP sofas
    'sink':        (175, 200, 215),  # light blue — restroom sinks
}
OBSTACLE_BORDER  = (70, 70, 80)
OBSTACLE_LABEL_SIZE = 12
OBSTACLE_LABEL_COLOR = (40, 40, 50)

# Decor (visual only) — colored by 'type'
DECOR_STOOL_COLOR     = (110,  80,  55)
DECOR_TABLE_COLOR     = (200, 185, 150)
DECOR_PARTITION_COLOR = (150, 155, 170)
DECOR_PLANT_COLOR     = (90, 150, 90)

# Alert thresholds (web Safety UI)
ALERT_CAPACITY_WARN  = 0.8
ALERT_CAPACITY_CRIT  = 1.0
ALERT_SURGE_RATIO    = 0.5
ALERT_BOTTLENECK_RATIO = 0.5
ALERT_EVAC_DISTANCE  = 300
ALERT_DATAQUAL_RATIO = 0.3
