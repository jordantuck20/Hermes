# tests/test_config_manager.py
import pytest  # type: ignore
import unittest
from unittest.mock import MagicMock, patch

from utils.config_manager import ConfigManager
from utils.bot_database import DiscordServer


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.mock_session_obj = MagicMock()

        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = self.mock_session_obj
        mock_context_manager.__exit__.return_value = False

        self.patcher_get_db_session = patch(
            "utils.config_manager.get_db_session", return_value=mock_context_manager
        )
        self.mock_get_db_session_func = self.patcher_get_db_session.start()

        self.config_manager = ConfigManager()

    def tearDown(self):
        self.patcher_get_db_session.stop()

    async def test_get_or_create_guild_config_new(self):
        mock_guild_id = 122333444
        mock_guild_name = "New Test Guild"

        self.mock_session_obj.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        self.mock_session_obj.refresh.return_value = None

        returned_config = self.config_manager.get_or_create_guild_config(
            mock_guild_id, mock_guild_name
        )

        self.assertIsNotNone(returned_config)
        self.assertEqual(returned_config.server_id, mock_guild_id)
        self.assertEqual(returned_config.channel_id, mock_guild_id)
        self.assertEqual(returned_config.server_name, mock_guild_name)

        self.mock_session_obj.add.assert_called_once()

        added_config = self.mock_session_obj.add.call_args[0][0]
        self.assertIsIstance(added_config, DiscordServer)
        self.assertEqual(added_config.server_id, mock_guild_id)
        self.assertEqual(added_config.channel_id, mock_guild_id)
        self.assertEqual(added_config.server_name, mock_guild_name)

        self.mock_session_obj.commit.assert_called_once()
        self.mock_session_obj.refresh.assert_called_once_with(added_config)

    async def test_get_or_create_guild_config_existing(self):
        mock_guild_id = 1234567890
        mock_guild_name = "Existing Test Guild"
        mock_existing_config = DiscordServer(
            server_id=mock_guild_id, channel_id=9876543210, server_name=mock_guild_name
        )

        self.mock_session_obj.query.return_value.filter_by.return_value.first.return_value = (
            mock_existing_config
        )

        returned_config = self.config_manager.get_or_create_guild_config(
            mock_guild_id, mock_guild_name
        )

        self.assertEqual(returned_config, mock_existing_config)
        self.mock_session_obj.query.assert_called_once_with(DiscordServer)
        self.mock_session_obj.query.return_value.filter_by.assert_called_once_with(
            server_id=mock_guild_id
        )
        self.mock_session_obj.add.assert_not_called()
        self.mock_session_obj.commit.assert_not_called()

    async def test_get_guild_channel_id_exists(self):
        mock_guild_id = 444455555
        mock_channel_id = 227777777
        mock_config = DiscordServer(server_id=mock_guild_id, channel_id=mock_channel_id)
        self.mock_session_obj.query.return_value.filter_by.return_value.first.return_value = (
            mock_config
        )

        returned_channel_id = self.config_manager.get_guild_channel_id(mock_guild_id)

        self.assertEqual(returned_channel_id, mock_channel_id)
        self.mock_session_obj.query.assert_called_once_with(DiscordServer)
        self.mock_session_obj.query.return_value.filter_by.assert_called_once_with(
            server_id=mock_guild_id
        )

    async def test_get_guild_channel_id_not_exists(self):
        mock_guild_id = 666666333
        self.mock_session_obj.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        returned_channel_id = self.config_manager.get_guild_channel_id(mock_guild_id)

        self.assertIsNone(returned_channel_id)
        self.mock_session_obj.query.assert_called_once_with(DiscordServer)

    async def test_set_guild_channel_id_new(self):
        mock_guild_id = 999999999333
        new_channel_id = 6666664444
        self.mock_session_obj.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        self.config_manager.set_guild_channel_id(mock_guild_id, new_channel_id)

        self.mock_session_obj.add.assert_called_once()
        added_config = self.mock_session_obj.add.call_args[0][0]
        self.assertIsInstance(added_config, DiscordServer)
        self.assertEqual(added_config.server_id, mock_guild_id)
        self.assertEqual(added_config.channel_id, new_channel_id)

        self.assertEqual(added_config.server_name, "Unknown Guild")
        self.mock_session_obj.commit.assert_called_once()

    async def test_set_guild_channeL_id_existing(self):
        mock_guild_id = 1444455555
        old_channel_id = 88888888333
        new_channel_id = 99999999922
        mock_config = DiscordServer(server_id=mock_guild_id, channel_id=old_channel_id)
        self.mock_session_obj.query.return_value.filter_by.return_value.first.return_value = (
            mock_config
        )

        self.config_manager.set_guild_channel_id(mock_guild_id, new_channel_id)

        self.assertEqual(mock_config.channel_id, new_channel_id)
        self.mock_session_obj.commit.assert_called_once()
        self.mock_session_obj.add.assert_not_called()
