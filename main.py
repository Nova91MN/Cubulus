import json
import math
import os
import random
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

APP_VERSION = "0.3.0"

print(f"Cubulus v{APP_VERSION} Demo - Python build")

try:
    import pygame
except ImportError:
    print("pygame is not installed. Please run: pip install pygame")
    sys.exit(1)

import config


Coordinate = Tuple[int, int]
PAUSE_MENU_ITEMS = (
    "pause_continue",
    "menu_options",
    "pause_main_menu",
    "menu_quit"
)

MENU_ITEMS = (
    "menu_start",
    "menu_player_name",
    "menu_difficulty",
    "menu_mode",
    "menu_color",
    "menu_map",
    "menu_load_map",
    "menu_level_editor",
    "menu_options",
    "menu_quit"
)

OPTIONS_MENU_ITEMS = (
    "option_auto_move",
    "option_camera_zoom",
    "option_resolution",
    "option_debug",
    "option_game_speed",
    "option_language",
    "option_back"
)

LANGUAGES = ("de", "en")
TRANSLATIONS = {
    "de": {
        "status_awaiting": "Bereit zum Start",
        "status_match_running": "Match läuft",
        "menu_start": "Spiel starten",
        "menu_player_name": "Spielername",
        "menu_difficulty": "Schwierigkeit",
        "menu_mode": "Spielmodus",
        "menu_color": "Spielfarbe",
        "menu_map": "Karte",
        "menu_load_map": "Eigene Map laden",
        "menu_level_editor": "Level-Editor",
        "menu_options": "Optionen",
        "menu_quit": "Beenden",
        "pause_continue": "Fortsetzen",
        "pause_main_menu": "Hauptmenü",
        "option_auto_move": "Automatische Bewegung",
        "option_camera_zoom": "Kamera-Zoom",
        "option_resolution": "Auflösung",
        "option_debug": "Debug-Modus",
        "option_game_speed": "Spielgeschwindigkeit",
        "option_language": "Sprache",
        "option_back": "Zurück",
        "language_name": "Deutsch",
        "mode_untimed": "Endlos",
        "mode_timed": "10 Minuten",
        "mode_territory": "Territorium",
        "difficulty_beginner": "Anfänger",
        "difficulty_easy": "Leicht",
        "difficulty_normal": "Normal",
        "difficulty_hard": "Schwer",
        "difficulty_expert": "Experte",
        "difficulty_god": "Gott",
        "color_red": "Rot",
        "color_yellow": "Gelb",
        "color_green": "Grün",
        "color_blue": "Blau",
        "color_purple": "Lila",
        "color_orange": "Orange",
        "color_cyan": "Cyan",
        "color_pink": "Pink",
        "color_lime": "Limette",
        "color_teal": "Türkis",
        "menu_tagline": "TAKTISCHER GEBIETSKAMPF",
        "menu_subtitle": "Erobere das Raster. Überlebe deine Gegner.",
        "menu_controls": "↑↓ AUSWAHL     ←→ ÄNDERN     ENTER BESTÄTIGEN",
        "live_arena": "LIVE  KI-ARENA",
        "round": "RUNDE {number}",
        "arena_winner": "{name} GEWINNT",
        "draw": "UNENTSCHIEDEN",
        "options_eyebrow": "SPIELEINSTELLUNGEN",
        "options_title": "OPTIONEN",
        "options_subtitle": "Steuerung, Anzeige, Sprache und Debug-Werkzeuge.",
        "options_hint": "W/S AUSWAHL   A/D ÄNDERN   ENTER BESTÄTIGEN   ESC ZURÜCK",
        "on": "AN",
        "off": "AUS",
        "debug_off": "DEBUG AUS",
        "map_dialog_title": "Cubulus-Map auswählen",
        "map_dialog_filter": "Cubulus-Maps",
        "map_loaded": "Map geladen: {name}",
        "map_load_failed": "Map konnte nicht geladen werden: {error}",
        "game_over": "SPIELENDE",
        "victory": "SIEG",
        "player_lost": "Du hast alle 3 Leben verloren.",
        "all_eliminated": "Alle Spieler wurden eliminiert.",
        "eliminated": "{name} wurde eliminiert.",
        "lost_life": "{name} verlor ein Leben. Noch {lives}.",
        "winner": "{name} gewinnt!",
        "time_no_winner": "Zeit abgelaufen. Kein Gewinner.",
        "time_winner": "Zeit abgelaufen. {name} gewinnt!",
        "time_tie": "Zeit abgelaufen. Gleichstand zwischen: {names}",
        "territory_winner": "{name} hat das Gebietsziel erreicht!",
        "territory_reset": "{name} wurde zum Startpunkt zurückgesetzt.",
        "match_active": "MATCH LÄUFT",
        "ten_minutes": "10 MINUTEN",
        "endless": "ENDLOS",
        "territory_target": "ZIEL {percent}%",
        "infinite": "UNENDLICH",
        "pause_short": "ESC  PAUSE",
        "you": "DU",
        "territories": "GEBIETE",
        "match_paused": "MATCH ANGEHALTEN",
        "paused": "PAUSIERT",
        "mode": "MODUS",
        "lives": "LEBEN",
        "pause_hint": "W/S AUSWAHL   ENTER BESTÄTIGEN   ESC FORTSETZEN",
        "again_hint": "ENTER: Noch einmal  |  ESC: Beenden",
        "name_title": "SPIELERNAME",
        "name_hint": "Namen eingeben   ENTER SPEICHERN   ESC ABBRECHEN",
        "editor_title": "LEVEL-EDITOR",
        "editor_name": "Name",
        "editor_width": "Breite",
        "editor_height": "Höhe",
        "editor_save": "Speichern",
        "editor_clear": "Leeren",
        "editor_back": "Zurück",
        "editor_obstacle": "Hindernis",
        "editor_start": "Start {number}",
        "editor_hint": "Linksklick: Hindernis   Rechtsklick: Löschen   1–4: Startpunkt",
        "editor_keys": "N: Name   [ ]: Breite   - +: Höhe   S: Speichern   ESC: Zurück",
        "editor_saved": "Level gespeichert: {name}",
        "editor_save_failed": "Speichern fehlgeschlagen: {error}",
        "editor_start_selected": "Startpunkt {number} wählen und auf ein Feld klicken.",
        "editor_name_prompt": "Levelname eingeben",
    },
    "en": {
        "status_awaiting": "Ready to start",
        "status_match_running": "Match running",
        "menu_start": "Start game",
        "menu_player_name": "Player name",
        "menu_difficulty": "Difficulty",
        "menu_mode": "Game mode",
        "menu_color": "Player color",
        "menu_map": "Map",
        "menu_load_map": "Load custom map",
        "menu_level_editor": "Level editor",
        "menu_options": "Options",
        "menu_quit": "Quit",
        "pause_continue": "Continue",
        "pause_main_menu": "Main menu",
        "option_auto_move": "Automatic movement",
        "option_camera_zoom": "Camera zoom",
        "option_resolution": "Resolution",
        "option_debug": "Debug mode",
        "option_game_speed": "Game speed",
        "option_language": "Language",
        "option_back": "Back",
        "language_name": "English",
        "mode_untimed": "Untimed",
        "mode_timed": "10 minutes",
        "mode_territory": "Territory",
        "difficulty_beginner": "Beginner",
        "difficulty_easy": "Easy",
        "difficulty_normal": "Normal",
        "difficulty_hard": "Hard",
        "difficulty_expert": "Expert",
        "difficulty_god": "God",
        "color_red": "Red",
        "color_yellow": "Yellow",
        "color_green": "Green",
        "color_blue": "Blue",
        "color_purple": "Purple",
        "color_orange": "Orange",
        "color_cyan": "Cyan",
        "color_pink": "Pink",
        "color_lime": "Lime",
        "color_teal": "Teal",
        "menu_tagline": "TACTICAL TERRITORY COMBAT",
        "menu_subtitle": "Claim the grid. Outlast your opponents.",
        "menu_controls": "↑↓ SELECT     ←→ CHANGE     ENTER CONFIRM",
        "live_arena": "LIVE  AI ARENA",
        "round": "ROUND {number}",
        "arena_winner": "{name} WINS",
        "draw": "DRAW",
        "options_eyebrow": "GAME SETTINGS",
        "options_title": "OPTIONS",
        "options_subtitle": "Controls, display, language and debug tools.",
        "options_hint": "W/S SELECT   A/D CHANGE   ENTER CONFIRM   ESC BACK",
        "on": "ON",
        "off": "OFF",
        "debug_off": "DEBUG OFF",
        "map_dialog_title": "Select a Cubulus map",
        "map_dialog_filter": "Cubulus maps",
        "map_loaded": "Map loaded: {name}",
        "map_load_failed": "Could not load map: {error}",
        "game_over": "GAME OVER",
        "victory": "VICTORY",
        "player_lost": "You lost all 3 lives.",
        "all_eliminated": "All players were eliminated.",
        "eliminated": "{name} was eliminated.",
        "lost_life": "{name} lost a life. {lives} remaining.",
        "winner": "{name} wins!",
        "time_no_winner": "Time expired. No winner.",
        "time_winner": "Time expired. {name} wins!",
        "time_tie": "Time expired. Tie between: {names}",
        "territory_winner": "{name} reached the territory target!",
        "territory_reset": "{name} was reset to the spawn point.",
        "match_active": "MATCH ACTIVE",
        "ten_minutes": "10 MINUTES",
        "endless": "UNTIMED",
        "territory_target": "TARGET {percent}%",
        "infinite": "INFINITE",
        "pause_short": "ESC  PAUSE",
        "you": "YOU",
        "territories": "TERRITORY",
        "match_paused": "MATCH PAUSED",
        "paused": "PAUSED",
        "mode": "MODE",
        "lives": "LIVES",
        "pause_hint": "W/S SELECT   ENTER CONFIRM   ESC CONTINUE",
        "again_hint": "ENTER: Play again  |  ESC: Quit",
        "name_title": "PLAYER NAME",
        "name_hint": "Type a name   ENTER SAVE   ESC CANCEL",
        "editor_title": "LEVEL EDITOR",
        "editor_name": "Name",
        "editor_width": "Width",
        "editor_height": "Height",
        "editor_save": "Save",
        "editor_clear": "Clear",
        "editor_back": "Back",
        "editor_obstacle": "Obstacle",
        "editor_start": "Start {number}",
        "editor_hint": "Left click: obstacle   Right click: erase   1–4: start point",
        "editor_keys": "N: name   [ ]: width   - +: height   S: save   ESC: back",
        "editor_saved": "Level saved: {name}",
        "editor_save_failed": "Could not save: {error}",
        "editor_start_selected": "Choose start point {number}, then click a cell.",
        "editor_name_prompt": "Enter a level name",
    },
}

MENU_GRID_WIDTH = 44
MENU_GRID_HEIGHT = 30
MENU_BOT_STEP_MS = 82
SETTINGS_VERSION = 4
MIN_MAP_SIZE = 4
MAX_MAP_SIZE = 500


def clamp(value: int, low: int, high: int) -> int:
    """Clamp integer between low and high inclusive."""
    return max(low, min(high, value))


@dataclass
class Player:
    player_id: int
    name: str
    start_position: Coordinate
    color: str
    is_human: bool = False
    lives: int = field(default_factory=lambda: config.PLAYER_LIVES)
    position: Coordinate = field(init=False)
    alive: bool = field(init=False, default=True)
    invulnerable_until: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        self.reset(self.start_position, self.color)

    def reset(self, position: Coordinate, color: str) -> None:
        self.position = position
        self.color = color
        self.lives = config.PLAYER_LIVES
        self.alive = True
        self.invulnerable_until = 0

    def move(
        self,
        dx: int,
        dy: int,
        grid_width: int,
        grid_height: int
    ) -> None:
        if not self.alive:
            return

        x, y = self.position

        x = clamp(x + dx, 0, grid_width - 1)
        y = clamp(y + dy, 0, grid_height - 1)

        self.position = (x, y)

    def take_damage(self, current_ticks: int) -> bool:
        """Remove exactly one life when the damage cooldown has expired."""

        if not self.alive or current_ticks < self.invulnerable_until:
            return False

        self.lives = max(0, self.lives - 1)
        self.invulnerable_until = (
            current_ticks + config.DAMAGE_COOLDOWN_MS
        )

        if self.lives == 0:
            self.alive = False

        return True


