# utils/config_manager.py
import logging
from typing import Optional

from utils.bot_database import DiscordServer, get_db_session

logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self):
        """
        Manages Discord server-specific configurations in the database.

        This class provides a clean interface for interacting with the `discord_servers`
        table, handling creation, retrieval, and updates of server-level settings
        like the designated news channel.
        """
        logger.info("ConfigManager initialized for database operations.")

    async def get_or_create_guild_config(
        self, guild_id: int, guild_name: str
    ) -> DiscordServer:
        """
        Retrieves a guild's configuration from the database.

        If a configuration for the specified guild ID does not exist, a new one
        is created with default values and saved to the database.

        Args:
            guild_id (str): The unique ID of the Discord guild (server).
            guild_name (str): The name of the Discord guild.

        Returns:
            DiscordServer: The database model object for the guild's configuration.
        """

        with get_db_session() as session:
            guild_config = (
                session.query(DiscordServer).filter_by(server_id=guild_id).first()
            )

            if not guild_config:
                logger.info(
                    f"Guild config not found for {guild_name} ({guild_id}). Creating new default config."
                )
                guild_config = DiscordServer(
                    server_id=guild_id, channel_id=guild_id, server_name=guild_name
                )
                session.add(guild_config)
                session.commit()
                session.refresh(guild_config)

            return guild_config

    async def get_guild_channel_id(self, guild_id: int) -> Optional[int]:
        """
        Retrieves the configured news channel ID for a specific guild.

        Args:
            guild_id (str): The unique ID of the Discord guild (server).

        Returns:
            Optional[int]: The configured channel ID, or None if the configuration or channel ID does not exist.
        """

        with get_db_session() as session:
            guild_config = (
                session.query(DiscordServer).filter_by(server_id=guild_id).first()
            )
            if guild_config:
                return guild_config.channel_id
            return None

    async def set_guild_channel_id(self, guild_id: int, channel_id: int) -> None:
        """
        Sets the news channel ID for a specific guild.

        If the guild's configuration does not exist, a new one is created.

        Args:
            guild_id (str): The unique ID of the Discord guild (server).
            channel_id (int): The channel ID to be set as the news channel.
        """
        with get_db_session() as session:
            guild_config = (
                session.query(DiscordServer).filter_by(server_id=guild_id).first()
            )
            if guild_config:
                guild_config.channel_id = channel_id
                session.commit()
            else:
                logger.warning(
                    f"Attempted to set channel_id for non-existent guild {guild_id}. Creating it."
                )
                new_guild = DiscordServer(
                    server_id=guild_id,
                    channel_id=channel_id,
                    server_name="Unknown Guild",
                )
                session.add(new_guild)
                session.commit()
                logger.info(
                    f"Created new guild config for {guild_id} with channel {channel_id} during set operation."
                )
