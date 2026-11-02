# ===== FILE: settings.py =====
"""settings.py - Every tweakable constant lives here (no magic numbers elsewhere)."""

# ---------------- Window ----------------
WIDTH, HEIGHT = 1000, 700
FPS = 60
TITLE = "Dental Game"
MAX_DT = 0.05            # Clamp delta time so a lag spike can't teleport things

# ---------------- Rules ----------------
ROUND_TIME_SECONDS = 600     # 10 minutes. Lower this (e.g. 20) to test the Time's Up screen
BACTERIA_TO_CLEAN = 10       # Cleaned this many -> dentist wins
BACTERIA_TO_LOSE = 10        # This many reach the teeth -> bacteria win
FIRST_SPAWN_DELAY = 0.5      # Seconds before the first bacteria of a round

# ---------------- Level config ----------------
# speed: pixels/second | spawn_interval: average seconds between spawns
# max_bacteria: limit on screen | wobble: sideways zig-zag strength
LEVELS = [
    {"name": "Easy",   "speed": 70,  "spawn_interval": 2.6, "max_bacteria": 4, "wobble": 0.40},
    {"name": "Medium", "speed": 115, "spawn_interval": 1.8, "max_bacteria": 6, "wobble": 0.70},
    {"name": "Hard",   "speed": 170, "spawn_interval": 1.0, "max_bacteria": 9, "wobble": 1.20},
]
SPAWN_JITTER = (0.7, 1.3)        # Random multiplier on the spawn interval

# ---------------- Colors ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WALL_COLOR = (214, 238, 235)
WALL_STRIPE = (190, 224, 220)
FLOOR_A = (235, 235, 240)
FLOOR_B = (200, 205, 215)
LIP_RED = (200, 30, 50)
MOUTH_DARK = (110, 20, 40)
GUM_PINK = (242, 130, 150)
TOOTH_WHITE = (252, 252, 248)
TOOTH_OUTLINE = (175, 175, 185)
FLASH_RED = (255, 0, 0)
HUD_BG = (20, 30, 50, 190)
HUD_TEXT = (255, 255, 255)
HUD_GOOD = (140, 255, 160)
HUD_BAD = (255, 130, 130)
HUD_TIME_LOW = (255, 90, 90)
PANEL_BG = (255, 250, 235, 235)
TEXT_DARK = (40, 40, 70)
BRUSH_HANDLE = (40, 120, 230)
BRUSH_HEAD = (255, 150, 40)
BRUSH_OUTLINE = (20, 30, 80)
BRISTLE_COLOR = (130, 210, 255)
BACTERIA_COLORS = [(90, 200, 90), (150, 90, 200)]   # green and purple
SPARKLE_COLORS = [(255, 255, 120), (255, 255, 255), (150, 230, 255)]

# ---------------- Layout ----------------
HUD_HEIGHT = 46
FLOOR_Y = 560
TILE_SIZE = 50
MOUTH_CENTER = (500, 350)
LIPS_SIZE = (840, 340)
INNER_MOUTH_SIZE = (800, 300)
TEETH_PER_ROW = 14
TOOTH_W, TOOTH_H, TOOTH_GAP = 40, 65, 3
UPPER_TEETH_Y = 280
LOWER_TEETH_Y = 355
GUM_OVERHANG = 8
TOOTH_RADIUS = 12
FLASH_DURATION = 0.4
FLASH_MAX_ALPHA = 140

# ---------------- Toothbrush ----------------
BRUSH_SPEED = 400
BRUSH_HEAD_W, BRUSH_HEAD_H = 80, 20
BRUSH_BRISTLE_H = 18
BRUSH_HANDLE_L, BRUSH_HANDLE_H = 130, 14
BRUSH_TOTAL_W = BRUSH_HEAD_W + BRUSH_HANDLE_L
BRISTLE_SPACING = 6
BRUSH_START_BOTTOM_MARGIN = 140

# ---------------- Bacteria ----------------
BACTERIA_RADIUS = 18
BACTERIA_SPEED_VARIATION = (0.85, 1.15)
WOBBLE_FREQ_RANGE = (2.0, 4.0)
DRIFT_CHANGE_RANGE = (0.4, 1.0)   # Seconds between random zig-zag direction changes
WOBBLE_SINE_WEIGHT = 0.6
WOBBLE_DRIFT_WEIGHT = 0.4
SPIKE_COUNT = 8
SPIKE_LENGTH = 8

# ---------------- Particles ----------------
SPARKLE_COUNT = 10
SPARKLE_SPEED = (60, 160)
SPARKLE_LIFE = (0.3, 0.6)
RING_LIFE = 0.35
RING_MAX_RADIUS = 40