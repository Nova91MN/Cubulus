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

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def menu_loop(self) -> None:

        while (
            self.state == "menu"
            and
            self.running
        ):

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    self.running = False
                    return

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.running = False
                        return

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

                        self.start_match()

            self.draw_menu()

            self.clock.tick(
                config.FPS
            )

    def draw_menu(self) -> None:

        self.screen.fill(
            config.COLORS["background"]
        )

        width, height = self.screen.get_size()

        title = self.title_font.render(
            "Cubulus v0.0.4 Demo",
            True,
            config.COLORS["white"]
        )

        self.screen.blit(
            title,
            (
                width // 2
                - title.get_width() // 2,
                height // 2 - 170
            )
        )

        mode_text = (
            f"Modus (M): "
            f"{config.GAME_MODES[self.mode_index]}"
        )

        color_text = (
            f"Farbe (C): "
            f"{config.PLAYER_COLOR_OPTIONS[self.color_index]}"
        )

        hint_text = (
            "ENTER: Starten  |  ESC: Beenden"
        )

        self.screen.blit(
            self.primary_font.render(
                mode_text,
                True,
                config.COLORS["white"]
            ),
            (width // 2 - 170, height // 2 - 50)
        )

        self.screen.blit(
            self.primary_font.render(
                color_text,
                True,
                config.COLORS["white"]
            ),
            (width // 2 - 170, height // 2 - 10)
        )

        self.screen.blit(
            self.primary_font.render(
                hint_text,
                True,
                config.COLORS["white"]
            ),
            (width // 2 - 170, height // 2 + 50)
        )

        zoom_hint = self.small_font.render(
            "Im Spiel: Mausrad oder +/- zum Zoomen, 0 zum Zurücksetzen",
            True,
            config.COLORS["muted"]
        )
        self.screen.blit(
            zoom_hint,
            (width // 2 - zoom_hint.get_width() // 2, height - 70)
        )

        pygame.display.flip()

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

                self.running = False
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

        highest = (
            max(counts.values())
            if counts
            else 0
        )

        leaders = [
            player
            for player in self.players
            if (
                counts.get(
                    player.player_id,
                    0
                ) == highest
                and
                player.alive
            )
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

        self.screen.fill(
            config.COLORS["background"]
        )

        self.draw_board()

        self.draw_players()

        self.draw_damage_flash()

        self.draw_ui_panel()

        pygame.display.flip()

    def draw_board(self) -> None:

        if not self.board:
            return

        viewport = self.board_viewport()
        cell_size = config.CELL_SIZE * self.camera_zoom
        origin_x = viewport.centerx - self.camera_x * cell_size
        origin_y = viewport.centery - self.camera_y * cell_size

        board_height = len(self.board)
        board_width = len(self.board[0])

        first_x = max(0, int(math.floor((viewport.left - origin_x) / cell_size)))
        first_y = max(0, int(math.floor((viewport.top - origin_y) / cell_size)))
        last_x = min(board_width, int(math.ceil((viewport.right - origin_x) / cell_size)))
        last_y = min(board_height, int(math.ceil((viewport.bottom - origin_y) / cell_size)))
        gap = max(1, int(round(cell_size * 0.09)))

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
                color = config.COLORS.get(
                    row[x],
                    config.COLORS["neutral"]
                )
                pygame.draw.rect(self.screen, color, rect)

        self.screen.set_clip(previous_clip)

    def board_viewport(self) -> pygame.Rect:

        width, height = self.screen.get_size()
        return pygame.Rect(
            0,
            config.TOP_HUD_HEIGHT,
            width,
            max(
                1,
                height - config.TOP_HUD_HEIGHT - config.BOTTOM_HUD_HEIGHT
            )
        )

    def cell_screen_rect(self, x: int, y: int) -> pygame.Rect:

        viewport = self.board_viewport()
        cell_size = config.CELL_SIZE * self.camera_zoom
        origin_x = viewport.centerx - self.camera_x * cell_size
        origin_y = viewport.centery - self.camera_y * cell_size
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

            pygame.draw.rect(
                self.screen,
                color,
                rect
            )

            border_width = max(1, min(3, rect.width // 6))
            pygame.draw.rect(
                self.screen,
                config.COLORS["white"],
                rect,
                border_width
            )

        self.screen.set_clip(previous_clip)

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
        human_lives = self.players[0].lives if self.players else 0

        lives_surface = self.hud_font.render(
            f"Leben: {human_lives}",
            True,
            config.COLORS["white"]
        )
        shadow_surface = self.hud_font.render(
            f"Leben: {human_lives}",
            True,
            (65, 65, 65)
        )
        self.screen.blit(shadow_surface, (14, 15))
        self.screen.blit(lives_surface, (12, 13))

        remaining = self.remaining_time()
        if remaining is not None:
            timer = self.hud_font.render(
                f"Zeit: {remaining}s",
                True,
                config.COLORS["white"]
            )
            self.screen.blit(timer, (width - timer.get_width() - 14, 13))

        panel_rect = pygame.Rect(
            0,
            height - config.BOTTOM_HUD_HEIGHT,
            width,
            config.BOTTOM_HUD_HEIGHT
        )
        pygame.draw.rect(self.screen, config.COLORS["panel"], panel_rect)

        color_labels = (
            ("Rot", "red"),
            ("Gelb", "yellow"),
            ("Grün", "green"),
            ("Blau", "blue")
        )
        counts_by_color = {
            player.color: self.territory_counts.get(player.player_id, 0)
            for player in self.players
        }
        territory_text = "Gebiete - " + " | ".join(
            f"{label}: {counts_by_color.get(color, 0)}"
            for label, color in color_labels
        )
        territory_surface = self.hud_font.render(
            territory_text,
            True,
            config.COLORS["white"]
        )
        text_position = (
            width // 2 - territory_surface.get_width() // 2,
            panel_rect.centery - territory_surface.get_height() // 2 - 2
        )
        self.screen.blit(territory_surface, text_position)

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

            elif self.state == "game_over":

                self.game_over_loop()

        pygame.quit()

        sys.exit(0)


def main() -> None:

    game = CubulusGame()

    game.run()


if __name__ == "__main__":
    main()
