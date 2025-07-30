# utils/config_manager.py
import logging
from typing import Optional, Dict, Any

from utils.bot_database import get_db_session, DiscordServer

logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self):
        logger.info("ConfigManager initialized for database operations.")

    async def get_or_create_guild_config(
        self, guild_id: int, guild_name: str
    ) -> DiscordServer:
        """
        Retrieves a guild's configuration from the database, or creates a new one if it doesn't exist
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
        """Retrieves the configured update channel ID for a guild."""

        with get_db_session() as session:
            guild_config = (
                session.query(DiscordServer).filter_by(server_id=guild_id).first()
            )
            if guild_config:
                return guild_config.channel_id
            return None

    async def set_guild_channel_id(self, guild_id: int, channel_id: int) -> None:
        """Sets the update channel ID for a guild."""
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
