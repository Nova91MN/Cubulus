import asyncio
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


try:
    import pygame  # noqa: F401
except ModuleNotFoundError:
    pygame_stub = types.ModuleType("pygame")
    pygame_stub.Rect = type("Rect", (), {})
    pygame_stub.Surface = type("Surface", (), {})
    sys.modules["pygame"] = pygame_stub

import config  # noqa: E402
from main import APP_VERSION, CubulusGame, Player, TRANSLATIONS  # noqa: E402


class MapLoadingTests(unittest.TestCase):
    fixtures = Path(__file__).parent / "fixtures"

    def test_custom_dimensions_and_starts_are_used(self) -> None:
        data = CubulusGame.load_map_file(self.fixtures / "custom.json")

        game = CubulusGame.__new__(CubulusGame)
        game.map_data = data
        game.color_index = 0
        game.board = []
        game.players = []
        game.reset_board()
        game.create_players()

        self.assertEqual((8, 12), (len(game.board), len(game.board[0])))
        self.assertEqual(
            [(1, 1), (10, 1), (1, 6), (10, 6)],
            [player.start_position for player in game.players],
        )

        with (
            mock.patch("main.random.random", return_value=0.0),
            mock.patch("main.random.choice", return_value=(1, 0)),
        ):
            game.update_bots()
            game.update_bots()

        self.assertTrue(
            all(player.position[0] < 12 for player in game.players)
        )

    def test_default_starts_use_custom_map_corners(self) -> None:
        data = CubulusGame.load_map_file(self.fixtures / "default_starts.json")

        self.assertEqual([[0, 0], [6, 0], [0, 4], [6, 4]], data["player_starts"])

    def test_invalid_start_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the map"):
            CubulusGame.load_map_file(self.fixtures / "invalid_start.json")

    def test_obstacles_are_normalized_and_block_movement(self) -> None:
        data = CubulusGame.load_map_file(self.fixtures / "obstacles.json")
        self.assertEqual([[1, 0], [2, 2]], data["obstacles"])

        game = CubulusGame.__new__(CubulusGame)
        game.map_data = data
        game.color_index = 0
        game.player_name = "Nova"
        game.board = []
        game.players = []
        game.reset_board()
        game.create_players()

        human = game.players[0]
        self.assertFalse(game.try_move_player(human, 1, 0))
        self.assertEqual((0, 0), human.position)
        self.assertEqual("obstacle", game.board[0][1])

    def test_editor_data_contains_sorted_obstacles(self) -> None:
        game = CubulusGame.__new__(CubulusGame)
        game.editor_name = "Test Level"
        game.editor_width = 8
        game.editor_height = 6
        game.editor_starts = [(0, 0), (7, 0), (0, 5), (7, 5)]
        game.editor_obstacles = {(4, 3), (1, 1), (3, 1)}

        self.assertEqual(
            [[1, 1], [3, 1], [4, 3]],
            game.editor_map_data()["obstacles"],
        )


class SettingsTests(unittest.TestCase):
    def test_player_name_and_difficulty_are_saved(self) -> None:
        game = CubulusGame.__new__(CubulusGame)
        game.settings_path = Path("settings.json")
        game.auto_movement_enabled = True
        game.preferred_camera_zoom = 3.0
        game.screen = mock.Mock()
        game.screen.get_size.return_value = (960, 720)
        game.debug_mode = False
        game.infinite_lives_enabled = True
        game.player_speed_index = config.DEBUG_PLAYER_SPEED_OPTIONS.index(2.0)
        game.game_speed_index = config.DEBUG_SPEED_OPTIONS.index(1.0)
        game.mode_index = 0
        game.color_index = 1
        game.difficulty_index = config.DIFFICULTY_LEVELS.index("Expert")
        game.player_name = "Nova"
        game.language = "de"
        game.map_path = Path("maps/default.json")

        with (
            mock.patch("builtins.open", mock.mock_open()),
            mock.patch("main.json.dump") as dump,
            mock.patch.object(Path, "mkdir"),
            mock.patch.object(Path, "replace"),
        ):
            game.save_settings()
        settings = dump.call_args.args[0]

        self.assertEqual("Nova", settings["player_name"])
        self.assertEqual(
            config.DIFFICULTY_LEVELS.index("Expert"),
            settings["difficulty_index"],
        )
        self.assertEqual("Expert", settings["difficulty"])
        self.assertTrue(settings["infinite_lives_enabled"])
        self.assertEqual(2.0, settings["player_speed"])
        self.assertEqual("1.1", APP_VERSION)

    def test_player_name_is_sanitized(self) -> None:
        self.assertEqual("Nova Player", CubulusGame.sanitize_player_name("  Nova   Player  "))
        self.assertEqual(config.PLAYER_NAMES[0], CubulusGame.sanitize_player_name(""))


