# tests/test_game_manager.py
import pytest  # type: ignore
import unittest
from unittest.mock import MagicMock, patch

from utils.game_manager import GameManager
from utils.bot_database import Game, get_db_session


class TestGameManager(unittest.TestCase):
    def setUp(self):
        self.patcher = patch.object(GameManager, "_load_games_from_db", autospec=True)
        self.mock_load_games = self.patcher.start()

        self.mock_session = MagicMock()
        self.get_db_session_patcher = patch(
            "utils.game_manager.get_db_session", return_value=self.mock_session
        )
        self.mock_get_db_session = self.get_db_session_patcher.start()

        self.game_manager = GameManager()

    def tearDown(self):
        self.patcher.stop()
        self.get_db_session_patcher.stop()

    def test_init_loads_games_from_db(self):
        self.patcher.stop()
        self.get_db_session_patcher.stop()

        test_session_mock = MagicMock()
        with patch(
            "utils.game_manager.get_db_session", return_value=test_session_mock
        ) as mock_get_db_session_inner:
            mock_get_db_session_inner.return_value.__enter__.return_value = (
                test_session_mock
            )

            mock_games_data = [
                Game(steam_id=1, game_name="Test Game A"),
                Game(steam_id=2, game_name="Test Game B"),
                Game(steam_id=3, game_name="Another Game C"),
            ]

            test_session_mock.query.return_value.all.return_value = mock_games_data

            game_manager_for_this_test = GameManager()

            test_session_mock.query.assert_called_once_with(Game)
            test_session_mock.query.return_value.all.assert_called_once()

            assert game_manager_for_this_test.appid_to_name == {
                1: "Test Game A",
                2: "Test Game B",
                3: "Another Game C",
            }
            assert game_manager_for_this_test.name_to_appid == {
                "test game a": 1,
                "test game b": 2,
                "another game c": 3,
            }

    def test_get_name(self):
        self.game_manager.appid_to_name = {101: "Example Game"}
        self.game_manager.name_to_appid = {"example game": 101}

        assert self.game_manager.get_name(101) == "Example Game"
        assert self.game_manager.get_name(999) == "Unknown Game"

    def test_get_appid_by_name(self):
        self.game_manager.appid_to_name = {202: "Case Sensitive Game"}
        self.game_manager.name_to_appid = {"case sensitive game": 202}

        assert self.game_manager.get_appid_by_name("Case Sensitive Game") == 202
        assert self.game_manager.get_appid_by_name("case sensitive game") == 202
        assert self.game_manager.get_appid_by_name("Non Existent") is None

    def test_add_game_new(self):
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        self.game_manager.add_game(303, "New Test Game")

        self.mock_session.add.assert_called_once()
        added_game = self.mock_session.add.call_args[0][0]
        assert added_game.steam_id == 303
        assert added_game.game_name == "New Test Game"
        self.mock_session.commit.assert_called_once()

        assert self.game_manager.get_name(303) == "New Test Game"
        assert self.game_managergame_manager.get_appid_by_name("new test game") == 303

    def test_add_game_existing_no_change(self):
        existing_game_obj = Game(steam_id=404, game_name="Existing Game")
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = (
            existing_game_obj
        )

        self.game_manager.appid_to_name = {404: "Existing Game"}
        self.game_manager.name_to_appid = {"existing game": 404}

        self.game_manager.add_game(404, "Existing Game")

        self.mock_session.add.assert_not_called()
        self.mock_session.commit.assert_not_called()

        assert self.game_manager.get_name(404) == "Existing Game"

    def test_add_game_existing_with_name_change(self):
        existing_game_obj = Game(steam_id=505, game_name="Old Name")
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = (
            existing_game_obj
        )

        self.game_manager.appid_to_name = {505: "Old Name"}
        self.game_manager.name_to_appid = {"old name": 505}

        self.game_manager.add_game(505, "New Updated Name")

        assert existing_game_obj.game_name == "New Updated Name"
        self.mock_session.commit.assert_called_once()
        self.mock_session.add.assert_not_called()

        assert self.game_manager.get_name(505) == "New Updated Name"
        assert self.game_manager.get_appid_by_name("new updated name") == 505