class CubulusGame:
    def __init__(self) -> None:
        pygame.init()

        self.settings_path = self.get_settings_path()
        saved_settings = self.load_settings()
        saved_language = saved_settings.get("language")
        self.language = (
            saved_language if saved_language in LANGUAGES else "de"
        )

        saved_resolution = saved_settings.get("resolution")
        initial_resolution = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        if (
            isinstance(saved_resolution, list)
            and len(saved_resolution) == 2
            and all(
                isinstance(value, int) and not isinstance(value, bool)
                for value in saved_resolution
            )
            and 800 <= saved_resolution[0] <= 3840
            and 600 <= saved_resolution[1] <= 2160
        ):
            initial_resolution = tuple(saved_resolution)

        self.resolution_index = min(
            range(len(config.RESOLUTION_OPTIONS)),
            key=lambda index: (
                abs(config.RESOLUTION_OPTIONS[index][0] - initial_resolution[0])
                + abs(config.RESOLUTION_OPTIONS[index][1] - initial_resolution[1])
            )
        )

        self.screen = pygame.display.set_mode(
            initial_resolution,
            pygame.RESIZABLE
        )

        pygame.display.set_caption(f"Cubulus v{APP_VERSION} Demo")

        self.clock = pygame.time.Clock()

        self.primary_font = pygame.font.SysFont(
            "consolas",
            18
        )

        self.title_font = pygame.font.SysFont(
            "segoeui",
            30,
            bold=True
        )

        self.menu_title_font = pygame.font.SysFont(
            "segoeui",
            72,
            bold=True
        )

        self.menu_heading_font = pygame.font.SysFont(
            "segoeui",
            22,
            bold=True
        )

        self.menu_button_font = pygame.font.SysFont(
            "segoeui",
            20,
            bold=True
        )

        self.hud_font = pygame.font.SysFont(
            "segoeui",
            30,
            bold=True
        )

        self.small_font = pygame.font.SysFont(
            "segoeui",
            16
        )

        self.game_over_font = pygame.font.SysFont(
            "segoeui",
            64,
            bold=True
        )

        self.running = True
        self.state = "menu"

        self.mode_index = self.valid_saved_index(
            saved_settings.get("game_mode_index"),
            len(config.GAME_MODES)
        )
        self.color_index = self.valid_saved_index(
            saved_settings.get("player_color_index"),
            len(config.PLAYER_COLOR_OPTIONS)
        )
        saved_difficulty_name = saved_settings.get("difficulty")
        saved_difficulty_index = saved_settings.get("difficulty_index")
        if saved_difficulty_name in config.DIFFICULTY_LEVELS:
            self.difficulty_index = config.DIFFICULTY_LEVELS.index(
                saved_difficulty_name
            )
        elif (
            isinstance(saved_difficulty_index, int)
            and not isinstance(saved_difficulty_index, bool)
        ):
            # Versions through 0.2.0 stored only the index of
            # Easy/Normal/Hard. Preserve its meaning after inserting Beginner.
            legacy_levels = ("Easy", "Normal", "Hard")
            saved_version = saved_settings.get("version", 0)
            legacy_settings = (
                not isinstance(saved_version, int)
                or isinstance(saved_version, bool)
                or saved_version < SETTINGS_VERSION
            )
            if legacy_settings and 0 <= saved_difficulty_index < 3:
                legacy_name = legacy_levels[saved_difficulty_index]
                self.difficulty_index = config.DIFFICULTY_LEVELS.index(legacy_name)
            elif 0 <= saved_difficulty_index < len(config.DIFFICULTY_LEVELS):
                self.difficulty_index = saved_difficulty_index
            else:
                self.difficulty_index = config.DIFFICULTY_LEVELS.index("Normal")
        else:
            self.difficulty_index = config.DIFFICULTY_LEVELS.index("Normal")
        self.player_name = self.sanitize_player_name(
            saved_settings.get("player_name", config.PLAYER_NAMES[0])
        )

        self.status_message = self.t("status_awaiting")

        self.board: List[List[str]] = []
        self.players: List[Player] = []

        self.territory_counts: Dict[int, int] = {}

        saved_map_path = saved_settings.get("map_path")
        extra_map_path = (
            Path(saved_map_path).expanduser()
            if isinstance(saved_map_path, str) and saved_map_path
            else None
        )
        self.available_maps = self.discover_maps(extra_map_path)
        if not self.available_maps:
            raise SystemExit("No valid Cubulus maps were found.")
        self.map_index = 0
        if extra_map_path is not None:
            selected_path = extra_map_path.resolve(strict=False)
            for index, (path, _) in enumerate(self.available_maps):
                if path.resolve(strict=False) == selected_path:
                    self.map_index = index
                    break
        self.map_path, self.map_data = self.available_maps[self.map_index]
        self.map_notice = ""
        self.map_notice_until = 0

        self.match_start_ticks: Optional[int] = None
        self.damage_flash_until = 0
        self.game_over_title = self.t("game_over")
        self.game_over_color = config.COLORS["white"]

        # Camera coordinates are expressed in cells. Keeping world and screen
        # units separate makes zooming smooth and leaves gameplay untouched.
        self.camera_x = 0.5
        self.camera_y = 0.5
        saved_zoom = saved_settings.get("camera_zoom")
        self.preferred_camera_zoom = (
            max(config.CAMERA_MIN_ZOOM, min(config.CAMERA_MAX_ZOOM, saved_zoom))
            if isinstance(saved_zoom, (int, float))
            and not isinstance(saved_zoom, bool)
            else config.CAMERA_START_ZOOM
        )
        self.camera_zoom = self.preferred_camera_zoom
        self.camera_target_zoom = self.preferred_camera_zoom
        self.frame_dt = 1.0 / config.FPS
        self.game_ticks_ms = 0.0
        self.simulation_accumulator = 0.0

        self.pause_selection = 0
        self.pause_view = "main"
        self.pause_started_ticks: Optional[int] = None
        self.pause_item_rects: List[pygame.Rect] = []
        self.pause_background: Optional[pygame.Surface] = None

        self.menu_selection = 0
        self.menu_view = "main"
        self.menu_item_rects: List[pygame.Rect] = []
        self.options_selection = 0
        self.options_item_rects: List[pygame.Rect] = []
        self.name_draft = self.player_name
        saved_auto_movement = saved_settings.get("auto_movement_enabled")
        self.auto_movement_enabled = (
            saved_auto_movement
            if isinstance(saved_auto_movement, bool)
            else True
        )
        saved_debug_mode = saved_settings.get("debug_mode")
        self.debug_mode = (
            saved_debug_mode
            if isinstance(saved_debug_mode, bool)
            else False
        )
        saved_game_speed = saved_settings.get("game_speed")
        self.game_speed_index = (
            config.DEBUG_SPEED_OPTIONS.index(float(saved_game_speed))
            if isinstance(saved_game_speed, (int, float))
            and not isinstance(saved_game_speed, bool)
            and float(saved_game_speed) in config.DEBUG_SPEED_OPTIONS
            else config.DEBUG_SPEED_OPTIONS.index(1.0)
        )
        self.human_move_direction: Optional[Coordinate] = None
        self.human_last_move_ticks = 0
        self.menu_board: List[List[str]] = []
        self.menu_players: List[Player] = []
        self.menu_last_step_ticks = 0
        self.menu_round = 0
        self.menu_round_reset_at: Optional[int] = None
        self.menu_battle_message = self.t("round", number=1)
        self.menu_battle_message_until = 0
        self.menu_clash_position: Optional[Coordinate] = None
        self.menu_clash_until = 0

        self.editor_name = self.t("editor_name_prompt")
        self.editor_name_draft = self.editor_name
        self.editor_width = 30
        self.editor_height = 20
        self.editor_starts: List[Coordinate] = []
        self.editor_obstacles: Set[Coordinate] = set()
        self.editor_selected_start: Optional[int] = None
        self.editor_editing_name = False
        self.editor_grid_rect = pygame.Rect(0, 0, 0, 0)
        self.editor_cell_size = 1.0
        self.editor_button_rects: Dict[str, pygame.Rect] = {}
        self.editor_notice = ""
        self.editor_notice_until = 0
        self.editor_saved_path: Optional[Path] = None
        self.reset_editor_starts()
        self.reset_menu_battle()

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def t(self, key: str, **values: object) -> str:
        """Return a translated UI string for the active language."""

        language_strings = TRANSLATIONS.get(
            self.language,
            TRANSLATIONS["de"]
        )
        template = language_strings.get(
            key,
            TRANSLATIONS["de"].get(key, key)
        )
        return template.format(**values)

    def current_mode(self) -> str:
        return config.GAME_MODES[getattr(self, "mode_index", 0)]

    def current_difficulty(self) -> str:
        default = config.DIFFICULTY_LEVELS.index("Normal")
        return config.DIFFICULTY_LEVELS[
            getattr(self, "difficulty_index", default)
        ]

    def is_territory_mode(self) -> bool:
        return self.current_mode() == "Territory"

    def god_alliance_active(self) -> bool:
        return self.current_difficulty() == "God"

    def territory_win_fraction(self) -> float:
        return config.TERRITORY_WIN_PERCENTAGES[self.current_difficulty()]

    def territory_target_tiles(self) -> int:
        playable_tiles = sum(
            tile != "obstacle"
            for row in self.board
            for tile in row
        )
        return max(1, math.ceil(playable_tiles * self.territory_win_fraction()))

    def territory_target_percent(self) -> str:
        percentage = self.territory_win_fraction() * 100
        return f"{percentage:g}"

    def mode_display_label(self) -> str:
        mode_keys = {
            "Untimed": "mode_untimed",
            "Timed": "mode_timed",
            "Territory": "mode_territory",
        }
        mode = self.current_mode()
        return self.t(mode_keys.get(mode, mode))

    @staticmethod
    def get_settings_path() -> Path:
        """Return a per-user path that also works for packaged builds."""

        override = os.environ.get("CUBULUS_SETTINGS_PATH")
        if override:
            return Path(override).expanduser()

        if sys.platform == "win32":
            base_dir = Path(os.environ.get("APPDATA", Path.home()))
            return base_dir / "Cubulus" / "settings.json"

        base_dir = Path(
            os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        )
        return base_dir / "cubulus" / "settings.json"

    @staticmethod
    def valid_saved_index(value: object, item_count: int) -> int:
        if isinstance(value, int) and not isinstance(value, bool):
            if 0 <= value < item_count:
                return value
        return 0

    @staticmethod
    def sanitize_player_name(value: object) -> str:
        """Return a short, printable player name suitable for the HUD."""

        if not isinstance(value, str):
            return config.PLAYER_NAMES[0]
        cleaned = "".join(character for character in value if character.isprintable())
        cleaned = " ".join(cleaned.split()).strip()
        return cleaned[:16] or config.PLAYER_NAMES[0]

    def load_settings(self) -> Dict:
        try:
            with open(self.settings_path, "r", encoding="utf-8") as handle:
                settings = json.load(handle)
            if isinstance(settings, dict):
                return settings
            print("Ignoring settings: expected a JSON object.")
        except FileNotFoundError:
            pass
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not load settings: {exc}")
        return {}

    def save_settings(self) -> None:
        """Persist menu and gameplay preferences using an atomic replace."""

        settings = {
            "version": SETTINGS_VERSION,
            "auto_movement_enabled": self.auto_movement_enabled,
            "camera_zoom": round(self.preferred_camera_zoom, 2),
            "resolution": list(self.screen.get_size()),
            "debug_mode": self.debug_mode,
            "game_speed": config.DEBUG_SPEED_OPTIONS[self.game_speed_index],
            "game_mode_index": self.mode_index,
            "player_color_index": self.color_index,
            "difficulty_index": self.difficulty_index,
            "difficulty": self.current_difficulty(),
            "player_name": self.player_name,
            "language": self.language,
            "map_path": str(self.map_path),
        }

        temporary_path = self.settings_path.with_suffix(".tmp")
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temporary_path, "w", encoding="utf-8") as handle:
                json.dump(settings, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            temporary_path.replace(self.settings_path)
        except OSError as exc:
            print(f"Could not save settings: {exc}")

    def apply_resolution(
        self,
        resolution: Tuple[int, int],
        save: bool = True
    ) -> None:
        self.screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
        if resolution in config.RESOLUTION_OPTIONS:
            self.resolution_index = config.RESOLUTION_OPTIONS.index(resolution)
        if save:
            self.save_settings()

    def handle_resize(self, size: Tuple[int, int]) -> None:
        """Keep manual window resizing and persisted resolution in sync."""

        width = max(800, int(size[0]))
        height = max(600, int(size[1]))
        self.resolution_index = min(
            range(len(config.RESOLUTION_OPTIONS)),
            key=lambda index: (
                abs(config.RESOLUTION_OPTIONS[index][0] - width)
                + abs(config.RESOLUTION_OPTIONS[index][1] - height)
            )
        )
        self.apply_resolution((width, height), save=False)

    def game_ticks(self) -> int:
        return int(self.game_ticks_ms)

    def effective_game_speed(self) -> float:
        if not self.debug_mode:
            return 1.0
        return config.DEBUG_SPEED_OPTIONS[self.game_speed_index]

    @staticmethod
    def load_map_file(map_path: Path) -> Dict:
        """Read and validate a map without modifying the active match."""

        try:
            with open(map_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except FileNotFoundError as exc:
            raise ValueError(f"file not found: {map_path}") from exc
        except OSError as exc:
            raise ValueError(str(exc)) from exc
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"invalid JSON at line {exc.lineno}, column {exc.colno}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError("the root value must be a JSON object")

        width = data.get("width")
        height = data.get("height")
        for label, value in (("width", width), ("height", height)):
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"'{label}' must be an integer")
            if not MIN_MAP_SIZE <= value <= MAX_MAP_SIZE:
                raise ValueError(
                    f"'{label}' must be between {MIN_MAP_SIZE} and "
                    f"{MAX_MAP_SIZE}"
                )

        name = data.get("name", map_path.stem)
        if not isinstance(name, str) or not name.strip():
            raise ValueError("'name' must be a non-empty string")
        name = name.strip()[:64]

        default_starts = [
            [0, 0],
            [width - 1, 0],
            [0, height - 1],
            [width - 1, height - 1],
        ]
        raw_starts = data.get("player_starts", default_starts)
        if isinstance(raw_starts, dict):
            raw_starts = [
                raw_starts.get(str(player_id), raw_starts.get(player_id))
                for player_id in range(4)
            ]
        if not isinstance(raw_starts, list) or len(raw_starts) != 4:
            raise ValueError("'player_starts' must contain exactly 4 positions")

        player_starts: List[List[int]] = []
        for player_id, position in enumerate(raw_starts):
            if (
                not isinstance(position, (list, tuple))
                or len(position) != 2
                or not all(
                    isinstance(value, int) and not isinstance(value, bool)
                    for value in position
                )
            ):
                raise ValueError(
                    f"player start {player_id} must be an [x, y] integer pair"
                )
            x, y = position
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(
                    f"player start {player_id} is outside the map"
                )
            player_starts.append([x, y])

        if len({tuple(position) for position in player_starts}) != 4:
            raise ValueError("player starts must be unique")

        raw_obstacles = data.get("obstacles", [])
        if not isinstance(raw_obstacles, list):
            raise ValueError("'obstacles' must be a list of [x, y] positions")

        obstacles: List[List[int]] = []
        occupied = {tuple(position) for position in player_starts}
        for index, position in enumerate(raw_obstacles):
            if (
                not isinstance(position, (list, tuple))
                or len(position) != 2
                or not all(
                    isinstance(value, int) and not isinstance(value, bool)
                    for value in position
                )
            ):
                raise ValueError(f"obstacle {index} must be an [x, y] integer pair")
            x, y = position
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"obstacle {index} is outside the map")
            if (x, y) in occupied:
                raise ValueError(f"obstacle {index} overlaps a player start")
            if [x, y] not in obstacles:
                obstacles.append([x, y])

        normalized = dict(data)
        normalized.update({
            "name": name,
            "width": width,
            "height": height,
            "player_starts": player_starts,
            "obstacles": obstacles,
        })
        print(f"Loaded map: {name} ({width} x {height})")
        return normalized

    def discover_maps(
        self,
        extra_path: Optional[Path] = None
    ) -> List[Tuple[Path, Dict]]:
        """Find valid bundled maps plus a previously selected custom map."""

        bundled_map_dir = Path(__file__).resolve().parent / "maps"
        user_map_dir = self.settings_path.parent / "maps"
        candidates = sorted(
            list(bundled_map_dir.glob("*.json"))
            + list(user_map_dir.glob("*.json")),
            key=lambda path: (path.name != "default.json", path.name.lower())
        )
        if extra_path is not None:
            extra_resolved = extra_path.resolve(strict=False)
            if all(
                path.resolve(strict=False) != extra_resolved
                for path in candidates
            ):
                candidates.append(extra_path)

        maps: List[Tuple[Path, Dict]] = []
        for path in candidates:
            try:
                maps.append((path, self.load_map_file(path)))
            except ValueError as exc:
                print(f"Skipping invalid map '{path}': {exc}")
        return maps

    def cycle_map(self, direction: int) -> None:
        if not self.available_maps:
            return
        self.map_index = (
            self.map_index + direction
        ) % len(self.available_maps)
        self.map_path, self.map_data = self.available_maps[self.map_index]
        self.map_notice = self.t(
            "map_loaded",
            name=self.map_data["name"]
        )
        self.map_notice_until = pygame.time.get_ticks() + 2200
        self.save_settings()

    def choose_custom_map(self) -> None:
        """Open a native file picker and activate a validated JSON map."""

        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            selected = filedialog.askopenfilename(
                parent=root,
                title=self.t("map_dialog_title"),
                filetypes=(
                    (self.t("map_dialog_filter"), "*.json"),
                    ("JSON", "*.json"),
                )
            )
            root.destroy()
        except Exception as exc:
            selected = ""
            self.map_notice = self.t("map_load_failed", error=str(exc))
            self.map_notice_until = pygame.time.get_ticks() + 5000

        if not selected:
            return

        path = Path(selected)
        try:
            data = self.load_map_file(path)
        except ValueError as exc:
            self.map_notice = self.t("map_load_failed", error=str(exc))
            self.map_notice_until = pygame.time.get_ticks() + 5000
            print(self.map_notice)
            return

        resolved = path.resolve(strict=False)
        for index, (known_path, _) in enumerate(self.available_maps):
            if known_path.resolve(strict=False) == resolved:
                self.available_maps[index] = (path, data)
                self.map_index = index
                break
        else:
            self.available_maps.append((path, data))
            self.map_index = len(self.available_maps) - 1

        self.map_path, self.map_data = self.available_maps[self.map_index]
        self.map_notice = self.t("map_loaded", name=data["name"])
        self.map_notice_until = pygame.time.get_ticks() + 3500
        self.save_settings()

    # ------------------------------------------------------------------
    # Level editor
    # ------------------------------------------------------------------

    def reset_editor_starts(self) -> None:
        """Place four valid starts in the editor's corners."""

        self.editor_starts = [
            (0, 0),
            (self.editor_width - 1, 0),
            (0, self.editor_height - 1),
            (self.editor_width - 1, self.editor_height - 1),
        ]
        self.editor_obstacles.difference_update(self.editor_starts)

    def start_level_editor(self) -> None:
        """Open a fresh, playable level editor canvas."""

        self.editor_name = "Mein Level" if self.language == "de" else "My Level"
        self.editor_name_draft = self.editor_name
        self.editor_width = 30
        self.editor_height = 20
        self.editor_obstacles = set()
        self.editor_selected_start = None
        self.editor_editing_name = False
        self.editor_saved_path = None
        self.editor_notice = ""
        self.reset_editor_starts()
        self.state = "editor"

    def resize_editor(self, width_delta: int, height_delta: int) -> None:
        new_width = clamp(
            self.editor_width + width_delta,
            MIN_MAP_SIZE,
            MAX_MAP_SIZE
        )
        new_height = clamp(
            self.editor_height + height_delta,
            MIN_MAP_SIZE,
            MAX_MAP_SIZE
        )
        if (new_width, new_height) == (self.editor_width, self.editor_height):
            return
        self.editor_width = new_width
        self.editor_height = new_height
        self.editor_obstacles = {
            (x, y)
            for x, y in self.editor_obstacles
            if x < new_width and y < new_height
        }
        self.reset_editor_starts()

    def editor_map_data(self) -> Dict:
        return {
            "name": self.editor_name.strip()[:64] or "Custom Level",
            "width": self.editor_width,
            "height": self.editor_height,
            "player_starts": [list(position) for position in self.editor_starts],
            "obstacles": [
                [x, y]
                for x, y in sorted(
                    self.editor_obstacles,
                    key=lambda position: (position[1], position[0])
                )
            ],
        }

    def save_editor_level(self) -> None:
        """Save the edited level and immediately select it in the menu."""

        data = self.editor_map_data()
        user_map_dir = self.settings_path.parent / "maps"
        slug = re.sub(r"[^a-z0-9_-]+", "-", data["name"].lower()).strip("-_")
        slug = slug or "custom-level"

        path = self.editor_saved_path
        if path is None:
            path = user_map_dir / f"{slug}.json"
            suffix = 2
            while path.exists():
                path = user_map_dir / f"{slug}-{suffix}.json"
                suffix += 1

        temporary_path = path.with_suffix(".tmp")
        try:
            user_map_dir.mkdir(parents=True, exist_ok=True)
            with open(temporary_path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            temporary_path.replace(path)
            normalized = self.load_map_file(path)
        except (OSError, ValueError) as exc:
            self.editor_notice = self.t("editor_save_failed", error=str(exc))
            self.editor_notice_until = pygame.time.get_ticks() + 5000
            return

        self.editor_saved_path = path
        resolved = path.resolve(strict=False)
        for index, (known_path, _) in enumerate(self.available_maps):
            if known_path.resolve(strict=False) == resolved:
                self.available_maps[index] = (path, normalized)
                self.map_index = index
                break
        else:
            self.available_maps.append((path, normalized))
            self.map_index = len(self.available_maps) - 1
        self.map_path, self.map_data = self.available_maps[self.map_index]
        self.editor_notice = self.t("editor_saved", name=normalized["name"])
        self.editor_notice_until = pygame.time.get_ticks() + 3500
        self.map_notice = self.editor_notice
        self.map_notice_until = self.editor_notice_until
        self.save_settings()

    def editor_cell_at(self, position: Coordinate) -> Optional[Coordinate]:
        if not self.editor_grid_rect.collidepoint(position):
            return None
        x = int((position[0] - self.editor_grid_rect.x) / self.editor_cell_size)
        y = int((position[1] - self.editor_grid_rect.y) / self.editor_cell_size)
        if 0 <= x < self.editor_width and 0 <= y < self.editor_height:
            return x, y
        return None

    def begin_editor_name_entry(self) -> None:
        self.editor_name_draft = self.editor_name
        self.editor_editing_name = True
        pygame.key.start_text_input()

    def activate_editor_button(self, button: str) -> None:
        if button == "name":
            self.begin_editor_name_entry()
        elif button == "width_down":
            self.resize_editor(-1, 0)
        elif button == "width_up":
            self.resize_editor(1, 0)
        elif button == "height_down":
            self.resize_editor(0, -1)
        elif button == "height_up":
            self.resize_editor(0, 1)
        elif button == "save":
            self.save_editor_level()
        elif button == "clear":
            self.editor_obstacles.clear()
        elif button == "back":
            self.state = "menu"
            self.menu_selection = 0

    def handle_editor_click(self, position: Coordinate, button: int) -> None:
        if button == 1:
            for key, rect in self.editor_button_rects.items():
                if rect.collidepoint(position):
                    self.activate_editor_button(key)
                    return

        cell = self.editor_cell_at(position)
        if cell is None:
            return
        if button == 3:
            self.editor_obstacles.discard(cell)
            return
        if button != 1:
            return

        if self.editor_selected_start is not None:
            if cell not in self.editor_starts:
                self.editor_starts[self.editor_selected_start] = cell
                self.editor_obstacles.discard(cell)
            self.editor_selected_start = None
            return

        if cell in self.editor_starts:
            return
        if cell in self.editor_obstacles:
            self.editor_obstacles.remove(cell)
        else:
            self.editor_obstacles.add(cell)

    def editor_loop(self) -> None:
        while self.state == "editor" and self.running:
            self.clock.tick(config.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.size)
                    continue
                if event.type == pygame.TEXTINPUT and self.editor_editing_name:
                    printable = "".join(
                        character for character in event.text
                        if character.isprintable()
                    )
                    self.editor_name_draft = (
                        self.editor_name_draft + printable
                    )[:32]
                    continue
                if event.type == pygame.KEYDOWN:
                    if self.editor_editing_name:
                        if event.key == pygame.K_ESCAPE:
                            self.editor_editing_name = False
                            pygame.key.stop_text_input()
                        elif event.key == pygame.K_BACKSPACE:
                            self.editor_name_draft = self.editor_name_draft[:-1]
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            candidate = " ".join(self.editor_name_draft.split())
                            if candidate:
                                self.editor_name = candidate[:64]
                            self.editor_editing_name = False
                            pygame.key.stop_text_input()
                        continue

                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                        self.menu_selection = 0
                        return
                    if event.key == pygame.K_n:
                        self.begin_editor_name_entry()
                    elif event.key == pygame.K_s:
                        self.save_editor_level()
                    elif event.key == pygame.K_c:
                        self.editor_obstacles.clear()
                    elif event.key == pygame.K_LEFTBRACKET:
                        self.resize_editor(-1, 0)
                    elif event.key == pygame.K_RIGHTBRACKET:
                        self.resize_editor(1, 0)
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        self.resize_editor(0, -1)
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                        self.resize_editor(0, 1)
                    elif pygame.K_1 <= event.key <= pygame.K_4:
                        self.editor_selected_start = event.key - pygame.K_1
                        self.editor_notice = self.t(
                            "editor_start_selected",
                            number=self.editor_selected_start + 1
                        )
                        self.editor_notice_until = pygame.time.get_ticks() + 3000
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_editor_click(event.pos, event.button)

            self.draw_editor()

    def draw_editor(self) -> None:
        width, height = self.screen.get_size()
        self.screen.fill((6, 9, 15))

        title = self.title_font.render(self.t("editor_title"), True, (248, 250, 255))
        self.screen.blit(title, (24, 20))
        subtitle = self.small_font.render(
            f"{self.editor_name}  ·  {self.editor_width} × {self.editor_height}",
            True,
            (113, 183, 255)
        )
        self.screen.blit(subtitle, (26, 61))

        sidebar_width = min(265, max(220, width // 4))
        grid_area = pygame.Rect(24, 96, width - sidebar_width - 64, height - 160)
        cell_size = max(
            1.0,
            min(
                grid_area.width / self.editor_width,
                grid_area.height / self.editor_height
            )
        )
        grid_width = cell_size * self.editor_width
        grid_height = cell_size * self.editor_height
        self.editor_grid_rect = pygame.Rect(
            round(grid_area.centerx - grid_width / 2),
            round(grid_area.centery - grid_height / 2),
            max(1, round(grid_width)),
            max(1, round(grid_height))
        )
        self.editor_cell_size = cell_size

        for y in range(self.editor_height):
            for x in range(self.editor_width):
                rect = pygame.Rect(
                    round(self.editor_grid_rect.x + x * cell_size),
                    round(self.editor_grid_rect.y + y * cell_size),
                    max(1, math.ceil(cell_size) - 1),
                    max(1, math.ceil(cell_size) - 1)
                )
                color = (
                    config.COLORS["obstacle"]
                    if (x, y) in self.editor_obstacles
                    else (17, 24, 34)
                )
                pygame.draw.rect(self.screen, color, rect, border_radius=2)
                if (x, y) in self.editor_obstacles and cell_size >= 10:
                    pygame.draw.line(self.screen, (116, 128, 145), rect.topleft, rect.bottomright, 2)
                    pygame.draw.line(self.screen, (116, 128, 145), rect.topright, rect.bottomleft, 2)

        for index, position in enumerate(self.editor_starts):
            x, y = position
            rect = pygame.Rect(
                round(self.editor_grid_rect.x + x * cell_size),
                round(self.editor_grid_rect.y + y * cell_size),
                max(2, math.ceil(cell_size) - 1),
                max(2, math.ceil(cell_size) - 1)
            )
            color_name = config.PLAYER_COLOR_OPTIONS[index]
            pygame.draw.rect(self.screen, config.COLORS[color_name], rect, border_radius=2)
            if cell_size >= 13:
                number = self.small_font.render(str(index + 1), True, (255, 255, 255))
                self.screen.blit(number, number.get_rect(center=rect.center))

        side_rect = pygame.Rect(width - sidebar_width - 24, 96, sidebar_width, height - 160)
        self.draw_glass_panel(side_rect, fill=(7, 12, 20, 226))
        self.editor_button_rects = {}
        button_specs = (
            ("name", f"{self.t('editor_name')}: {self.editor_name[:15]}"),
            ("width_down", f"− {self.t('editor_width')}"),
            ("width_up", f"+ {self.t('editor_width')}"),
            ("height_down", f"− {self.t('editor_height')}"),
            ("height_up", f"+ {self.t('editor_height')}"),
            ("save", self.t("editor_save")),
            ("clear", self.t("editor_clear")),
            ("back", self.t("editor_back")),
        )
        button_height = max(31, min(43, (side_rect.height - 64) // len(button_specs) - 5))
        button_gap = 5
        y = side_rect.y + 22
        for key, label_text in button_specs:
            rect = pygame.Rect(side_rect.x + 18, y, side_rect.width - 36, button_height)
            self.editor_button_rects[key] = rect
            accent = key == "save"
            pygame.draw.rect(
                self.screen,
                (25, 51, 72) if accent else (16, 24, 36),
                rect,
                border_radius=10
            )
            pygame.draw.rect(
                self.screen,
                (83, 166, 255) if accent else (67, 81, 101),
                rect,
                1,
                border_radius=10
            )
            label = self.small_font.render(label_text, True, (225, 231, 240))
            self.screen.blit(label, label.get_rect(center=rect.center))
            y += button_height + button_gap

        notice = (
            self.editor_notice
            if pygame.time.get_ticks() < self.editor_notice_until
            else self.t("editor_hint")
        )
        hint = self.small_font.render(notice, True, (165, 177, 194))
        self.screen.blit(hint, (24, height - 51))
        keys = self.small_font.render(self.t("editor_keys"), True, (126, 140, 159))
        self.screen.blit(keys, (24, height - 28))

        if self.editor_editing_name:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((2, 6, 12, 180))
            self.screen.blit(overlay, (0, 0))
            dialog = pygame.Rect(0, 0, min(560, width - 60), 230)
            dialog.center = (width // 2, height // 2)
            self.draw_glass_panel(dialog, fill=(7, 12, 20, 248))
            prompt = self.menu_heading_font.render(
                self.t("editor_name_prompt"),
                True,
                (248, 250, 255)
            )
            self.screen.blit(prompt, prompt.get_rect(center=(dialog.centerx, dialog.y + 48)))
            field = pygame.Rect(dialog.x + 35, dialog.y + 85, dialog.width - 70, 58)
            pygame.draw.rect(self.screen, (18, 28, 42), field, border_radius=10)
            pygame.draw.rect(self.screen, (83, 166, 255), field, 2, border_radius=10)
            value = self.menu_heading_font.render(self.editor_name_draft, True, (244, 247, 252))
            self.screen.blit(value, (field.x + 15, field.centery - value.get_height() // 2))
            name_hint = self.small_font.render(self.t("name_hint"), True, (126, 140, 159))
            self.screen.blit(name_hint, name_hint.get_rect(center=(dialog.centerx, dialog.bottom - 39)))

        pygame.display.flip()

    def reset_board(self) -> None:

        width = self.map_data["width"]
        height = self.map_data["height"]

        self.board = [
            [
                "neutral"
                for _ in range(width)
            ]
            for _ in range(height)
        ]

        neutral_cells = self.map_data.get(
            "neutral",
            []
        )

        for cell in neutral_cells:

            if isinstance(cell, dict):

                x = cell.get("x")
                y = cell.get("y")

            else:

                try:
                    x, y = cell

                except (TypeError, ValueError):
                    continue

            if x is None or y is None:
                continue

            if (
                0 <= x < width
                and
                0 <= y < height
            ):
                self.board[y][x] = "neutral"

        for x, y in self.map_data.get("obstacles", []):
            self.board[y][x] = "obstacle"

    def create_players(self) -> None:

        self.players = []
        bot_names = random.sample(config.BOT_NAMES, 3)

        selected_color = (
            config.PLAYER_COLOR_OPTIONS[
                self.color_index
            ]
        )

        available_colors = [
            c
            for c in config.PLAYER_COLOR_OPTIONS
            if c != selected_color
        ]

        for pid in range(4):

            color = (
                selected_color
                if pid == 0
                else (
                    available_colors[pid - 1]
                    if pid - 1 < len(available_colors)
                    else random.choice(
                        config.PLAYER_COLOR_OPTIONS
                    )
                )
            )

            player = Player(
                player_id=pid,

                name=(
                    getattr(self, "player_name", config.PLAYER_NAMES[0])
                    if pid == 0
                    else bot_names[pid - 1]
                ),

                start_position=tuple(
                    self.map_data["player_starts"][pid]
                ),

                color=color,

                is_human=(pid == 0),
            )

            self.players.append(player)

    def apply_tile_effect(
        self,
        player: Player
    ) -> None:

        x, y = player.position

        current = self.board[y][x]

        if current == "neutral" or (
            self.is_territory_mode()
            and current != "obstacle"
        ):

            self.board[y][x] = player.color

    def try_move_player(self, player: Player, dx: int, dy: int) -> bool:
        """Move a player unless the destination contains an obstacle."""

        if not player.alive or not self.board:
            return False
        grid_height = len(self.board)
        grid_width = len(self.board[0])
        x, y = player.position
        destination = (
            clamp(x + dx, 0, grid_width - 1),
            clamp(y + dy, 0, grid_height - 1),
        )
        if destination == player.position:
            return False
        target_x, target_y = destination
        if self.board[target_y][target_x] == "obstacle":
            return False
        player.position = destination
        self.apply_tile_effect(player)
        return True

    def compute_territories(
        self
    ) -> Dict[int, int]:

        counts: Dict[int, int] = {
            player.player_id: 0
            for player in self.players
        }

        color_to_players: Dict[
            str,
            List[int]
        ] = {}

        for player in self.players:

            color_to_players.setdefault(
                player.color,
                []
            ).append(
                player.player_id
            )

        for row in self.board:

            for tile_color in row:

                ids = color_to_players.get(
                    tile_color,
                    []
                )

                for pid in ids:
                    counts[pid] += 1

        return counts

    def alive_players(
        self
    ) -> List[Player]:

        return [
            player
            for player in self.players
            if player.alive
        ]

    def start_match(self) -> None:

        mode = config.GAME_MODES[
            self.mode_index
        ]

        player_color = (
            config.PLAYER_COLOR_OPTIONS[
                self.color_index
            ]
        )

        print(
            f"Starting match in "
            f"{mode} mode as "
            f"{player_color}."
        )

        self.reset_board()

        self.create_players()

        for player in self.players:
            self.apply_tile_effect(player)

        self.territory_counts = self.compute_territories()

        human_x, human_y = self.players[0].position
        self.camera_x = human_x + 0.5
        self.camera_y = human_y + 0.5
        self.camera_zoom = self.preferred_camera_zoom
        self.camera_target_zoom = self.preferred_camera_zoom
        self.damage_flash_until = 0
        self.game_over_title = self.t("game_over")
        self.game_over_color = config.COLORS["white"]
        self.pause_selection = 0
        self.pause_view = "main"
        self.pause_started_ticks = None
        self.pause_background = None
        self.human_move_direction = None
        self.game_ticks_ms = 0.0
        self.simulation_accumulator = 0.0
        self.human_last_move_ticks = self.game_ticks()
        self.match_start_ticks = self.game_ticks()

        self.status_message = self.t("status_match_running")

        self.state = "playing"

    def end_match(
        self,
        message: str,
        title: Optional[str] = None,
        color: Optional[Tuple[int, int, int]] = None
    ) -> None:

        print(message)

        self.status_message = message
        self.game_over_title = title or self.t("game_over")
        self.game_over_color = color or config.COLORS["white"]

        self.state = "game_over"

        self.match_start_ticks = None

    def pause_match(self) -> None:

        if self.state != "playing":
            return

        self.pause_started_ticks = pygame.time.get_ticks()
        self.pause_selection = 0
        self.pause_view = "main"
        self.options_selection = 0
        self.pause_background = self.screen.copy()
        self.state = "paused"

    def resume_match(self) -> None:

        if self.state != "paused":
            return

        # The simulation clock advances only during gameplay, so all match
        # timers and cooldowns remain frozen without shifting deadlines.
        self.pause_started_ticks = None
        self.pause_background = None
        self.state = "playing"

    def return_to_main_menu(self) -> None:

        self.state = "menu"
        self.match_start_ticks = None
        self.pause_started_ticks = None
        self.pause_background = None
        self.menu_view = "main"
        self.menu_selection = 0
        self.status_message = self.t("status_awaiting")
        self.reset_menu_battle()

    def reset_menu_battle(self) -> None:
        """Start a fresh, self-contained AI battle behind the main menu."""

        self.menu_round += 1
        self.menu_board = [
            ["neutral" for _ in range(MENU_GRID_WIDTH)]
            for _ in range(MENU_GRID_HEIGHT)
        ]
        starts = (
            (3, 3),
            (MENU_GRID_WIDTH - 4, 3),
            (3, MENU_GRID_HEIGHT - 4),
            (MENU_GRID_WIDTH - 4, MENU_GRID_HEIGHT - 4)
        )
        names = random.sample(config.BOT_NAMES, len(starts))
        self.menu_players = []

        for player_id, (start, name, color) in enumerate(
            zip(starts, names, config.PLAYER_COLOR_OPTIONS)
        ):
            player = Player(
                player_id=player_id,
                name=name,
                start_position=start,
                color=color,
                is_human=False
            )
            # Shorter protection keeps the decorative match fast and lively.
            player.invulnerable_until = 0
            self.menu_players.append(player)
            self.paint_menu_tile(player)

        ticks = pygame.time.get_ticks()
        self.menu_last_step_ticks = ticks
        self.menu_round_reset_at = None
        self.menu_battle_message = self.t("round", number=self.menu_round)
        self.menu_battle_message_until = ticks + 1250
        self.menu_clash_position = None
        self.menu_clash_until = 0

    def paint_menu_tile(self, player: Player) -> None:
        x, y = player.position
        self.menu_board[y][x] = player.color

    def menu_territory_counts(self) -> Dict[int, int]:
        color_counts = {
            color: 0 for color in config.PLAYER_COLOR_OPTIONS
        }
        for row in self.menu_board:
            for color in row:
                if color in color_counts:
                    color_counts[color] += 1

        return {
            player.player_id: color_counts.get(player.color, 0)
            for player in self.menu_players
        }

    def choose_menu_bot_move(self, player: Player) -> Coordinate:
        opponents = [
            opponent
            for opponent in self.menu_players
            if opponent.alive and opponent.player_id != player.player_id
        ]
        moves = ((0, -1), (0, 1), (-1, 0), (1, 0))
        if not opponents:
            return random.choice(moves)

        target = min(
            opponents,
            key=lambda opponent: (
                abs(opponent.position[0] - player.position[0])
                + abs(opponent.position[1] - player.position[1])
            )
        )
        delta_x = target.position[0] - player.position[0]
        delta_y = target.position[1] - player.position[1]
        pursuit_moves: List[Coordinate] = []

        if delta_x:
            pursuit_moves.append((1 if delta_x > 0 else -1, 0))
        if delta_y:
            pursuit_moves.append((0, 1 if delta_y > 0 else -1))

        # Mostly pursue the closest rival, occasionally paint a side route.
        if pursuit_moves and random.random() < 0.78:
            return random.choice(pursuit_moves)
        return random.choice(moves)

    def update_menu_battle(self) -> None:
        ticks = pygame.time.get_ticks()

        if self.menu_round_reset_at is not None:
            if ticks >= self.menu_round_reset_at:
                self.reset_menu_battle()
            return

        if ticks - self.menu_last_step_ticks < MENU_BOT_STEP_MS:
            return

        self.menu_last_step_ticks = ticks
        for player in self.menu_players:
            if not player.alive:
                continue
            dx, dy = self.choose_menu_bot_move(player)
            player.move(
                dx,
                dy,
                MENU_GRID_WIDTH,
                MENU_GRID_HEIGHT
            )
            self.paint_menu_tile(player)

        self.resolve_menu_collisions(ticks)
        alive = [player for player in self.menu_players if player.alive]
        if len(alive) <= 1:
            self.menu_battle_message = (
                self.t("arena_winner", name=alive[0].name)
                if alive
                else self.t("draw")
            )
            self.menu_battle_message_until = ticks + 1800
            self.menu_round_reset_at = ticks + 1800

    def resolve_menu_collisions(self, ticks: int) -> None:
        positions: Dict[Coordinate, List[Player]] = {}
        for player in self.menu_players:
            if player.alive:
                positions.setdefault(player.position, []).append(player)

        territory = self.menu_territory_counts()
        for position, occupants in positions.items():
            if len(occupants) < 2:
                continue

            # Territory is the combat strength. A random tie break guarantees
            # that visible clashes resolve instead of freezing on one cell.
            highest = max(territory[player.player_id] for player in occupants)
            leaders = [
                player
                for player in occupants
                if territory[player.player_id] == highest
            ]
            winner = random.choice(leaders)
            self.menu_clash_position = position
            self.menu_clash_until = ticks + 360

            for loser in occupants:
                if loser is winner or not loser.take_damage(ticks):
                    continue

                self.menu_battle_message = (
                    f"{winner.name}  VS  {loser.name}"
                )
                self.menu_battle_message_until = ticks + 850
                if loser.alive:
                    loser.position = loser.start_position
                    # Menu battles should resume immediately after a hit.
                    loser.invulnerable_until = ticks + 420
                    self.paint_menu_tile(loser)

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def menu_loop(self) -> None:

        while (
            self.state == "menu"
            and
            self.running
        ):

            self.frame_dt = min(
                self.clock.tick(config.FPS) / 1000.0,
                0.05
            )

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    self.running = False
                    return

                if event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.size)
                    continue

                if event.type == pygame.TEXTINPUT and self.menu_view == "name":
                    printable = "".join(
                        character for character in event.text
                        if character.isprintable()
                    )
                    self.name_draft = (self.name_draft + printable)[:16]
                    continue

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        if self.menu_view in ("options", "name"):
                            if self.menu_view == "name":
                                pygame.key.stop_text_input()
                            self.menu_view = "main"
                            continue
                        self.running = False
                        return

                    if self.menu_view == "name":
                        if event.key == pygame.K_BACKSPACE:
                            self.name_draft = self.name_draft[:-1]
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            self.player_name = self.sanitize_player_name(
                                self.name_draft
                            )
                            pygame.key.stop_text_input()
                            self.menu_view = "main"
                            self.save_settings()
                        continue

                    if self.menu_view == "options":
                        self.handle_options_key(event.key, "menu")
                        continue

                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menu_selection = (
                            self.menu_selection - 1
                        ) % len(MENU_ITEMS)

                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_selection = (
                            self.menu_selection + 1
                        ) % len(MENU_ITEMS)

                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.cycle_menu_option(-1)

                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.cycle_menu_option(1)

                    if event.key == pygame.K_m:
                        self.mode_index = (
                            self.mode_index + 1
                        ) % len(config.GAME_MODES)
                        self.save_settings()

                    if event.key == pygame.K_c:
                        self.color_index = (
                            self.color_index + 1
                        ) % len(config.PLAYER_COLOR_OPTIONS)
                        self.save_settings()

                    if event.key == pygame.K_RETURN:

                        self.activate_menu_item()

                if event.type == pygame.MOUSEMOTION and self.menu_view == "main":
                    for index, rect in enumerate(self.menu_item_rects):
                        if rect.collidepoint(event.pos):
                            self.menu_selection = index
                            break

                if event.type == pygame.MOUSEMOTION and self.menu_view == "options":
                    self.select_option_at(event.pos)

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    if self.menu_view == "options":
                        if self.select_option_at(event.pos):
                            self.activate_selected_option("menu")
                        continue
                    for index, rect in enumerate(self.menu_item_rects):
                        if rect.collidepoint(event.pos):
                            self.menu_selection = index
                            self.activate_menu_item()
                            break

            self.update_menu_battle()
            self.draw_menu()

    def cycle_menu_option(self, direction: int) -> None:
        selected = MENU_ITEMS[self.menu_selection]
        if selected == "menu_mode":
            self.mode_index = (
                self.mode_index + direction
            ) % len(config.GAME_MODES)
        elif selected == "menu_color":
            self.color_index = (
                self.color_index + direction
            ) % len(config.PLAYER_COLOR_OPTIONS)
        elif selected == "menu_map":
            self.cycle_map(direction)
            return
        elif selected == "menu_difficulty":
            self.difficulty_index = (
                self.difficulty_index + direction
            ) % len(config.DIFFICULTY_LEVELS)
        else:
            return
        self.save_settings()

    def activate_menu_item(self) -> None:
        selected = MENU_ITEMS[self.menu_selection]
        if selected == "menu_start":
            self.start_match()
        elif selected == "menu_player_name":
            self.name_draft = self.player_name
            self.menu_view = "name"
            pygame.key.start_text_input()
        elif selected in (
            "menu_difficulty", "menu_mode", "menu_color", "menu_map"
        ):
            self.cycle_menu_option(1)
        elif selected == "menu_load_map":
            self.choose_custom_map()
        elif selected == "menu_level_editor":
            self.start_level_editor()
        elif selected == "menu_options":
            self.options_selection = 0
            self.menu_view = "options"
        elif selected == "menu_quit":
            self.running = False

    def draw_menu(self) -> None:
        width, height = self.screen.get_size()

        self.draw_menu_background(width, height)
        if self.menu_view == "options":
            self.draw_options_panel(width, height, "menu")
        elif self.menu_view == "name":
            self.draw_name_panel(width, height)
        else:
            self.draw_menu_panel(width, height)
        self.draw_menu_arena_hud(width, height)

        pygame.display.flip()

    def draw_menu_background(self, width: int, height: int) -> None:
        self.screen.fill((6, 9, 15))
        cell_size = max(
            width / MENU_GRID_WIDTH,
            height / MENU_GRID_HEIGHT
        )
        origin_x = (width - MENU_GRID_WIDTH * cell_size) / 2
        origin_y = (height - MENU_GRID_HEIGHT * cell_size) / 2
        neutral_color = (17, 24, 34)

        for y, row in enumerate(self.menu_board):
            for x, tile_color in enumerate(row):
                base_color = config.COLORS.get(tile_color, neutral_color)
                color = (
                    neutral_color
                    if tile_color == "neutral"
                    else tuple(min(255, 18 + int(channel * 0.48)) for channel in base_color)
                )
                rect = pygame.Rect(
                    round(origin_x + x * cell_size),
                    round(origin_y + y * cell_size),
                    max(1, math.ceil(cell_size) - 1),
                    max(1, math.ceil(cell_size) - 1)
                )
                pygame.draw.rect(self.screen, color, rect, border_radius=2)

        ticks = pygame.time.get_ticks()
        for player in self.menu_players:
            if not player.alive:
                continue
            center = (
                round(origin_x + (player.position[0] + 0.5) * cell_size),
                round(origin_y + (player.position[1] + 0.5) * cell_size)
            )
            color = config.COLORS[player.color]
            pygame.draw.circle(
                self.screen,
                (*color, 45),
                center,
                max(8, round(cell_size * 0.9))
            )
            bot_rect = pygame.Rect(0, 0, max(9, int(cell_size * 0.7)), max(9, int(cell_size * 0.7)))
            bot_rect.center = center
            pygame.draw.rect(self.screen, color, bot_rect, border_radius=3)
            pygame.draw.rect(self.screen, (255, 255, 255), bot_rect, 2, border_radius=3)

        if self.menu_clash_position and ticks < self.menu_clash_until:
            progress = (self.menu_clash_until - ticks) / 360.0
            center = (
                round(origin_x + (self.menu_clash_position[0] + 0.5) * cell_size),
                round(origin_y + (self.menu_clash_position[1] + 0.5) * cell_size)
            )
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                center,
                max(8, round(cell_size * (1.5 - progress))),
                max(1, round(3 * progress))
            )

        # A dark veil keeps the moving arena atmospheric and the menu legible.
        veil = pygame.Surface((width, height), pygame.SRCALPHA)
        veil.fill((3, 7, 13, 92))
        for band in range(8):
            band_rect = pygame.Rect(0, band * height // 8, width, height // 8 + 1)
            pygame.draw.rect(veil, (2, 5, 10, 8 + band * 5), band_rect)
        self.screen.blit(veil, (0, 0))

    def draw_menu_panel(self, width: int, height: int) -> None:
        panel_width = min(520, max(390, int(width * 0.43)))
        panel_height = min(780, max(560, height - 40))
        panel_x = max(28, int(width * 0.055))
        panel_y = max(28, (height - panel_height) // 2)
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            (9, 14, 23, 232),
            panel.get_rect(),
            border_radius=24
        )
        pygame.draw.rect(
            panel,
            (89, 111, 142, 105),
            panel.get_rect(),
            1,
            border_radius=24
        )
        self.screen.blit(panel, (panel_x, panel_y))

        eyebrow = self.small_font.render(
            self.t("menu_tagline"),
            True,
            (113, 183, 255)
        )
        self.screen.blit(eyebrow, (panel_x + 42, panel_y + 24))

        title = self.menu_title_font.render("CUBULUS", True, (248, 250, 255))
        self.screen.blit(title, (panel_x + 36, panel_y + 38))

        subtitle = self.small_font.render(
            self.t("menu_subtitle"),
            True,
            (165, 177, 194)
        )
        self.screen.blit(subtitle, (panel_x + 42, panel_y + 118))

        accent_rect = pygame.Rect(panel_x + 42, panel_y + 148, 64, 4)
        pygame.draw.rect(self.screen, (68, 156, 255), accent_rect, border_radius=2)

        buttons_top = panel_y + 172
        button_width = panel_width - 84
        available_button_height = panel_height - 222
        button_gap = 4
        button_height = min(
            43,
            max(29, (available_button_height - button_gap * (len(MENU_ITEMS) - 1)) // len(MENU_ITEMS))
        )
        self.menu_item_rects = []
        mode_labels = {
            "Untimed": self.t("mode_untimed"),
            "Timed": self.t("mode_timed"),
            "Territory": self.t("mode_territory"),
        }
        for index, item_key in enumerate(MENU_ITEMS):
            rect = pygame.Rect(
                panel_x + 42,
                buttons_top + index * (button_height + button_gap),
                button_width,
                button_height
            )
            self.menu_item_rects.append(rect)
            selected = index == self.menu_selection
            fill = (25, 38, 55, 245) if selected else (16, 24, 36, 218)
            border = (83, 166, 255) if selected else (67, 81, 101)
            pygame.draw.rect(self.screen, fill, rect, border_radius=12)
            pygame.draw.rect(self.screen, border, rect, 2 if selected else 1, border_radius=12)

            label_color = (255, 255, 255) if selected else (202, 211, 224)
            label = self.menu_button_font.render(
                self.t(item_key),
                True,
                label_color
            )
            self.screen.blit(label, (rect.x + 20, rect.centery - label.get_height() // 2))

            if item_key == "menu_start":
                arrow_x = rect.right - 31
                pygame.draw.polygon(
                    self.screen,
                    (103, 192, 255),
                    (
                        (arrow_x - 5, rect.centery - 8),
                        (arrow_x + 6, rect.centery),
                        (arrow_x - 5, rect.centery + 8)
                    )
                )
            elif item_key == "menu_player_name":
                value_surface = self.small_font.render(
                    self.player_name,
                    True,
                    (225, 231, 240)
                )
                self.screen.blit(
                    value_surface,
                    (rect.right - value_surface.get_width() - 18, rect.centery - value_surface.get_height() // 2)
                )
            elif item_key == "menu_difficulty":
                difficulty_labels = {
                    "Beginner": self.t("difficulty_beginner"),
                    "Easy": self.t("difficulty_easy"),
                    "Normal": self.t("difficulty_normal"),
                    "Hard": self.t("difficulty_hard"),
                    "Expert": self.t("difficulty_expert"),
                    "God": self.t("difficulty_god"),
                }
                difficulty = config.DIFFICULTY_LEVELS[self.difficulty_index]
                value_surface = self.small_font.render(
                    f"‹  {difficulty_labels[difficulty]}  ›",
                    True,
                    (113, 183, 255)
                )
                self.screen.blit(
                    value_surface,
                    (rect.right - value_surface.get_width() - 18, rect.centery - value_surface.get_height() // 2)
                )
            elif item_key == "menu_mode":
                value = mode_labels.get(
                    config.GAME_MODES[self.mode_index],
                    config.GAME_MODES[self.mode_index]
                )
                value_surface = self.small_font.render(f"‹  {value}  ›", True, (113, 183, 255))
                self.screen.blit(
                    value_surface,
                    (rect.right - value_surface.get_width() - 18, rect.centery - value_surface.get_height() // 2)
                )
            elif item_key == "menu_color":
                selected_color = config.PLAYER_COLOR_OPTIONS[self.color_index]
                value = self.t(f"color_{selected_color}")
                value_surface = self.small_font.render(f"{value}  ›", True, (225, 231, 240))
                value_x = rect.right - value_surface.get_width() - 18
                self.screen.blit(
                    value_surface,
                    (value_x, rect.centery - value_surface.get_height() // 2)
                )
                pygame.draw.circle(
                    self.screen,
                    config.COLORS[selected_color],
                    (value_x - 17, rect.centery),
                    7
                )
            elif item_key == "menu_map":
                value = self.map_data["name"]
                value_surface = self.small_font.render(
                    f"‹  {value}  ›",
                    True,
                    (113, 183, 255)
                )
                self.screen.blit(
                    value_surface,
                    (
                        rect.right - value_surface.get_width() - 18,
                        rect.centery - value_surface.get_height() // 2
                    )
                )
            elif item_key in ("menu_load_map", "menu_level_editor", "menu_options"):
                arrow = self.menu_button_font.render(">", True, (113, 183, 255))
                self.screen.blit(
                    arrow,
                    (rect.right - arrow.get_width() - 22, rect.centery - arrow.get_height() // 2)
                )
            elif item_key == "menu_quit":
                close = self.menu_button_font.render("×", True, (232, 105, 112))
                self.screen.blit(
                    close,
                    (rect.right - close.get_width() - 22, rect.centery - close.get_height() // 2)
                )

        controls = self.small_font.render(
            (
                self.map_notice
                if pygame.time.get_ticks() < self.map_notice_until
                else self.t("menu_controls")
            ),
            True,
            (126, 140, 159)
        )
        self.screen.blit(
            controls,
            (panel_x + 42, panel_y + panel_height - 48)
        )

    def draw_name_panel(self, width: int, height: int) -> None:
        """Draw the focused player-name input on top of the menu arena."""

        panel_rect = pygame.Rect(0, 0, min(560, width - 60), 270)
        panel_rect.center = (width // 2, height // 2)
        self.draw_glass_panel(panel_rect, fill=(7, 12, 20, 242))

        title = self.title_font.render(
            self.t("name_title"),
            True,
            (248, 250, 255)
        )
        self.screen.blit(
            title,
            title.get_rect(center=(panel_rect.centerx, panel_rect.y + 54))
        )

        input_rect = pygame.Rect(
            panel_rect.x + 42,
            panel_rect.y + 100,
            panel_rect.width - 84,
            62
        )
        pygame.draw.rect(self.screen, (18, 28, 42), input_rect, border_radius=12)
        pygame.draw.rect(self.screen, (83, 166, 255), input_rect, 2, border_radius=12)
        value = self.menu_heading_font.render(
            self.name_draft + ("|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""),
            True,
            (244, 247, 252)
        )
        self.screen.blit(
            value,
            (input_rect.x + 18, input_rect.centery - value.get_height() // 2)
        )

        hint = self.small_font.render(
            self.t("name_hint"),
            True,
            (126, 140, 159)
        )
        self.screen.blit(
            hint,
            hint.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 45))
        )

    def draw_menu_arena_hud(self, width: int, height: int) -> None:
        if width < 860:
            return

        hud_width = min(330, width - 610)
        hud_rect = pygame.Rect(width - hud_width - 42, 42, hud_width, 238)
        hud = pygame.Surface(hud_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(hud, (7, 12, 20, 205), hud.get_rect(), border_radius=18)
        pygame.draw.rect(hud, (75, 94, 119, 120), hud.get_rect(), 1, border_radius=18)
        self.screen.blit(hud, hud_rect.topleft)

        live_dot = (hud_rect.x + 25, hud_rect.y + 29)
        pygame.draw.circle(self.screen, (255, 73, 88), live_dot, 5)
        live_label = self.menu_heading_font.render(
            self.t("live_arena"),
            True,
            (244, 247, 252)
        )
        self.screen.blit(live_label, (hud_rect.x + 40, hud_rect.y + 15))

        territory = self.menu_territory_counts()
        for index, player in enumerate(self.menu_players):
            row_y = hud_rect.y + 68 + index * 36
            color = config.COLORS[player.color]
            pygame.draw.circle(self.screen, color, (hud_rect.x + 27, row_y + 9), 6)
            name_color = (213, 220, 230) if player.alive else (91, 101, 115)
            name = self.small_font.render(player.name, True, name_color)
            self.screen.blit(name, (hud_rect.x + 42, row_y))
            score = self.small_font.render(
                f"{territory.get(player.player_id, 0):03d}  "
                + "●" * player.lives
                + "○" * (config.PLAYER_LIVES - player.lives),
                True,
                name_color
            )
            self.screen.blit(score, (hud_rect.right - score.get_width() - 18, row_y))

        ticks = pygame.time.get_ticks()
        if ticks < self.menu_battle_message_until:
            message = self.small_font.render(
                self.menu_battle_message,
                True,
                (126, 199, 255)
            )
            message_rect = message.get_rect(
                center=(hud_rect.centerx, hud_rect.bottom - 22)
            )
            self.screen.blit(message, message_rect)

    # ------------------------------------------------------------------
    # Gameplay
    # ------------------------------------------------------------------

    def playing_loop(self) -> None:

        while (
            self.state == "playing"
            and
            self.running
        ):

            real_frame_dt = min(
                self.clock.tick(config.FPS) / 1000.0,
                0.05
            )

            self.handle_game_events()

            if self.state != "playing" or not self.running:
                return

            self.simulation_accumulator += (
                real_frame_dt * self.effective_game_speed()
            )
            simulation_step = 1.0 / config.FPS
            while self.simulation_accumulator >= simulation_step:
                self.frame_dt = simulation_step
                self.game_ticks_ms += simulation_step * 1000.0
                self.update_game_state()
                self.simulation_accumulator -= simulation_step
                if self.state != "playing" or not self.running:
                    return

            self.draw_gameplay()

    def handle_game_events(self) -> None:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False
                return

            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.size)
                continue

            if (
                event.type == pygame.KEYDOWN
                and
                event.key == pygame.K_ESCAPE
            ):

                self.pause_match()
                return

            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.change_zoom(config.CAMERA_ZOOM_STEP)
                    continue

                if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.change_zoom(-config.CAMERA_ZOOM_STEP)
                    continue

                if event.key in (pygame.K_0, pygame.K_KP0):
                    self.camera_target_zoom = config.CAMERA_START_ZOOM
                    continue

                human = self.players[0]

                if not human.alive:
                    continue

                moves = {
                    pygame.K_w: (0, -1),
                    pygame.K_s: (0, 1),
                    pygame.K_a: (-1, 0),
                    pygame.K_d: (1, 0),

                    pygame.K_UP: (0, -1),
                    pygame.K_DOWN: (0, 1),
                    pygame.K_LEFT: (-1, 0),
                    pygame.K_RIGHT: (1, 0),
                }

                if event.key in moves:

                    dx, dy = moves[
                        event.key
                    ]
                    if self.auto_movement_enabled:
                        self.human_move_direction = (dx, dy)
                    self.move_human(dx, dy)
                    self.human_last_move_ticks = self.game_ticks()

            if event.type == pygame.MOUSEWHEEL:
                self.change_zoom(
                    event.y * config.CAMERA_ZOOM_STEP
                )

    def move_human(self, dx: int, dy: int) -> None:

        if not self.players:
            return

        human = self.players[0]
        if not human.alive:
            return

        self.try_move_player(human, dx, dy)

    def update_human_auto_movement(self) -> None:

        if not self.auto_movement_enabled or self.human_move_direction is None:
            return

        ticks = self.game_ticks()
        if ticks - self.human_last_move_ticks < config.PLAYER_MOVE_INTERVAL_MS:
            return

        dx, dy = self.human_move_direction
        self.move_human(dx, dy)
        self.human_last_move_ticks = ticks

    def change_zoom(self, amount: float) -> None:

        self.camera_target_zoom = max(
            config.CAMERA_MIN_ZOOM,
            min(
                config.CAMERA_MAX_ZOOM,
                self.camera_target_zoom + amount
            )
        )

    def update_camera(self) -> None:

        if not self.players:
            return

        human = self.players[0]
        target_x = human.position[0] + 0.5
        target_y = human.position[1] + 0.5

        follow_blend = 1.0 - math.exp(
            -config.CAMERA_FOLLOW_SPEED * self.frame_dt
        )
        zoom_blend = 1.0 - math.exp(
            -config.CAMERA_ZOOM_SPEED * self.frame_dt
        )

        self.camera_x += (target_x - self.camera_x) * follow_blend
        self.camera_y += (target_y - self.camera_y) * follow_blend
        self.camera_zoom += (
            self.camera_target_zoom - self.camera_zoom
        ) * zoom_blend

    def update_game_state(self) -> None:

        if not self.running:
            return

        self.update_human_auto_movement()

        self.update_bots()

        self.resolve_collisions()

        self.update_camera()

        self.territory_counts = (
            self.compute_territories()
        )

        self.check_victory_conditions()

    def update_bots(self) -> None:

        grid_height = len(self.board)
        grid_width = len(self.board[0]) if grid_height else 0
        if not grid_width:
            return

        difficulty_index = getattr(self, "difficulty_index", 1)
        difficulty = config.DIFFICULTY_LEVELS[difficulty_index]
        profile = config.DIFFICULTY_PROFILES[difficulty]

        for player in self.players[1:]:

            if not player.alive:
                continue

            if (
                random.random()
                <=
                profile["bot_move_chance"]
            ):

                dx, dy = self.choose_bot_move(
                    player,
                    profile["bot_chase_chance"]
                )
                if not self.try_move_player(player, dx, dy):
                    alternatives = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                    random.shuffle(alternatives)
                    for fallback_dx, fallback_dy in alternatives:
                        if self.try_move_player(player, fallback_dx, fallback_dy):
                            break

    def choose_bot_move(
        self,
        player: Player,
        chase_chance: float
    ) -> Coordinate:
        """Choose a random or human-seeking move based on difficulty."""

        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        if not self.players or random.random() > chase_chance:
            return random.choice(moves)

        target = self.players[0]
        delta_x = target.position[0] - player.position[0]
        delta_y = target.position[1] - player.position[1]
        preferred: List[Coordinate] = []
        if delta_x:
            preferred.append((1 if delta_x > 0 else -1, 0))
        if delta_y:
            preferred.append((0, 1 if delta_y > 0 else -1))
        if not preferred:
            return random.choice(moves)
        preferred.sort(
            key=lambda move: abs(delta_x) if move[0] else abs(delta_y),
            reverse=True
        )
        return preferred[0]

    def resolve_collisions(self) -> None:

        positions: Dict[
            Coordinate,
            List[Player]
        ] = {}

        for player in self.players:

            if player.alive:

                positions.setdefault(
                    player.position,
                    []
                ).append(
                    player
                )

        if not positions:
            return

        territory_snapshot = (
            self.compute_territories()
        )
        current_ticks = self.game_ticks()

        for occupants in positions.values():

            if len(occupants) < 2:
                continue

            if self.god_alliance_active():
                human = next(
                    (player for player in occupants if player.is_human),
                    None
                )
                bots = [player for player in occupants if not player.is_human]
                if human is None or not bots:
                    # Allied bots never damage one another.
                    continue
                human_strength = territory_snapshot[human.player_id]
                bot_strength = max(
                    territory_snapshot[bot.player_id]
                    for bot in bots
                )
                if human_strength < bot_strength:
                    losers = [human]
                elif human_strength > bot_strength:
                    losers = bots
                else:
                    losers = []
            else:
                best = max(
                    territory_snapshot[
                        player.player_id
                    ]
                    for player in occupants
                )

                losers = [
                    player
                    for player in occupants
                    if territory_snapshot[
                        player.player_id
                    ] < best
                ]

            if not losers:
                continue

            for loser in losers:

                if self.is_territory_mode():
                    if current_ticks < loser.invulnerable_until:
                        continue
                    loser.invulnerable_until = (
                        current_ticks + config.DAMAGE_COOLDOWN_MS
                    )
                    loser.position = loser.start_position
                    self.apply_tile_effect(loser)
                    if loser.is_human:
                        self.damage_flash_until = (
                            current_ticks + config.DAMAGE_FLASH_MS
                        )
                    self.status_message = self.t(
                        "territory_reset",
                        name=loser.name
                    )
                    continue

                if not loser.take_damage(current_ticks):
                    continue

                if loser.is_human:
                    self.damage_flash_until = (
                        current_ticks + config.DAMAGE_FLASH_MS
                    )

                if not loser.alive:

                    self.status_message = self.t(
                        "eliminated",
                        name=loser.name
                    )

                else:

                    # Moving a damaged player to the spawn point prevents one
                    # collision from draining several lives in succession.
                    loser.position = loser.start_position
                    self.apply_tile_effect(loser)
                    self.status_message = self.t(
                        "lost_life",
                        name=loser.name,
                        lives=loser.lives
                    )

    def determine_territory_winner(self) -> Optional[Player]:
        counts = self.territory_counts or self.compute_territories()
        if not self.players:
            return None

        highest = max(counts.get(player.player_id, 0) for player in self.players)
        if highest < self.territory_target_tiles():
            return None

        leaders = [
            player
            for player in self.players
            if counts.get(player.player_id, 0) == highest
        ]
        return leaders[0] if len(leaders) == 1 else None

    def check_victory_conditions(
        self
    ) -> None:

        if self.is_territory_mode():
            winner = self.determine_territory_winner()
            if winner is not None:
                self.end_match(
                    self.t("territory_winner", name=winner.name),
                    title=(
                        self.t("victory")
                        if winner.is_human
                        else self.t("game_over")
                    ),
                    color=(
                        config.COLORS["green"]
                        if winner.is_human
                        else config.COLORS["white"]
                    )
                )
            return

        alive = self.alive_players()

        if self.players and not self.players[0].alive:

            self.end_match(
                self.t("player_lost"),
                title=self.t("game_over"),
                color=config.COLORS["red"]
            )

            return

        if not alive:

            self.end_match(
                self.t("all_eliminated")
            )

            return

        if len(alive) == 1:

            winner = alive[0]

            message = self.t("winner", name=winner.name)

            self.end_match(
                message,
                title=(
                    self.t("victory")
                    if winner.is_human
                    else self.t("game_over")
                ),
                color=(
                    config.COLORS["green"]
                    if winner.is_human
                    else config.COLORS["white"]
                )
            )

            return

        if (
            config.GAME_MODES[
                self.mode_index
            ] == "Timed"
        ):

            assert (
                self.match_start_ticks
                is not None
            )

            elapsed = (
                self.game_ticks()
                -
                self.match_start_ticks
            ) / 1000.0

            if (
                elapsed
                >=
                config.TIMED_MODE_SECONDS
            ):

                winner = (
                    self.determine_timed_winner()
                )

                self.end_match(
                    winner
                )

    def determine_timed_winner(
        self
    ) -> str:

        counts = (
            self.territory_counts
            or
            self.compute_territories()
        )

        contenders = self.alive_players()

        if not contenders:

            return self.t("time_no_winner")

        # Eliminated players keep the tiles they marked.  They must not set
        # the score to beat, otherwise the timed match can finish without a
        # winner even though two or more active players are still competing.
        highest = (
            max(
                counts.get(
                    player.player_id,
                    0
                )
                for player in contenders
            )
        )

        leaders = [
            player
            for player in contenders
            if counts.get(
                player.player_id,
                0
            ) == highest
        ]

        if len(leaders) == 1:

            return self.t("time_winner", name=leaders[0].name)

        if leaders:

            names = ", ".join(
                player.name
                for player in leaders
            )

            return self.t("time_tie", names=names)

        return self.t("time_no_winner")

    def remaining_time(
        self
    ) -> Optional[int]:

        if (
            config.GAME_MODES[
                self.mode_index
            ] != "Timed"
            or
            self.match_start_ticks
            is None
        ):

            return None

        elapsed = (
            self.game_ticks()
            -
            self.match_start_ticks
        ) / 1000.0

        remaining = max(
            0,
            int(
                config.TIMED_MODE_SECONDS
                -
                elapsed
            )
        )

        return remaining

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw_gameplay(self) -> None:

        # Use the same dark tactical presentation as the main menu: the arena
        # fills the window while translucent interface cards float above it.
        self.screen.fill((6, 9, 15))

        self.draw_board()

        self.draw_gameplay_atmosphere()

        self.draw_players()

        self.draw_damage_flash()

        self.draw_ui_panel()

        self.draw_debug_overlay()

        pygame.display.flip()

    def draw_debug_overlay(self) -> None:
        if not self.debug_mode:
            return

        speed = config.DEBUG_SPEED_OPTIONS[self.game_speed_index]
        label = self.small_font.render(
            f"DEBUG  |  SIMULATION {speed:g}x",
            True,
            (255, 206, 112)
        )
        padding_x = 13
        padding_y = 8
        rect = pygame.Rect(
            self.screen.get_width() - label.get_width() - padding_x * 2 - 18,
            18,
            label.get_width() + padding_x * 2,
            label.get_height() + padding_y * 2
        )
        badge = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(badge, (39, 29, 13, 220), badge.get_rect(), border_radius=12)
        pygame.draw.rect(
            badge,
            (255, 183, 70, 190),
            badge.get_rect(),
            1,
            border_radius=12
        )
        badge.blit(label, (padding_x, padding_y))
        self.screen.blit(badge, rect.topleft)

    def draw_board(self) -> None:

        if not self.board:
            return

        viewport = self.board_viewport()
        cell_size = config.CELL_SIZE * self.camera_zoom
        origin_x, origin_y = self.board_origin(viewport, cell_size)

        board_height = len(self.board)
        board_width = len(self.board[0])

        first_x = max(0, int(math.floor((viewport.left - origin_x) / cell_size)))
        first_y = max(0, int(math.floor((viewport.top - origin_y) / cell_size)))
        last_x = min(board_width, int(math.ceil((viewport.right - origin_x) / cell_size)))
        last_y = min(board_height, int(math.ceil((viewport.bottom - origin_y) / cell_size)))
        gap = max(1, int(round(cell_size * 0.09)))
        radius = max(1, min(4, int(round(cell_size * 0.12))))

        previous_clip = self.screen.get_clip()
        self.screen.set_clip(viewport)

        for y in range(first_y, last_y):
            row = self.board[y]

            for x in range(first_x, last_x):
                left = round(origin_x + x * cell_size)
                top = round(origin_y + y * cell_size)
                right = round(origin_x + (x + 1) * cell_size)
                bottom = round(origin_y + (y + 1) * cell_size)

                rect = pygame.Rect(
                    left,
                    top,
                    max(1, right - left - gap),
                    max(1, bottom - top - gap)
                )
                tile_color = row[x]
                base_color = config.COLORS.get(
                    tile_color,
                    config.COLORS["neutral"]
                )
                color = (
                    config.COLORS["obstacle"]
                    if tile_color == "obstacle"
                    else (17, 24, 34)
                    if tile_color == "neutral"
                    else tuple(
                        min(255, 18 + int(channel * 0.48))
                        for channel in base_color
                    )
                )
                pygame.draw.rect(
                    self.screen,
                    color,
                    rect,
                    border_radius=radius
                )
                if tile_color == "obstacle" and rect.width >= 8:
                    detail = (111, 124, 143)
                    pygame.draw.line(self.screen, detail, rect.topleft, rect.bottomright, 2)
                    pygame.draw.line(self.screen, detail, rect.topright, rect.bottomleft, 2)

        self.screen.set_clip(previous_clip)

    def board_viewport(self) -> pygame.Rect:

        width, height = self.screen.get_size()
        return pygame.Rect(0, 0, width, height)

    def board_origin(
        self,
        viewport: pygame.Rect,
        cell_size: float
    ) -> Tuple[float, float]:
        """Keep the arena behind the HUD, including at map edges."""

        board_height = len(self.board)
        board_width = len(self.board[0]) if board_height else 0
        board_pixel_width = board_width * cell_size
        board_pixel_height = board_height * cell_size

        if board_pixel_width <= viewport.width:
            origin_x = viewport.centerx - board_pixel_width / 2
        else:
            half_visible = viewport.width / (2 * cell_size)
            camera_x = max(
                half_visible,
                min(board_width - half_visible, self.camera_x)
            )
            origin_x = viewport.centerx - camera_x * cell_size

        if board_pixel_height <= viewport.height:
            origin_y = viewport.centery - board_pixel_height / 2
        else:
            half_visible = viewport.height / (2 * cell_size)
            camera_y = max(
                half_visible,
                min(board_height - half_visible, self.camera_y)
            )
            origin_y = viewport.centery - camera_y * cell_size

        return origin_x, origin_y

    def cell_screen_rect(self, x: int, y: int) -> pygame.Rect:

        viewport = self.board_viewport()
        cell_size = config.CELL_SIZE * self.camera_zoom
        origin_x, origin_y = self.board_origin(viewport, cell_size)
        gap = max(1, int(round(cell_size * 0.09)))

        left = round(origin_x + x * cell_size)
        top = round(origin_y + y * cell_size)
        right = round(origin_x + (x + 1) * cell_size)
        bottom = round(origin_y + (y + 1) * cell_size)

        return pygame.Rect(
            left,
            top,
            max(1, right - left - gap),
            max(1, bottom - top - gap)
        )

    def draw_players(self) -> None:

        viewport = self.board_viewport()
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(viewport)

        for player in self.players:

            if not player.alive:
                continue

            current_ticks = self.game_ticks()
            if (
                current_ticks < player.invulnerable_until
                and (current_ticks // 100) % 2 == 0
            ):
                continue

            color = config.COLORS.get(
                player.color,
                config.COLORS["white"]
            )

            rect = self.cell_screen_rect(*player.position)

            if not rect.colliderect(viewport):
                continue

            glow_rect = rect.inflate(
                max(6, rect.width // 2),
                max(6, rect.height // 2)
            )
            glow_color = tuple(
                min(255, 22 + int(channel * 0.38))
                for channel in color
            )
            pygame.draw.rect(
                self.screen,
                glow_color,
                glow_rect,
                border_radius=max(4, glow_rect.width // 3)
            )

            pygame.draw.rect(
                self.screen,
                color,
                rect,
                border_radius=max(2, rect.width // 5)
            )

            border_width = max(1, min(3, rect.width // 6))
            pygame.draw.rect(
                self.screen,
                config.COLORS["white"],
                rect,
                border_width,
                border_radius=max(2, rect.width // 5)
            )

        self.screen.set_clip(previous_clip)

    def draw_gameplay_atmosphere(self) -> None:
        """Add the menu's cool cinematic veil without hiding the action."""

        width, height = self.screen.get_size()
        veil = pygame.Surface((width, height), pygame.SRCALPHA)
        veil.fill((3, 7, 13, 22))

        band_count = 8
        for band in range(band_count):
            band_height = height // band_count + 1
            top_alpha = max(0, 36 - band * 6)
            bottom_alpha = max(0, 36 - (band_count - 1 - band) * 6)
            alpha = max(top_alpha, bottom_alpha)
            band_rect = pygame.Rect(
                0,
                band * height // band_count,
                width,
                band_height
            )
            pygame.draw.rect(veil, (2, 5, 10, alpha), band_rect)

        self.screen.blit(veil, (0, 0))

    def draw_damage_flash(self) -> None:

        remaining = self.damage_flash_until - self.game_ticks()
        if remaining <= 0:
            return

        viewport = self.board_viewport()
        alpha = int(
            95 * min(1.0, remaining / config.DAMAGE_FLASH_MS)
        )
        overlay = pygame.Surface(viewport.size, pygame.SRCALPHA)
        overlay.fill((*config.COLORS["red"], alpha))
        self.screen.blit(overlay, viewport.topleft)

    def draw_ui_panel(self) -> None:

        width, height = self.screen.get_size()
        margin = max(14, min(24, width // 45))

        brand_rect = pygame.Rect(
            margin,
            margin,
            min(260, max(205, width // 4)),
            72
        )
        self.draw_glass_panel(brand_rect)
        pygame.draw.circle(
            self.screen,
            (90, 190, 255),
            (brand_rect.x + 19, brand_rect.y + 20),
            5
        )
        eyebrow = self.small_font.render(
            self.t("match_active"),
            True,
            (113, 183, 255)
        )
        self.screen.blit(eyebrow, (brand_rect.x + 32, brand_rect.y + 10))
        title = self.menu_heading_font.render(
            "CUBULUS",
            True,
            (248, 250, 255)
        )
        self.screen.blit(title, (brand_rect.x + 17, brand_rect.y + 35))

        mode = self.current_mode()
        mode_label = self.mode_display_label().upper()
        remaining = self.remaining_time()
        match_value = (
            f"{remaining // 60:02d}:{remaining % 60:02d}"
            if remaining is not None
            else (
                self.t(
                    "territory_target",
                    percent=self.territory_target_percent()
                )
                if mode == "Territory"
                else mode_label
            )
        )
        info_width = min(230, max(175, width // 5))
        info_rect = pygame.Rect(
            width - margin - info_width,
            margin,
            info_width,
            72
        )
        self.draw_glass_panel(info_rect)
        mode_surface = self.small_font.render(
            mode_label,
            True,
            (126, 140, 159)
        )
        self.screen.blit(mode_surface, (info_rect.x + 17, info_rect.y + 11))
        value_surface = self.menu_heading_font.render(
            match_value,
            True,
            (244, 247, 252)
        )
        self.screen.blit(value_surface, (info_rect.x + 17, info_rect.y + 34))
        esc_surface = self.small_font.render(
            self.t("pause_short"),
            True,
            (113, 183, 255)
        )
        self.screen.blit(
            esc_surface,
            (
                info_rect.right - esc_surface.get_width() - 16,
                info_rect.y + 14
            )
        )

        compact = width < 760
        score_height = 154 if compact else 100
        score_width = min(width - margin * 2, 920)
        score_rect = pygame.Rect(
            (width - score_width) // 2,
            height - margin - score_height,
            score_width,
            score_height
        )
        self.draw_glass_panel(score_rect, fill=(7, 12, 20, 222))

        column_count = 2 if compact else max(1, len(self.players))
        row_count = 2 if compact else 1
        column_width = score_rect.width / column_count
        row_height = score_rect.height / row_count

        for index, player in enumerate(self.players):
            column = index % column_count
            row = index // column_count
            item_rect = pygame.Rect(
                round(score_rect.x + column * column_width),
                round(score_rect.y + row * row_height),
                round(column_width),
                round(row_height)
            )
            selected = player.is_human
            if selected:
                highlight = item_rect.inflate(-8, -8)
                pygame.draw.rect(
                    self.screen,
                    (22, 36, 52, 205),
                    highlight,
                    border_radius=12
                )
                pygame.draw.rect(
                    self.screen,
                    (83, 166, 255),
                    highlight,
                    1,
                    border_radius=12
                )
            elif column > 0:
                divider_x = item_rect.left
                pygame.draw.line(
                    self.screen,
                    (67, 81, 101),
                    (divider_x, item_rect.top + 18),
                    (divider_x, item_rect.bottom - 18),
                    1
                )

            content_x = item_rect.x + 19
            color = config.COLORS.get(
                player.color,
                config.COLORS["white"]
            )
            pygame.draw.circle(
                self.screen,
                color,
                (content_x + 6, item_rect.y + 27),
                6
            )
            name = player.name.upper()
            name_surface = self.small_font.render(
                name,
                True,
                (244, 247, 252) if player.alive else (91, 101, 115)
            )
            self.screen.blit(name_surface, (content_x + 19, item_rect.y + 18))

            territory = self.territory_counts.get(player.player_id, 0)
            score_surface = self.menu_heading_font.render(
                f"{territory:03d}",
                True,
                (244, 247, 252) if player.alive else (91, 101, 115)
            )
            self.screen.blit(score_surface, (content_x, item_rect.y + 48))
            label_surface = self.small_font.render(
                self.t("territories"),
                True,
                (126, 140, 159)
            )
            self.screen.blit(
                label_surface,
                (content_x + score_surface.get_width() + 8, item_rect.y + 55)
            )

            pip_y = item_rect.y + (63 if compact else 72)
            if self.is_territory_mode():
                infinity_surface = self.menu_heading_font.render(
                    "∞",
                    True,
                    color
                )
                self.screen.blit(
                    infinity_surface,
                    infinity_surface.get_rect(
                        midright=(item_rect.right - 19, pip_y)
                    )
                )
            else:
                pip_x = item_rect.right - 24
                for life_index in range(config.PLAYER_LIVES - 1, -1, -1):
                    filled = life_index < player.lives
                    pygame.draw.circle(
                        self.screen,
                        color if filled else (65, 76, 91),
                        (pip_x, pip_y),
                        4,
                        0 if filled else 1
                    )
                    pip_x -= 13

    def draw_glass_panel(
        self,
        rect: pygame.Rect,
        fill: Tuple[int, int, int, int] = (7, 12, 20, 205)
    ) -> None:
        """Draw a translucent card from the main-menu visual system."""

        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            fill,
            panel.get_rect(),
            border_radius=18
        )
        pygame.draw.rect(
            panel,
            (75, 94, 119, 120),
            panel.get_rect(),
            1,
            border_radius=18
        )
        self.screen.blit(panel, rect.topleft)

    # ------------------------------------------------------------------
    # Shared options
    # ------------------------------------------------------------------

    def handle_options_key(self, key: int, source: str) -> None:

        if key in (pygame.K_UP, pygame.K_w):
            self.options_selection = (
                self.options_selection - 1
            ) % len(OPTIONS_MENU_ITEMS)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.options_selection = (
                self.options_selection + 1
            ) % len(OPTIONS_MENU_ITEMS)
        elif key in (
            pygame.K_LEFT,
            pygame.K_a,
            pygame.K_MINUS,
            pygame.K_KP_MINUS
        ):
            self.adjust_selected_option(-1)
        elif key in (
            pygame.K_RIGHT,
            pygame.K_d,
            pygame.K_PLUS,
            pygame.K_EQUALS,
            pygame.K_KP_PLUS
        ):
            self.adjust_selected_option(1)
        elif key in (pygame.K_0, pygame.K_KP0):
            if self.options_selection == 1:
                self.preferred_camera_zoom = config.CAMERA_START_ZOOM
                self.camera_target_zoom = self.preferred_camera_zoom
                self.save_settings()
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.activate_selected_option(source)

    def adjust_selected_option(self, direction: int) -> None:

        if self.options_selection == 0:
            self.auto_movement_enabled = not self.auto_movement_enabled
            if not self.auto_movement_enabled:
                self.human_move_direction = None
        elif self.options_selection == 1:
            self.change_zoom(direction * config.CAMERA_ZOOM_STEP)
            self.preferred_camera_zoom = self.camera_target_zoom
        elif self.options_selection == 2:
            self.resolution_index = (
                self.resolution_index + direction
            ) % len(config.RESOLUTION_OPTIONS)
            self.apply_resolution(
                config.RESOLUTION_OPTIONS[self.resolution_index]
            )
            return
        elif self.options_selection == 3:
            self.debug_mode = not self.debug_mode
            self.simulation_accumulator = 0.0
        elif self.options_selection == 4:
            if not self.debug_mode:
                return
            self.game_speed_index = (
                self.game_speed_index + direction
            ) % len(config.DEBUG_SPEED_OPTIONS)
            self.simulation_accumulator = 0.0
        elif self.options_selection == 5:
            language_index = LANGUAGES.index(self.language)
            self.language = LANGUAGES[
                (language_index + direction) % len(LANGUAGES)
            ]
            self.status_message = self.t(
                "status_match_running"
                if self.state in ("playing", "paused")
                else "status_awaiting"
            )
            self.game_over_title = self.t("game_over")
            self.menu_battle_message = self.t(
                "round",
                number=self.menu_round
            )
        else:
            return

        self.save_settings()

    def activate_selected_option(self, source: str) -> None:

        if self.options_selection < len(OPTIONS_MENU_ITEMS) - 1:
            self.adjust_selected_option(1)
        else:
            if source == "pause":
                self.pause_view = "main"
            else:
                self.menu_view = "main"

    def select_option_at(self, position: Coordinate) -> bool:

        for index, rect in enumerate(self.options_item_rects):
            if rect.collidepoint(position):
                self.options_selection = index
                return True

        return False

    def draw_options_panel(self, width: int, height: int, source: str) -> None:

        panel_width = min(600, max(440, int(width * 0.52)))
        panel_height = min(650, max(560, height - 40))
        panel_x = (
            max(28, int(width * 0.055))
            if source == "menu"
            else (width - panel_width) // 2
        )
        panel_y = max(28, (height - panel_height) // 2)
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.draw_glass_panel(panel_rect, fill=(7, 12, 20, 238))

        eyebrow = self.small_font.render(
            self.t("options_eyebrow"),
            True,
            (113, 183, 255)
        )
        self.screen.blit(eyebrow, (panel_x + 38, panel_y + 25))
        title = self.menu_heading_font.render(
            self.t("options_title"),
            True,
            (248, 250, 255)
        )
        self.screen.blit(title, (panel_x + 38, panel_y + 49))
        subtitle = self.small_font.render(
            self.t("options_subtitle"),
            True,
            (151, 165, 184)
        )
        self.screen.blit(subtitle, (panel_x + 38, panel_y + 81))

        self.options_item_rects = []
        rows_top = panel_y + 120
        row_width = panel_width - 76
        row_height = 48
        row_gap = 6

        for index, label_key in enumerate(OPTIONS_MENU_ITEMS):
            rect = pygame.Rect(
                panel_x + 38,
                rows_top + index * (row_height + row_gap),
                row_width,
                row_height
            )
            self.options_item_rects.append(rect)
            selected = index == self.options_selection
            disabled = index == 4 and not self.debug_mode
            fill = (25, 38, 55, 248) if selected else (14, 22, 33, 226)
            border = (83, 166, 255) if selected else (58, 72, 91)
            pygame.draw.rect(self.screen, fill, rect, border_radius=14)
            pygame.draw.rect(
                self.screen,
                border,
                rect,
                2 if selected else 1,
                border_radius=14
            )

            label_surface = self.menu_button_font.render(
                self.t(label_key),
                True,
                (
                    (112, 123, 139)
                    if disabled
                    else ((244, 247, 252) if selected else (196, 205, 218))
                )
            )
            self.screen.blit(
                label_surface,
                (rect.x + 20, rect.centery - label_surface.get_height() // 2)
            )

            if index == 0:
                value = self.t("on") if self.auto_movement_enabled else self.t("off")
                value_color = (
                    (100, 220, 162)
                    if self.auto_movement_enabled
                    else (137, 149, 166)
                )
                value_surface = self.small_font.render(value, True, value_color)
                pill = pygame.Rect(
                    rect.right - 82,
                    rect.centery - 17,
                    58,
                    34
                )
                pygame.draw.rect(self.screen, (22, 40, 48), pill, border_radius=17)
                pygame.draw.rect(self.screen, value_color, pill, 1, border_radius=17)
                self.screen.blit(value_surface, value_surface.get_rect(center=pill.center))
            elif index == 1:
                zoom_percent = round(self.camera_target_zoom * 100)
                value_surface = self.small_font.render(
                    f"<  {zoom_percent} %  >",
                    True,
                    (113, 183, 255)
                )
                self.screen.blit(
                    value_surface,
                    (
                        rect.right - value_surface.get_width() - 20,
                        rect.centery - value_surface.get_height() // 2
                    )
                )
            elif index == 2:
                resolution = self.screen.get_size()
                value_surface = self.small_font.render(
                    f"<  {resolution[0]} × {resolution[1]}  >",
                    True,
                    (113, 183, 255)
                )
                self.screen.blit(
                    value_surface,
                    (
                        rect.right - value_surface.get_width() - 20,
                        rect.centery - value_surface.get_height() // 2
                    )
                )
            elif index == 3:
                value = self.t("on") if self.debug_mode else self.t("off")
                value_color = (
                    (255, 193, 92) if self.debug_mode else (137, 149, 166)
                )
                value_surface = self.small_font.render(value, True, value_color)
                pill = pygame.Rect(
                    rect.right - 82,
                    rect.centery - 17,
                    58,
                    34
                )
                pygame.draw.rect(self.screen, (42, 35, 23), pill, border_radius=17)
                pygame.draw.rect(self.screen, value_color, pill, 1, border_radius=17)
                self.screen.blit(value_surface, value_surface.get_rect(center=pill.center))
            elif index == 4:
                speed = config.DEBUG_SPEED_OPTIONS[self.game_speed_index]
                value = (
                    f"<  {speed:g}x  >"
                    if self.debug_mode
                    else self.t("debug_off")
                )
                value_surface = self.small_font.render(
                    value,
                    True,
                    (255, 193, 92) if self.debug_mode else (112, 123, 139)
                )
                self.screen.blit(
                    value_surface,
                    (
                        rect.right - value_surface.get_width() - 20,
                        rect.centery - value_surface.get_height() // 2
                    )
                )
            elif index == 5:
                value_surface = self.small_font.render(
                    f"<  {self.t('language_name')}  >",
                    True,
                    (113, 183, 255)
                )
                self.screen.blit(
                    value_surface,
                    (
                        rect.right - value_surface.get_width() - 20,
                        rect.centery - value_surface.get_height() // 2
                    )
                )
            else:
                arrow = self.menu_button_font.render("<", True, (113, 183, 255))
                self.screen.blit(
                    arrow,
                    (rect.right - arrow.get_width() - 24, rect.centery - arrow.get_height() // 2)
                )

        hint = self.small_font.render(
            self.t("options_hint"),
            True,
            (126, 140, 159)
        )
        self.screen.blit(
            hint,
            (panel_x + 38, panel_rect.bottom - 42)
        )

    # ------------------------------------------------------------------
    # Pause menu
    # ------------------------------------------------------------------

    def pause_loop(self) -> None:

        while self.state == "paused" and self.running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False
                    return

                if event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.size)
                    continue

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        if self.pause_view == "options":
                            self.pause_view = "main"
                        else:
                            self.resume_match()
                            return

                    elif self.pause_view == "main":

                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.pause_selection = (
                                self.pause_selection - 1
                            ) % len(PAUSE_MENU_ITEMS)

                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.pause_selection = (
                                self.pause_selection + 1
                            ) % len(PAUSE_MENU_ITEMS)

                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.activate_pause_option()

                    else:
                        self.handle_options_key(event.key, "pause")

                if self.pause_view == "main":

                    if event.type == pygame.MOUSEMOTION:
                        self.select_pause_item_at(event.pos)

                    if (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                        and self.select_pause_item_at(event.pos)
                    ):
                        self.activate_pause_option()

                elif self.pause_view == "options":

                    if event.type == pygame.MOUSEMOTION:
                        self.select_option_at(event.pos)

                    if (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                        and self.select_option_at(event.pos)
                    ):
                        self.activate_selected_option("pause")

            if self.state != "paused" or not self.running:
                return

            self.draw_pause_menu()
            self.clock.tick(config.FPS)

    def select_pause_item_at(self, position: Coordinate) -> bool:

        for index, rect in enumerate(self.pause_item_rects):
            if rect.collidepoint(position):
                self.pause_selection = index
                return True

        return False

    def activate_pause_option(self) -> None:

        selected = PAUSE_MENU_ITEMS[self.pause_selection]

        if selected == "pause_continue":
            self.resume_match()

        elif selected == "menu_options":
            self.options_selection = 0
            self.pause_view = "options"

        elif selected == "pause_main_menu":
            self.return_to_main_menu()

        elif selected == "menu_quit":
            self.running = False

    def draw_pause_menu(self) -> None:

        width, height = self.screen.get_size()
        self.draw_pause_backdrop(width, height)

        if self.pause_view == "options":
            self.draw_pause_options(width, height)
            pygame.display.flip()
            return

        panel_width = min(580, max(390, int(width * 0.52)))
        panel_height = min(650, max(540, height - 60))
        panel_rect = pygame.Rect(
            (width - panel_width) // 2,
            (height - panel_height) // 2,
            panel_width,
            panel_height
        )
        self.draw_glass_panel(panel_rect, fill=(7, 12, 20, 240))

        status_surface = self.small_font.render(
            self.t("match_paused"),
            True,
            (113, 183, 255)
        )
        self.screen.blit(
            status_surface,
            status_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 35))
        )

        title_surface = self.game_over_font.render(
            self.t("paused"),
            True,
            (248, 250, 255)
        )
        self.screen.blit(
            title_surface,
            title_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 81))
        )

        accent = pygame.Rect(panel_rect.centerx - 34, panel_rect.y + 112, 68, 4)
        pygame.draw.rect(self.screen, (68, 156, 255), accent, border_radius=2)

        human = self.players[0] if self.players else None
        mode = self.current_mode()
        pause_mode_label = self.mode_display_label()
        if mode == "Territory":
            pause_mode_label = (
                f"{pause_mode_label} · "
                + self.t(
                    "territory_target",
                    percent=self.territory_target_percent()
                )
            )
        stat_values = (
            (
                self.t("mode"),
                pause_mode_label
            ),
            (
                self.t("lives"),
                self.t("infinite")
                if mode == "Territory"
                else str(human.lives if human else 0)
            ),
            (self.t("territories"), str(self.territory_counts.get(0, 0)))
        )
        stats_rect = pygame.Rect(
            panel_rect.x + 34,
            panel_rect.y + 132,
            panel_rect.width - 68,
            58
        )
        stat_width = stats_rect.width / len(stat_values)
        for index, (label, value) in enumerate(stat_values):
            stat_rect = pygame.Rect(
                round(stats_rect.x + index * stat_width),
                stats_rect.y,
                round(stat_width),
                stats_rect.height
            )
            if index > 0:
                pygame.draw.line(
                    self.screen,
                    (55, 70, 89),
                    (stat_rect.left, stat_rect.y + 7),
                    (stat_rect.left, stat_rect.bottom - 7)
                )
            label_surface = self.small_font.render(label, True, (126, 140, 159))
            value_surface = self.menu_heading_font.render(value, True, (239, 244, 251))
            self.screen.blit(
                label_surface,
                label_surface.get_rect(center=(stat_rect.centerx, stat_rect.y + 11))
            )
            self.screen.blit(
                value_surface,
                value_surface.get_rect(center=(stat_rect.centerx, stat_rect.y + 38))
            )

        self.pause_item_rects = []
        item_y = panel_rect.y + 210
        item_height = 60
        item_gap = 12

        for index, label_key in enumerate(PAUSE_MENU_ITEMS):
            rect = pygame.Rect(
                panel_rect.x + 36,
                item_y + index * (item_height + item_gap),
                panel_rect.width - 72,
                item_height
            )
            self.pause_item_rects.append(rect)
            selected = index == self.pause_selection
            fill = (25, 38, 55, 248) if selected else (14, 22, 33, 226)
            border = (83, 166, 255) if selected else (58, 72, 91)
            pygame.draw.rect(self.screen, fill, rect, border_radius=13)
            pygame.draw.rect(
                self.screen,
                border,
                rect,
                2 if selected else 1,
                border_radius=13
            )

            surface = self.menu_button_font.render(
                self.t(label_key),
                True,
                (248, 250, 255) if selected else (196, 205, 218)
            )
            self.screen.blit(
                surface,
                (rect.x + 20, rect.centery - surface.get_height() // 2)
            )
            marker = self.menu_button_font.render(
                ">" if index != 3 else "×",
                True,
                (113, 183, 255) if index != 3 else (232, 105, 112)
            )
            self.screen.blit(
                marker,
                (rect.right - marker.get_width() - 22, rect.centery - marker.get_height() // 2)
            )

        hint_surface = self.small_font.render(
            self.t("pause_hint"),
            True,
            (126, 140, 159)
        )
        self.screen.blit(
            hint_surface,
            hint_surface.get_rect(
                center=(panel_rect.centerx, panel_rect.bottom - 28)
            )
        )

        pygame.display.flip()

    def draw_pause_options(self, width: int, height: int) -> None:

        self.pause_item_rects = []
        self.draw_options_panel(width, height, "pause")

    def draw_pause_backdrop(self, width: int, height: int) -> None:

        if self.pause_background is not None:
            background = self.pause_background
            if background.get_size() != (width, height):
                background = pygame.transform.smoothscale(background, (width, height))
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill((5, 9, 15))

        veil = pygame.Surface((width, height), pygame.SRCALPHA)
        veil.fill((2, 6, 12, 184))
        pygame.draw.rect(
            veil,
            (12, 35, 58, 52),
            pygame.Rect(0, 0, width, max(1, height // 3))
        )
        self.screen.blit(veil, (0, 0))

    # ------------------------------------------------------------------
    # Game Over
    # ------------------------------------------------------------------

    def game_over_loop(self) -> None:

        while (
            self.state == "game_over"
            and
            self.running
        ):

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    self.running = False
                    return

                if event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.size)
                    continue

                if (
                    event.type == pygame.KEYDOWN
                    and
                    event.key == pygame.K_ESCAPE
                ):

                    self.running = False
                    return

                if (
                    event.type == pygame.KEYDOWN
                    and
                    event.key == pygame.K_RETURN
                ):

                    self.start_match()
                    return

            self.draw_game_over()

            self.clock.tick(
                config.FPS
            )

    def draw_game_over(self) -> None:

        self.screen.fill(
            config.COLORS["background"]
        )

        width, height = self.screen.get_size()

        title_surface = self.game_over_font.render(
            self.game_over_title,
            True,
            self.game_over_color
        )

        self.screen.blit(
            title_surface,
            (
                width // 2 - title_surface.get_width() // 2,
                height // 2 - 130
            )
        )

        divider = pygame.Rect(width // 2 - 120, height // 2 - 45, 240, 3)
        pygame.draw.rect(self.screen, self.game_over_color, divider)

        message_surface = self.title_font.render(
            self.status_message,
            True,
            config.COLORS["white"]
        )
        self.screen.blit(
            message_surface,
            (
                width // 2 - message_surface.get_width() // 2,
                height // 2 - 10
            )
        )

        hint_surface = self.primary_font.render(
            self.t("again_hint"),
            True,
            config.COLORS["muted"]
        )
        self.screen.blit(
            hint_surface,
            (
                width // 2 - hint_surface.get_width() // 2,
                height // 2 + 75
            )
        )

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:

        while self.running:

            if self.state == "menu":

                self.menu_loop()

            elif self.state == "playing":

                self.playing_loop()

            elif self.state == "paused":

                self.pause_loop()

            elif self.state == "game_over":

                self.game_over_loop()

            elif self.state == "editor":

                self.editor_loop()

        self.save_settings()
        pygame.quit()

        sys.exit(0)


def main() -> None:

    game = CubulusGame()

    game.run()


if __name__ == "__main__":
    main()