class TranslationTests(unittest.TestCase):
    def test_languages_have_the_same_keys(self) -> None:
        self.assertEqual(set(TRANSLATIONS["de"]), set(TRANSLATIONS["en"]))


class BrowserCompatibilityTests(unittest.TestCase):
    def test_async_loop_dispatches_frames_cooperatively(self) -> None:
        game = CubulusGame.__new__(CubulusGame)
        game.running = True
        game.cooperative_loop = False
        frame_count = 0

        def run_frame() -> None:
            nonlocal frame_count
            frame_count += 1
            if frame_count == 2:
                game.running = False

        game.run_current_state = mock.Mock(side_effect=run_frame)
        game.save_settings = mock.Mock()

        with (
            mock.patch("main.IS_BROWSER", True),
            mock.patch.object(
                sys.modules["pygame"], "quit", create=True
            ) as quit_pygame,
        ):
            asyncio.run(game.run_async())

        self.assertEqual(2, frame_count)
        self.assertFalse(game.cooperative_loop)
        game.save_settings.assert_called_once_with()
        quit_pygame.assert_not_called()

    def test_browser_custom_map_picker_returns_a_notice(self) -> None:
        game = CubulusGame.__new__(CubulusGame)
        game.language = "en"

        with (
            mock.patch("main.IS_BROWSER", True),
            mock.patch.object(
                sys.modules["pygame"],
                "time",
                types.SimpleNamespace(get_ticks=lambda: 100),
            ),
        ):
            game.choose_custom_map()

        self.assertIn("file picker is not available", game.map_notice)
        self.assertEqual(5100, game.map_notice_until)


class DebugToolsTests(unittest.TestCase):
    @staticmethod
    def make_game() -> CubulusGame:
        game = CubulusGame.__new__(CubulusGame)
        game.mode_index = config.GAME_MODES.index("Untimed")
        game.difficulty_index = config.DIFFICULTY_LEVELS.index("Normal")
        game.language = "en"
        game.debug_mode = True
        game.infinite_lives_enabled = True
        game.player_speed_index = config.DEBUG_PLAYER_SPEED_OPTIONS.index(2.0)
        game.damage_flash_until = 0
        game.status_message = ""
        game.territory_counts = {}
        return game

    def test_debug_infinite_lives_protect_only_the_human_player(self) -> None:
        game = self.make_game()
        game.board = [
            ["yellow", "yellow"],
            ["red", "neutral"],
        ]
        human = Player(0, "Nova", (1, 1), "red", is_human=True)
        human.position = (0, 0)
        bot = Player(1, "Bot-1", (0, 0), "yellow")
        game.players = [human, bot]
        game.game_ticks = lambda: 1000

        game.resolve_collisions()

        self.assertEqual(config.PLAYER_LIVES, human.lives)
        self.assertTrue(human.alive)
        self.assertEqual((1, 1), human.position)
        self.assertEqual(1000 + config.DAMAGE_COOLDOWN_MS, human.invulnerable_until)
        self.assertEqual(
            "Nova lost no life thanks to debug mode.",
            game.status_message,
        )
        self.assertFalse(game.player_has_infinite_lives(bot))

    def test_infinite_lives_setting_is_inactive_without_debug_mode(self) -> None:
        game = self.make_game()
        game.debug_mode = False
        human = Player(0, "Nova", (0, 0), "red", is_human=True)

        self.assertFalse(game.player_has_infinite_lives(human))

    def test_player_speed_changes_only_the_human_move_interval(self) -> None:
        game = self.make_game()

        self.assertEqual(2.0, game.effective_player_speed())
        self.assertAlmostEqual(
            config.PLAYER_MOVE_INTERVAL_MS / 2.0,
            game.human_move_interval_ms(),
        )

        game.debug_mode = False
        self.assertEqual(1.0, game.effective_player_speed())
        self.assertEqual(
            float(config.PLAYER_MOVE_INTERVAL_MS),
            game.human_move_interval_ms(),
        )

    def test_auto_movement_uses_the_selected_player_speed(self) -> None:
        game = self.make_game()
        game.board = [["neutral"] * 4]
        human = Player(0, "Nova", (0, 0), "red", is_human=True)
        game.players = [human]
        game.auto_movement_enabled = True
        game.human_move_direction = (1, 0)
        game.human_last_move_ticks = 0.0
        ticks = [42]
        game.game_ticks = lambda: ticks[0]

        game.update_human_auto_movement()
        self.assertEqual((0, 0), human.position)

        ticks[0] = 43
        game.update_human_auto_movement()
        self.assertEqual((1, 0), human.position)
        self.assertEqual(config.PLAYER_MOVE_INTERVAL_MS / 2.0, game.human_last_move_ticks)



