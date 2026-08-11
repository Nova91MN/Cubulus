"""Configuration for the Cubulus demo."""

# Display settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
GRID_WIDTH = 100
GRID_HEIGHT = 100
CELL_SIZE = 8
FPS = 60

# Camera settings.  CELL_SIZE is the world-space base size of a tile; the
# displayed size is CELL_SIZE * zoom.
CAMERA_START_ZOOM = 3.0
CAMERA_MIN_ZOOM = 1.25
CAMERA_MAX_ZOOM = 5.0
CAMERA_ZOOM_STEP = 0.35
CAMERA_FOLLOW_SPEED = 7.5
CAMERA_ZOOM_SPEED = 9.0

# Fixed screen-space UI areas (the camera only draws between these bars).
TOP_HUD_HEIGHT = 92
BOTTOM_HUD_HEIGHT = 72

# Game settings
PLAYER_LIVES = 3
BOT_MOVE_CHANCE = 0.4  # Probability a bot attempts a move this frame
TIMED_MODE_SECONDS = 600

# Colors used in the game
COLORS = {
    "background": (0, 0, 0),
    "neutral": (202, 202, 202),
    "grid": (8, 8, 8),
    "panel": (49, 49, 49),
    "red": (211, 0, 0),
    "yellow": (255, 205, 0),
    "green": (0, 166, 81),
    "blue": (0, 112, 221),
    "white": (248, 248, 248),
    "muted": (178, 178, 178),
}

# Player configuration
PLAYER_STARTS = {
    0: (0, 0),
    1: (99, 0),
    2: (0, 99),
    3: (99, 99),
}

PLAYER_NAMES = {
    0: "Player",
    1: "Bot-1",
    2: "Bot-2",
    3: "Bot-3",
}

PLAYER_COLOR_OPTIONS = ["red", "yellow", "green", "blue"]
GAME_MODES = ["Untimed", "Timed"]

