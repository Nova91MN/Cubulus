import json
import random
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

print("Cubulus v0.0.0 Demo – Python build")

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

    def __post_init__(self) -> None:
        self.reset(self.start_position, self.color)

    def reset(self, position: Coordinate, color: str) -> None:
        self.position = position
        self.color = color
        self.lives = config.PLAYER_LIVES
        self.alive = True

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

    def lose_life(self) -> None:
        if not self.alive:
            return

        self.lives -= 1

        if self.lives <= 0:
            self.alive = False


class CubulusGame:
    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode(
            (
                config.WINDOW_WIDTH,
                config.WINDOW_HEIGHT
            )
        )

        pygame.display.set_caption("Cubulus v0.0.0 Demo")

        self.clock = pygame.time.Clock()

        self.primary_font = pygame.font.SysFont(
            "consolas",
            18
        )

        self.title_font = pygame.font.SysFont(
            "consolas",
            28,
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

        self.match_start_ticks = (
            pygame.time.get_ticks()
        )

        self.status_message = (
            "Match running"
        )

        self.state = "playing"

    def end_match(
        self,
        message: str
    ) -> None:

        print(message)

        self.status_message = message

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
            (12, 12, 12)
        )

        title = self.title_font.render(
            "Cubulus v0.0.0 Demo",
            True,
            config.COLORS["white"]
        )

        self.screen.blit(
            title,
            (
                config.WINDOW_WIDTH // 2
                - title.get_width() // 2,
                120
            )
        )

        mode_text = (
            f"Mode (M): "
            f"{config.GAME_MODES[self.mode_index]}"
        )

        color_text = (
            f"Color (C): "
            f"{config.PLAYER_COLOR_OPTIONS[self.color_index]}"
        )

        hint_text = (
            "Press ENTER to start, "
            "ESC to quit"
        )

        self.screen.blit(
            self.primary_font.render(
                mode_text,
                True,
                config.COLORS["white"]
            ),
            (240, 260)
        )

        self.screen.blit(
            self.primary_font.render(
                color_text,
                True,
                config.COLORS["white"]
            ),
            (240, 300)
        )

        self.screen.blit(
            self.primary_font.render(
                hint_text,
                True,
                config.COLORS["white"]
            ),
            (240, 340)
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

            self.handle_game_events()

            self.update_game_state()

            self.draw_gameplay()

            self.clock.tick(
                config.FPS
            )

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

    def update_game_state(self) -> None:

        if not self.running:
            return

        self.update_bots()

        self.resolve_collisions()

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

                loser.lose_life()

                if not loser.alive:

                    self.status_message = (
                        f"{loser.name} eliminated."
                    )

    def check_victory_conditions(
        self
    ) -> None:

        alive = self.alive_players()

        if not alive:

            self.end_match(
                "All eliminated."
            )

            return

        if len(alive) == 1:

            winner = alive[0]

            message = (
                f"{winner.name} wins!"
            )

            self.end_match(
                message
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
            config.COLORS["neutral"]
        )

        self.draw_board()

        self.draw_players()

        self.draw_ui_panel()

        pygame.display.flip()

    def draw_board(self) -> None:

        cell_size = config.CELL_SIZE

        for y, row in enumerate(
            self.board
        ):

            for x, color_name in enumerate(
                row
            ):

                color = config.COLORS.get(
                    color_name,
                    config.COLORS["neutral"]
                )

                rect = pygame.Rect(
                    x * cell_size,
                    y * cell_size,
                    cell_size,
                    cell_size
                )

                pygame.draw.rect(
                    self.screen,
                    color,
                    rect
                )

    def draw_players(self) -> None:

        cell_size = config.CELL_SIZE

        for player in self.players:

            if not player.alive:
                continue

            color = config.COLORS.get(
                player.color,
                config.COLORS["white"]
            )

            x, y = player.position

            rect = pygame.Rect(
                x * cell_size,
                y * cell_size,
                cell_size,
                cell_size
            )

            pygame.draw.rect(
                self.screen,
                color,
                rect
            )

            self.draw_hp_indicator(
                player,
                rect
            )

    def draw_hp_indicator(
        self,
        player: Player,
        rect: pygame.Rect
    ) -> None:

        max_lives = (
            config.PLAYER_LIVES
        )

        segment_width = (
            rect.width
            /
            max_lives
        )

        y = rect.top - 6

        if y < 2:
            y = rect.bottom + 2

        for i in range(max_lives):

            life_color = (
                config.COLORS["white"]
                if i < player.lives
                else
                (80, 80, 80)
            )

            indicator_rect = pygame.Rect(
                rect.left
                + i * segment_width,

                y,

                segment_width - 1,

                4
            )

            pygame.draw.rect(
                self.screen,
                life_color,
                indicator_rect
            )

    def draw_ui_panel(self) -> None:

        lines: List[str] = []

        lines.append(
            f"Mode: "
            f"{config.GAME_MODES[self.mode_index]}"
        )

        remaining = (
            self.remaining_time()
        )

        if remaining is not None:

            lines.append(
                f"Time: {remaining}s"
            )

        lines.append(
            f"Status: "
            f"{self.status_message}"
        )

        lines.append(
            "Players:"
        )

        for player in self.players:

            territory = (
                self.territory_counts.get(
                    player.player_id,
                    0
                )
            )

            state = (
                "Alive"
                if player.alive
                else "KO"
            )

            lines.append(
                f"  {player.name} "
                f"({player.color}) - "
                f"{state}, "
                f"HP:{player.lives}, "
                f"Tiles:{territory}"
            )

        y = 6

        for line in lines:

            surface = (
                self.primary_font.render(
                    line,
                    True,
                    config.COLORS["white"]
                )
            )

            self.screen.blit(
                surface,
                (8, y)
            )

            y += (
                surface.get_height()
                + 2
            )

    # ------------------------------------------------------------------
    # Game Over
    # ------------------------------------------------------------------

    def game_over_loop(self) -> None:

        timer_start = (
            pygame.time.get_ticks()
        )

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

            self.draw_game_over()

            self.clock.tick(
                config.FPS
            )

            if (
                pygame.time.get_ticks()
                -
                timer_start
            ) > 3000:

                self.state = "menu"

                self.status_message = (
                    "Awaiting start"
                )

                break

    def draw_game_over(self) -> None:

        self.screen.fill(
            (10, 10, 10)
        )

        message_surface = (
            self.title_font.render(
                self.status_message,
                True,
                config.COLORS["white"]
            )
        )

        self.screen.blit(
            message_surface,
            (
                config.WINDOW_WIDTH // 2
                -
                message_surface.get_width() // 2,

                config.WINDOW_HEIGHT // 2
                -
                60
            )
        )

        hint_surface = (
            self.primary_font.render(
                "Returning to menu...",
                True,
                config.COLORS["white"]
            )
        )

        self.screen.blit(
            hint_surface,
            (
                config.WINDOW_WIDTH // 2
                -
                hint_surface.get_width() // 2,

                config.WINDOW_HEIGHT // 2
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