class GameOverTests(unittest.TestCase):
    def test_escape_returns_to_main_menu(self) -> None:
        game = CubulusGame.__new__(CubulusGame)
        game.state = "game_over"
        game.running = True

        keydown = object()
        escape = object()
        event = types.SimpleNamespace(type=keydown, key=escape)

        def return_to_main_menu() -> None:
            game.state = "menu"

        game.return_to_main_menu = mock.Mock(side_effect=return_to_main_menu)

        with (
            mock.patch.object(sys.modules["pygame"], "QUIT", object(), create=True),
            mock.patch.object(
                sys.modules["pygame"], "VIDEORESIZE", object(), create=True
            ),
            mock.patch.object(sys.modules["pygame"], "KEYDOWN", keydown, create=True),
            mock.patch.object(sys.modules["pygame"], "K_ESCAPE", escape, create=True),
            mock.patch.object(
                sys.modules["pygame"],
                "event",
                types.SimpleNamespace(get=lambda: [event]),
                create=True,
            ),
        ):
            game.game_over_loop()

        game.return_to_main_menu.assert_called_once_with()
        self.assertTrue(game.running)
        self.assertEqual("menu", game.state)


class BotAndColorTests(unittest.TestCase):
    def test_match_bots_receive_unique_random_names(self) -> None:
        game = CubulusGame.__new__(CubulusGame)
        game.map_data = {
            "player_starts": [[0, 0], [3, 0], [0, 3], [3, 3]],
        }
        game.color_index = 0
        game.player_name = "Nova"

        with mock.patch(
            "main.random.sample",
            return_value=["Hans", "Ute", "Cécile"],
        ) as sample:
            game.create_players()

        sample.assert_called_once_with(config.BOT_NAMES, 3)
        self.assertEqual(
            ["Nova", "Hans", "Ute", "Cécile"],
            [player.name for player in game.players],
        )

    def test_menu_arena_refreshes_names_for_each_round(self) -> None:
        game = CubulusGame.__new__(CubulusGame)
        game.language = "de"
        game.menu_round = 0

        with (
            mock.patch(
                "main.random.sample",
                return_value=["Jesus", "Hans", "Dieter", "Günther"],
            ) as sample,
            mock.patch.object(
                sys.modules["pygame"],
                "time",
                types.SimpleNamespace(get_ticks=lambda: 100),
                create=True,
            ),
        ):
            game.reset_menu_battle()

        sample.assert_called_once_with(config.BOT_NAMES, 4)
        self.assertEqual(
            ["Jesus", "Hans", "Dieter", "Günther"],
            [player.name for player in game.menu_players],
        )

    def test_player_has_more_than_the_original_four_colors(self) -> None:
        self.assertGreater(len(config.PLAYER_COLOR_OPTIONS), 4)
        for color_name in config.PLAYER_COLOR_OPTIONS:
            self.assertIn(color_name, config.COLORS)
            self.assertIn(f"color_{color_name}", TRANSLATIONS["de"])
            self.assertIn(f"color_{color_name}", TRANSLATIONS["en"])

    @staticmethod
    def make_bot_game(mode: str = "Untimed") -> tuple[CubulusGame, Player]:
        game = CubulusGame.__new__(CubulusGame)
        game.mode_index = config.GAME_MODES.index(mode)
        game.difficulty_index = config.DIFFICULTY_LEVELS.index("Normal")
        human = Player(0, "Nova", (4, 0), "red", is_human=True)
        bot = Player(1, "Bot-1", (0, 0), "yellow")
        game.players = [human, bot]
        return game, bot

    def test_bot_that_is_behind_prefers_an_adjacent_claimable_tile(self) -> None:
        game, bot = self.make_bot_game()
        game.players[0].position = (0, 0)
        bot.position = (1, 1)
        game.board = [
            ["red", "red", "red"],
            ["red", "yellow", "neutral"],
        ]

        move = game.choose_bot_move(bot, chase_chance=1.0)

        self.assertEqual((1, 0), move)

    def test_bot_that_is_behind_takes_shortest_route_to_new_territory(self) -> None:
        game, bot = self.make_bot_game()
        game.players[0].position = (2, 0)
        bot.position = (2, 1)
        game.board = [
            ["red", "red", "red", "red", "red", "red"],
            ["yellow", "yellow", "yellow", "yellow", "neutral", "red"],
        ]

        move = game.choose_bot_move(bot, chase_chance=1.0)

        self.assertEqual((1, 0), move)

    def test_territory_bot_claims_enemy_tile_during_opening(self) -> None:
        game, bot = self.make_bot_game("Territory")
        game.board = [["yellow", "red", *("neutral" for _ in range(38))]]

        move = game.choose_bot_move(bot, chase_chance=0.0)

        self.assertEqual((1, 0), move)


