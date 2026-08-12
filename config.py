"""Configuration for the Cubulus demo."""

# Display settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
GRID_WIDTH = 100
GRID_HEIGHT = 100
CELL_SIZE = 8
FPS = 60
RESOLUTION_OPTIONS = (
    (960, 720),
    (1200, 900),
    (1280, 720),
    (1600, 900),
    (1920, 1080),
)

# The selected multiplier only affects gameplay while debug mode is enabled.
DEBUG_SPEED_OPTIONS = (0.25, 0.5, 1.0, 2.0, 4.0)

# This independent debug multiplier only changes the human player's automatic
# movement interval. Bots and all other simulation systems keep their speed.
DEBUG_PLAYER_SPEED_OPTIONS = (0.25, 0.5, 1.0, 2.0, 4.0)

# Camera settings.  CELL_SIZE is the world-space base size of a tile; the
# displayed size is CELL_SIZE * zoom.
CAMERA_START_ZOOM = 3.0
CAMERA_MIN_ZOOM = 1.25
CAMERA_MAX_ZOOM = 5.0
CAMERA_ZOOM_STEP = 0.35
CAMERA_FOLLOW_SPEED = 7.5
CAMERA_ZOOM_SPEED = 9.0

# Game settings
PLAYER_LIVES = 3
DAMAGE_COOLDOWN_MS = 1200
DAMAGE_FLASH_MS = 280
TIMED_MODE_SECONDS = 600
PLAYER_MOVE_INTERVAL_MS = 85

# Difficulty affects how often bots move and how consistently they pursue the
# human player. In Territory mode it also defines the share of all playable
# tiles a color has to conquer to win.
DIFFICULTY_LEVELS = (
    "Beginner",
    "Easy",
    "Normal",
    "Hard",
    "Expert",
    "God",
)
DIFFICULTY_PROFILES = {
    "Beginner": {"bot_move_chance": 0.07, "bot_chase_chance": 0.12},
    "Easy": {"bot_move_chance": 0.12, "bot_chase_chance": 0.25},
    "Normal": {"bot_move_chance": 0.24, "bot_chase_chance": 0.55},
    "Hard": {"bot_move_chance": 0.40, "bot_chase_chance": 0.85},
    "Expert": {"bot_move_chance": 0.55, "bot_chase_chance": 0.95},
    # God uses the Expert AI profile. Its additional bot alliance is handled
    # by the collision rules in main.py.
    "God": {"bot_move_chance": 0.55, "bot_chase_chance": 0.95},
}
TERRITORY_WIN_PERCENTAGES = {
    "Beginner": 0.025,
    "Easy": 0.05,
    "Normal": 0.10,
    "Hard": 0.20,
    "Expert": 0.50,
    "God": 0.75,
}

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
    "purple": (151, 71, 255),
    "orange": (255, 128, 0),
    "cyan": (0, 207, 230),
    "pink": (255, 79, 154),
    "lime": (139, 220, 50),
    "teal": (0, 176, 155),
    "white": (248, 248, 248),
    "muted": (178, 178, 178),
    "obstacle": (70, 79, 92),
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

BOT_NAMES = (
    "Jesus",
    "Hans",
    "Dieter",
    "Günther",
    "Ute",
    "Hans-Dieter",
    "Otto",
    "Siegfried",
    "Werner",
    "Anna",
    "Robin",
    "Noah",
    "Kevin",
    "Peter",
    "David",
    "Dave",
    "William",
    "Michelle",
    "Michaela",
    "Markus",
    "Marcus",
    "Marko",
    "Marco",
    "Lucas",
    "Lukas",
    "Luca",
    "Luka",
    "Cécile",
    "Marylin",
    "Marie",
    "Anne-Marie",
    "Monika",
    "Monica",
    "Super",
    "Mega",
    "Giga",
    "Tera",
    "Micro",
    "Macro",
    "Dingus",
    "Bingus",
    "Bogus",
    "Cao Cao",
    "Zhao Yun",
    "Liu Bei",
    "Sun Jian",
    "Sun Ce",
    "Sun Quan",
    "Liu Shan",
    "Sima Yi",
    "Lu Meng",
    "Lu Xun",
    "Shir",
    "Alex",
    "Alexander",
    "Alexandra",
    "Anastasia",
    "Annastasia",
    "Emir",
    "Charlie",
    "Manfred",
    "Manfred 2.0",
    "Manfred 3.0",
    "Manfred 4.0",
    "Manfred 5.0",
    "Yukimura",
    "Keiji",
    "Tadakatsu",
    "Takanori",
    "Max",
    "Maximilian",
    "Ursula",
    "Martina",
    "Alina",
    "Leonie",
    "Leon",
    "Noel",
    "Jannik",
    "Yannik",
    "Jannic",
    "Yannic",
    "Satoshi",
    "Yamanaka",
    "Hanzo",
    "Ken",
    "Kenneth",
    "Guo Jia",
    "Chris",
    "Christian",
    "Wolfgang",
    "Maria",
    "Josef",
    "Joseph",
    "Joe",
    "Jose",
    "Donald",
    "Ronald",
    "Konrad",
    "Conrad",
    "Marcel",
    "Dominic",
    "Dominik",
    "Julia",
    "Julian",
    "Johannes",
    "Johannis",
    "Hannes",
    "Johann",
    "Johan",
    "Sebastian",
    "Bastian",
    "Sina",
    "Hektor",
    "Hector",
    "Stardust",
    "Zoom",
    "Boom",
    "Manuel",
    "Solar",
    "Lunar",
    "Luna",
    "Moon",
    "Mars",
    "Jupiter",
    "Saturn",
    "Neptune",
    "Neptun",
    "Pluto",
    "Venus",
    "Mercury",
    "Sol",
    "Zeus",
    "Athena",
    "Odin",
    "Loki",
    "Battle",
    "War",
    "Striker",
    "Smoker",
    "Dexter",
    "Ox",
    "Diamondback",
    "Snow",
    "Sand",
    "Dragon",
    "Foot",
    "Bee",
)

PLAYER_COLOR_OPTIONS = [
    "red",
    "yellow",
    "green",
    "blue",
    "purple",
    "orange",
    "cyan",
    "pink",
    "lime",
    "teal",
]
GAME_MODES = ["Untimed", "Timed", "Territory"]

