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
from main import APP_VERSION, CubulusGame, TRANSLATIONS  # noqa: E402


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
        game.game_speed_index = config.DEBUG_SPEED_OPTIONS.index(1.0)
        game.mode_index = 0
        game.color_index = 1
        game.difficulty_index = 2
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
        self.assertEqual(2, settings["difficulty_index"])
        self.assertEqual("0.2.0", APP_VERSION)

    def test_player_name_is_sanitized(self) -> None:
        self.assertEqual("Nova Player", CubulusGame.sanitize_player_name("  Nova   Player  "))
        self.assertEqual(config.PLAYER_NAMES[0], CubulusGame.sanitize_player_name(""))


class TranslationTests(unittest.TestCase):
    def test_languages_have_the_same_keys(self) -> None:
        self.assertEqual(set(TRANSLATIONS["de"]), set(TRANSLATIONS["en"]))


if __name__ == "__main__":
    unittest.main()
