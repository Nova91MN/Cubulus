"""
Configuration module for Cubulus v0.0.0 Demo.
"""

# Display settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
GRID_WIDTH = 100
GRID_HEIGHT = 100
CELL_SIZE = WINDOW_WIDTH // GRID_WIDTH
FPS = 30

# Game settings
PLAYER_LIVES = 3
BOT_MOVE_CHANCE = 0.4  # Probability a bot attempts a move this frame
TIMED_MODE_SECONDS = 600

# Colors used in the game
COLORS = {
    "neutral": (30, 30, 30),
    "red": (220, 53, 69),
    "yellow": (255, 193, 7),
    "green": (40, 167, 69),
    "blue": (0, 123, 255),
    "white": (245, 245, 245),
}

# Player configuration
PLAYER_STARTS = {
    0: (5, 5),
    1: (94, 5),
    2: (5, 94),
    3: (94, 94),
}

PLAYER_NAMES = {
    0: "Player",
    1: "Bot-1",
    2: "Bot-2",
    3: "Bot-3",
}

PLAYER_COLOR_OPTIONS = ["red", "yellow", "green", "blue"]
GAME_MODES = ["Untimed", "Timed"]