class TerritoryModeTests(unittest.TestCase):
    @staticmethod
    def make_game(difficulty: str = "Normal") -> CubulusGame:
        game = CubulusGame.__new__(CubulusGame)
        game.mode_index = config.GAME_MODES.index("Territory")
        game.difficulty_index = config.DIFFICULTY_LEVELS.index(difficulty)
        game.language = "de"
        game.damage_flash_until = 0
        game.status_message = ""
        game.players = []
        game.territory_counts = {}
        return game

    def test_enemy_tiles_can_be_conquered(self) -> None:
        game = self.make_game()
        game.board = [["red"]]
        player = Player(1, "Bot-1", (0, 0), "yellow")

        game.apply_tile_effect(player)

        self.assertEqual("yellow", game.board[0][0])

    def test_target_uses_playable_map_area(self) -> None:
        game = self.make_game("Beginner")
        game.board = [["neutral"] * 10 for _ in range(10)]
        game.board[0][0] = "obstacle"

        self.assertEqual(3, game.territory_target_tiles())
        self.assertEqual("2.5", game.territory_target_percent())

    def test_unique_leader_wins_after_reaching_target(self) -> None:
        game = self.make_game("Beginner")
        game.board = [["neutral"] * 10 for _ in range(10)]
        game.players = [
            Player(0, "Nova", (0, 0), "red", is_human=True),
            Player(1, "Bot-1", (9, 0), "yellow"),
            Player(2, "Bot-2", (0, 9), "green"),
            Player(3, "Bot-3", (9, 9), "blue"),
        ]
        game.territory_counts = {0: 3, 1: 2, 2: 1, 3: 1}

        self.assertIs(game.players[0], game.determine_territory_winner())

        game.territory_counts[1] = 3
        self.assertIsNone(game.determine_territory_winner())

    def test_collision_resets_without_removing_a_life(self) -> None:
        game = self.make_game()
        game.board = [
            ["red", "red"],
            ["yellow", "neutral"],
        ]
        human = Player(0, "Nova", (0, 0), "red", is_human=True)
        bot = Player(1, "Bot-1", (1, 1), "yellow")
        bot.position = human.position
        game.players = [human, bot]
        game.game_ticks = lambda: 1000

        game.resolve_collisions()

        self.assertEqual((1, 1), bot.position)
        self.assertEqual(config.PLAYER_LIVES, bot.lives)
        self.assertTrue(bot.alive)

    def test_god_mode_bots_do_not_damage_each_other(self) -> None:
        game = self.make_game("God")
        game.board = [
            ["yellow", "yellow"],
            ["green", "neutral"],
        ]
        first_bot = Player(1, "Bot-1", (1, 1), "yellow")
        second_bot = Player(2, "Bot-2", (0, 1), "green")
        first_bot.position = (0, 0)
        second_bot.position = (0, 0)
        game.players = [first_bot, second_bot]
        game.game_ticks = lambda: 1000

        game.resolve_collisions()

        self.assertEqual((0, 0), first_bot.position)
        self.assertEqual((0, 0), second_bot.position)
        self.assertEqual(config.PLAYER_LIVES, first_bot.lives)
        self.assertEqual(config.PLAYER_LIVES, second_bot.lives)

    def test_expert_and_god_share_the_same_ai_profile(self) -> None:
        self.assertEqual(
            config.DIFFICULTY_PROFILES["Expert"],
            config.DIFFICULTY_PROFILES["God"],
        )


if __name__ == "__main__":
    unittest.main()
