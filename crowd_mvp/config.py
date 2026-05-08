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
COLOUR_OVERLAY_BG = (20, 20, 20, 180) # semi-transparent end overlay (D-11)
COLOUR_TEXT = (255, 255, 255)
COLOUR_LABEL = (40, 40, 40)

# Font sizes
FONT_SIZE_LABEL = 11   # POI and sniffer count labels
FONT_SIZE_OVERLAY = 28 # "Simulation complete" text
