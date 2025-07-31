# tests/test_game_manager.py
import pytest  # type: ignore
import unittest
from unittest.mock import MagicMock, patch

from utils.game_manager import GameManager
from utils.bot_database import Game


class TestGameManager(unittest.TestCase):
    def setUp(self):
        self.patcher_load_games = patch.object(
            GameManager, "load_games_from_db", autospec=True
        )
        self.mock_load_games = self.patcher_load_games.start()

        self.mock_session_obj = MagicMock()

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = self.mock_session_obj
        mock_context_manager.__exit__.return_value = False

        self.patcher_get_db_session = patch(
            "utils.game_manager.get_db_session", return_value=mock_context_manager
        )
        self.mock_get_db_session_func = self.patcher_get_db_session.start()

        self.game_manager = GameManager()

    def tearDown(self):
        self.patcher_load_games.stop()
        self.patcher_get_db_session.stop()

    def test_get_name(self):
        self.game_manager.appid_to_name = {
            101: "Example Game One",
            102: "Another Test Game",
        }
        self.game_manager.name_to_appid = {
            "example game one": 101,
            "another test game": 102,
        }

        self.assertEqual(self.game_manager.get_name(101), "Example Game One")
        self.assertEqual(self.game_manager.get_name(102), "Another Test Game")
        self.assertEqual(self.game_manager.get_name(000), "Unknown Game")
        self.assertEqual(self.game_manager.get_name(999), "Unknown Game")

        self.mock_session_obj.query.assert_not_called()
        self.mock_session_obj.commit.assert_not_called()

    def test_get_appid_by_name(self):
        self.game_manager.appid_to_name = {
            103: "Example Game Three",
            104: "Another Game Four",
        }
        self.game_manager.name_to_appid = {
            "example game three": 103,
            "another game four": 104,
        }

        self.assertEqual(self.game_manager.get_appid_by_name("Example Game Three"), 103)
        self.assertEqual(self.game_manager.get_appid_by_name("example game three"), 103)
        self.assertEqual(self.game_manager.get_appid_by_name("Another Game Four"), 104)
        self.assertEqual(self.game_manager.get_appid_by_name("another game four"), 104)

        self.mock_session_obj.query.assert_not_called()
        self.mock_session_obj.commit.assert_not_called()

    def test_add_game_new(self):
        self.mock_session_obj.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        self.game_manager.add_game(201, "Example Game Five")
        self.mock_session_obj.add.assert_called_once()

        added_game = self.mock_session_obj.add.call_args[0][0]
        self.assertIsInstance(added_game, Game)
        self.assertEqual(added_game.steam_id, 201)
        self.assertEqual(added_game.game_name, "Example Game Five")
        self.mock_session_obj.commit.assert_called_once()

        self.assertEqual(self.game_manager.get_name(201), "Example Game Five")
        self.assertEqual(self.game_manager.get_appid_by_name("Example Game Five"), 201)
        self.assertEqual(self.game_manager.get_appid_by_name("example game five"), 201)

    def test_add_game_existing(self):
        existing_game_obj = Game(steam_id=301, game_name="Example Game Six")
        self.mock_session_obj.query.return_value.filter_by.return_value.first.return_value = (
            existing_game_obj
        )

        self.game_manager.appid_to_name = {301: "Example Game Six"}
        self.game_manager.name_to_appid = {"example game six": 301}

        self.game_manager.add_game(301, "Example Game Six")

        self.mock_session_obj.add.assert_not_called()
        self.mock_session_obj.commit.assert_not_called()
        self.assertEqual(self.game_manager.get_name(301), "Example Game Six")
        self.assertEqual(existing_game_obj.game_name, "Example Game Six")

        self.mock_session_obj.reset_mock()

        new_name = "Updated Game Six"
        self.game_manager.add_game(301, new_name)

        self.mock_session_obj.add.assert_not_called()
        self.mock_session_obj.commit.assert_called_once()
        self.assertEqual(existing_game_obj.game_name, new_name)
        self.assertEqual(self.game_manager.get_name(301), new_name)
        self.assertEqual(self.game_manager.get_appid_by_name(new_name.lower()), 301)
