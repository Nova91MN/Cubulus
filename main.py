import json
import math
import random
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

print("Cubulus v0.0.4 Demo - Python build")

try:
    import pygame
except ImportError:
    print("pygame is not installed. Please run: pip install pygame")
    sys.exit(1)

import config


Coordinate = Tuple[int, int]
PAUSE_MENU_ITEMS = (
    "Fortsetzen",
    "Optionen",
    "Hauptmenü",
    "Beenden"
)

MENU_ITEMS = (
    "Spiel starten",
    "Spielmodus",
    "Spielfarbe",
    "Beenden"
)

MENU_GRID_WIDTH = 44
MENU_GRID_HEIGHT = 30
MENU_BOT_STEP_MS = 82


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

        self.screen = pygame.display.set_mode(
            (
                config.WINDOW_WIDTH,
                config.WINDOW_HEIGHT
            ),
            pygame.RESIZABLE
        )

        pygame.display.set_caption("Cubulus v0.0.4 Demo")

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

        self.mode_index = 0
        self.color_index = 0

        self.status_message = "Awaiting start"

        self.board: List[List[str]] = []
        self.players: List[Player] = []

        self.territory_counts: Dict[int, int] = {}

        self.map_data = self.load_map()

        self.match_start_ticks: Optional[int] = None
        self.damage_flash_until = 0
        self.game_over_title = "SPIELENDE"
        self.game_over_color = config.COLORS["white"]

        # Camera coordinates are expressed in cells. Keeping world and screen
        # units separate makes zooming smooth and leaves gameplay untouched.
        self.camera_x = 0.5
        self.camera_y = 0.5
        self.camera_zoom = config.CAMERA_START_ZOOM
        self.camera_target_zoom = config.CAMERA_START_ZOOM
        self.frame_dt = 1.0 / config.FPS

        self.pause_selection = 0
        self.pause_view = "main"
        self.pause_started_ticks: Optional[int] = None
        self.pause_item_rects: List[pygame.Rect] = []

        self.menu_selection = 0
        self.menu_item_rects: List[pygame.Rect] = []
        self.menu_board: List[List[str]] = []
        self.menu_players: List[Player] = []
        self.menu_last_step_ticks = 0
        self.menu_round = 0
        self.menu_round_reset_at: Optional[int] = None
        self.menu_battle_message = "KI-ARENA WIRD GESTARTET"
        self.menu_battle_message_until = 0
        self.menu_clash_position: Optional[Coordinate] = None
        self.menu_clash_until = 0
        self.reset_menu_battle()

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def load_map(self) -> Dict:

        # Determine the directory containing main.py.
        #
        # When running normally:
        #     C:\...\Cubulus
        #
        # When running through PyInstaller:
        #     PyInstaller makes the bundled files available relative
        #     to __file__ as well.
        base_dir = Path(__file__).resolve().parent

        # The map is therefore searched for relative to the program
        # instead of at a hard-coded location such as D:\Cubulus.
        map_path = base_dir / "maps" / "default.json"

        try:
            with open(
                map_path,
                "r",
                encoding="utf-8"
            ) as handle:

                data = json.load(handle)

            print(
                f"Loaded map: "
                f"{data.get('name', 'unknown')}"
            )

            return data

        except FileNotFoundError:

            print(
                f"Map file not found: {map_path}"
            )

            sys.exit(1)

        except json.JSONDecodeError as exc:

            print(
                f"Failed to parse map file: {exc}"
            )

            sys.exit(1)

    def reset_board(self) -> None:

        width = self.map_data.get(
            "width",
            config.GRID_WIDTH
        )

        height = self.map_data.get(
            "height",
            config.GRID_HEIGHT
        )

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

    def create_players(self) -> None:

        self.players = []

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

                name=config.PLAYER_NAMES.get(
                    pid,
                    f"Player {pid}"
                ),

                start_position=(
                    config.PLAYER_STARTS.get(
                        pid,
                        (0, 0)
                    )
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

        if current == "neutral":

            self.board[y][x] = player.color
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
        self.camera_zoom = config.CAMERA_START_ZOOM
        self.camera_target_zoom = config.CAMERA_START_ZOOM
        self.damage_flash_until = 0
        self.game_over_title = "SPIELENDE"
        self.game_over_color = config.COLORS["white"]
        self.pause_selection = 0
        self.pause_view = "main"
        self.pause_started_ticks = None

        self.match_start_ticks = (
            pygame.time.get_ticks()
        )

        self.status_message = (
            "Match running"
        )

        self.state = "playing"

    def end_match(
        self,
        message: str,
        title: str = "SPIELENDE",
        color: Optional[Tuple[int, int, int]] = None
    ) -> None:

        print(message)

        self.status_message = message
        self.game_over_title = title
        self.game_over_color = color or config.COLORS["white"]

        self.state = "game_over"

        self.match_start_ticks = None

    def pause_match(self) -> None:

        if self.state != "playing":
            return

        self.pause_started_ticks = pygame.time.get_ticks()
        self.pause_selection = 0
        self.pause_view = "main"
        self.state = "paused"

    def resume_match(self) -> None:

        if self.state != "paused":
            return

        current_ticks = pygame.time.get_ticks()
        pause_duration = (
            current_ticks - self.pause_started_ticks
            if self.pause_started_ticks is not None
            else 0
        )

        # Shift every real-time deadline by the pause duration so timers,
        # damage protection and visual effects genuinely freeze while paused.
        if self.match_start_ticks is not None:
            self.match_start_ticks += pause_duration

        for player in self.players:
            if player.invulnerable_until > 0:
                player.invulnerable_until += pause_duration

        if self.damage_flash_until > 0:
            self.damage_flash_until += pause_duration

        self.pause_started_ticks = None
        self.state = "playing"

    def return_to_main_menu(self) -> None:

        self.state = "menu"
        self.match_start_ticks = None
        self.pause_started_ticks = None
        self.status_message = "Awaiting start"
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
        names = ("NOVA", "PULSE", "BYTE", "ECHO")
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
        self.menu_battle_message = f"RUNDE {self.menu_round}"
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
                f"{alive[0].name} GEWINNT" if alive else "UNENTSCHIEDEN"
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

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.running = False
                        return

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
                        ) % len(
                            config.GAME_MODES
                        )

                    if event.key == pygame.K_c:

                        self.color_index = (
                            self.color_index + 1
                        ) % len(
                            config.PLAYER_COLOR_OPTIONS
                        )

                    if event.key == pygame.K_RETURN:

                        self.activate_menu_item()

                if event.type == pygame.MOUSEMOTION:
                    for index, rect in enumerate(self.menu_item_rects):
                        if rect.collidepoint(event.pos):
                            self.menu_selection = index
                            break

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    for index, rect in enumerate(self.menu_item_rects):
                        if rect.collidepoint(event.pos):
                            self.menu_selection = index
                            self.activate_menu_item()
                            break

            self.update_menu_battle()
            self.draw_menu()

    def cycle_menu_option(self, direction: int) -> None:
        if self.menu_selection == 1:
            self.mode_index = (
                self.mode_index + direction
            ) % len(config.GAME_MODES)
        elif self.menu_selection == 2:
            self.color_index = (
                self.color_index + direction
            ) % len(config.PLAYER_COLOR_OPTIONS)

    def activate_menu_item(self) -> None:
        if self.menu_selection == 0:
            self.start_match()
        elif self.menu_selection in (1, 2):
            self.cycle_menu_option(1)
        elif self.menu_selection == 3:
            self.running = False

    def draw_menu(self) -> None:
        width, height = self.screen.get_size()

        self.draw_menu_background(width, height)
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
        panel_height = min(700, max(620, height - 80))
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
            "TACTICAL TERRITORY COMBAT",
            True,
            (113, 183, 255)
        )
        self.screen.blit(eyebrow, (panel_x + 42, panel_y + 34))

        title = self.menu_title_font.render("CUBULUS", True, (248, 250, 255))
        self.screen.blit(title, (panel_x + 36, panel_y + 52))

        subtitle = self.small_font.render(
            "Erobere das Raster. Überlebe deine Gegner.",
            True,
            (165, 177, 194)
        )
        self.screen.blit(subtitle, (panel_x + 42, panel_y + 137))

        accent_rect = pygame.Rect(panel_x + 42, panel_y + 178, 64, 4)
        pygame.draw.rect(self.screen, (68, 156, 255), accent_rect, border_radius=2)

        buttons_top = panel_y + 214
        button_width = panel_width - 84
        button_height = 62
        button_gap = 13
        self.menu_item_rects = []
        mode_labels = {"Untimed": "Endlos", "Timed": "10 Minuten"}
        color_labels = {
            "red": "Rot",
            "yellow": "Gelb",
            "green": "Grün",
            "blue": "Blau"
        }

        for index, item in enumerate(MENU_ITEMS):
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
            label = self.menu_button_font.render(item, True, label_color)
            self.screen.blit(label, (rect.x + 20, rect.centery - label.get_height() // 2))

            if index == 0:
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
            elif index == 1:
                value = mode_labels.get(
                    config.GAME_MODES[self.mode_index],
                    config.GAME_MODES[self.mode_index]
                )
                value_surface = self.small_font.render(f"‹  {value}  ›", True, (113, 183, 255))
                self.screen.blit(
                    value_surface,
                    (rect.right - value_surface.get_width() - 18, rect.centery - value_surface.get_height() // 2)
                )
            elif index == 2:
                selected_color = config.PLAYER_COLOR_OPTIONS[self.color_index]
                value = color_labels.get(selected_color, selected_color)
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

        controls = self.small_font.render(
            "↑↓ AUSWAHL     ←→ ÄNDERN     ENTER BESTÄTIGEN",
            True,
            (126, 140, 159)
        )
        self.screen.blit(
            controls,
            (panel_x + 42, panel_y + panel_height - 48)
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
        live_label = self.menu_heading_font.render("LIVE  KI-ARENA", True, (244, 247, 252))
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

            self.frame_dt = min(
                self.clock.tick(config.FPS) / 1000.0,
                0.05
            )

            self.handle_game_events()

            if self.state != "playing" or not self.running:
                return

            self.update_game_state()

            self.draw_gameplay()

    def handle_game_events(self) -> None:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False
                return

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

                    human.move(
                        dx,
                        dy,
                        config.GRID_WIDTH,
                        config.GRID_HEIGHT
                    )

                    self.apply_tile_effect(
                        human
                    )

            if event.type == pygame.MOUSEWHEEL:
                self.change_zoom(
                    event.y * config.CAMERA_ZOOM_STEP
                )

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

        self.update_bots()

        self.resolve_collisions()

        self.update_camera()

        self.territory_counts = (
            self.compute_territories()
        )

        self.check_victory_conditions()

    def update_bots(self) -> None:

        for player in self.players[1:]:

            if not player.alive:
                continue

            if (
                random.random()
                <=
                config.BOT_MOVE_CHANCE
            ):

                dx, dy = random.choice(
                    [
                        (0, -1),
                        (0, 1),
                        (-1, 0),
                        (1, 0)
                    ]
                )

                player.move(
                    dx,
                    dy,
                    config.GRID_WIDTH,
                    config.GRID_HEIGHT
                )

                self.apply_tile_effect(
                    player
                )

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
        current_ticks = pygame.time.get_ticks()

        for occupants in positions.values():

            if len(occupants) < 2:
                continue

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

                if not loser.take_damage(current_ticks):
                    continue

                if loser.is_human:
                    self.damage_flash_until = (
                        current_ticks + config.DAMAGE_FLASH_MS
                    )

                if not loser.alive:

                    self.status_message = (
                        f"{loser.name} eliminated."
                    )

                else:

                    # Moving a damaged player to the spawn point prevents one
                    # collision from draining several lives in succession.
                    loser.position = loser.start_position
                    self.apply_tile_effect(loser)
                    self.status_message = (
                        f"{loser.name} lost a life. "
                        f"{loser.lives} remaining."
                    )

    def check_victory_conditions(
        self
    ) -> None:

        alive = self.alive_players()

        if self.players and not self.players[0].alive:

            self.end_match(
                "Du hast alle 3 Leben verloren.",
                title="GAME OVER",
                color=config.COLORS["red"]
            )

            return

        if not alive:

            self.end_match(
                "Alle Spieler wurden eliminiert."
            )

            return

        if len(alive) == 1:

            winner = alive[0]

            message = (
                f"{winner.name} wins!"
            )

            self.end_match(
                message,
                title=(
                    "SIEG"
                    if winner.is_human
                    else "SPIELENDE"
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
                pygame.time.get_ticks()
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

            return (
                "Time expired. No winner."
            )

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

            return (
                f"Time expired. "
                f"{leaders[0].name} wins!"
            )

        if leaders:

            names = ", ".join(
                player.name
                for player in leaders
            )

            return (
                f"Time expired. "
                f"Tie between: {names}"
            )

        return (
            "Time expired. No winner."
        )

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
            pygame.time.get_ticks()
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

        pygame.display.flip()

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
                    (17, 24, 34)
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

            current_ticks = pygame.time.get_ticks()
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

        remaining = self.damage_flash_until - pygame.time.get_ticks()
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
            "MATCH LÄUFT",
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

        mode = config.GAME_MODES[self.mode_index]
        mode_label = "10 MINUTEN" if mode == "Timed" else "ENDLOS"
        remaining = self.remaining_time()
        match_value = (
            f"{remaining // 60:02d}:{remaining % 60:02d}"
            if remaining is not None
            else mode_label
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
            "ESC  PAUSE",
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
            name = "DU" if player.is_human else player.name.upper()
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
                "GEBIETE",
                True,
                (126, 140, 159)
            )
            self.screen.blit(
                label_surface,
                (content_x + score_surface.get_width() + 8, item_rect.y + 55)
            )

            pip_y = item_rect.y + (63 if compact else 72)
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
    # Pause menu
    # ------------------------------------------------------------------

    def pause_loop(self) -> None:

        while self.state == "paused" and self.running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False
                    return

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

                        if event.key in (
                            pygame.K_LEFT,
                            pygame.K_a,
                            pygame.K_MINUS,
                            pygame.K_KP_MINUS
                        ):
                            self.change_zoom(-config.CAMERA_ZOOM_STEP)

                        elif event.key in (
                            pygame.K_RIGHT,
                            pygame.K_d,
                            pygame.K_PLUS,
                            pygame.K_EQUALS,
                            pygame.K_KP_PLUS
                        ):
                            self.change_zoom(config.CAMERA_ZOOM_STEP)

                        elif event.key in (pygame.K_0, pygame.K_KP0):
                            self.camera_target_zoom = config.CAMERA_START_ZOOM

                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.pause_view = "main"

                if self.pause_view == "main":

                    if event.type == pygame.MOUSEMOTION:
                        self.select_pause_item_at(event.pos)

                    if (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                        and self.select_pause_item_at(event.pos)
                    ):
                        self.activate_pause_option()

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

        if selected == "Fortsetzen":
            self.resume_match()

        elif selected == "Optionen":
            self.pause_view = "options"

        elif selected == "Hauptmenü":
            self.return_to_main_menu()

        elif selected == "Beenden":
            self.running = False

    def draw_pause_menu(self) -> None:

        self.screen.fill(config.COLORS["background"])
        width, height = self.screen.get_size()

        if self.pause_view == "options":
            self.draw_pause_options(width, height)
            pygame.display.flip()
            return

        title_surface = self.title_font.render(
            "PAUSIERT",
            True,
            config.COLORS["white"]
        )
        self.screen.blit(
            title_surface,
            (
                width // 2 - title_surface.get_width() // 2,
                max(72, int(height * 0.13))
            )
        )

        self.pause_item_rects = []
        item_y = int(height * 0.30)
        item_gap = max(72, int(height * 0.10))

        for index, label in enumerate(PAUSE_MENU_ITEMS):
            color = (
                config.COLORS["yellow"]
                if index == self.pause_selection
                else config.COLORS["white"]
            )
            surface = self.hud_font.render(label, True, color)
            position = (
                width // 2 - surface.get_width() // 2,
                item_y + index * item_gap
            )
            self.screen.blit(surface, position)
            self.pause_item_rects.append(
                surface.get_rect(topleft=position).inflate(64, 24)
            )

        hint_surface = self.small_font.render(
            "Pfeiltasten / WASD: Auswählen   •   ENTER: Bestätigen   •   ESC: Fortsetzen",
            True,
            config.COLORS["muted"]
        )
        self.screen.blit(
            hint_surface,
            (
                width // 2 - hint_surface.get_width() // 2,
                height - 55
            )
        )

        pygame.display.flip()

    def draw_pause_options(self, width: int, height: int) -> None:

        self.pause_item_rects = []
        title_surface = self.title_font.render(
            "OPTIONEN",
            True,
            config.COLORS["white"]
        )
        self.screen.blit(
            title_surface,
            (
                width // 2 - title_surface.get_width() // 2,
                max(72, int(height * 0.13))
            )
        )

        zoom_percent = round(self.camera_target_zoom * 100)
        zoom_surface = self.hud_font.render(
            f"‹   Kamera-Zoom: {zoom_percent} %   ›",
            True,
            config.COLORS["yellow"]
        )
        self.screen.blit(
            zoom_surface,
            (
                width // 2 - zoom_surface.get_width() // 2,
                int(height * 0.36)
            )
        )

        hint_surface = self.small_font.render(
            "Links / Rechts: Anpassen   •   0: Zurücksetzen   •   ESC / ENTER: Zurück",
            True,
            config.COLORS["muted"]
        )
        self.screen.blit(
            hint_surface,
            (
                width // 2 - hint_surface.get_width() // 2,
                height - 55
            )
        )

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
            "ENTER: Noch einmal  |  ESC: Beenden",
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

        pygame.quit()

        sys.exit(0)


def main() -> None:

    game = CubulusGame()

    game.run()


if __name__ == "__main__":
    main()
