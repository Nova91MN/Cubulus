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

from main import CubulusGame, TRANSLATIONS  # noqa: E402


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


class TranslationTests(unittest.TestCase):
    def test_languages_have_the_same_keys(self) -> None:
        self.assertEqual(set(TRANSLATIONS["de"]), set(TRANSLATIONS["en"]))


if __name__ == "__main__":
    unittest.main()
