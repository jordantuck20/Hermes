# utils/news_manager.py
import logging
from typing import Any, Dict, List, Optional

from utils.bot_database import Subscription, get_db_session
from utils.steam_api import fetch_steam_news

logger = logging.getLogger(__name__)


class NewsManager:
    def __init__(self):
        """
        Initializes the NewsManager for handling Steam news updates.

        This class provides methods for fetching news from the Steam API and
        for tracking which news items have been sent to subscribed guilds,
        using the database for persistence.
        """
        logger.info("NewsManager initialized for database operations.")

    async def get_last_news_id(self, guild_id: int, appid: int) -> Optional[int]:
        """
        Retrieves the last recorded news GID for a specific game and guild.

        This method queries the `subscriptions` table to find the unique ID of the
        last news item that was successfully sent for a given game and guild.

        Args:
            guild_id (int): The unique ID of the Discord guild (server).
            appid (int): The Steam Application ID for the game.

        Returns:
            Optional[int]: The Global ID (GID) of the last news item, or None if the subscription does not exist or has no GID saved.
        """

        with get_db_session() as session:
            subscription = (
                session.query(Subscription)
                .filter_by(server_id=guild_id, steam_id=appid)
                .first()
            )

            if subscription:
                return subscription.last_news_item_timestamp
            return None

    async def save_last_news_id(self, guild_id: int, appid: int, news_gid: str) -> None:
        """
        Saves (updates) the GID of the last news item sent for a subscription.

        This method finds the subscription for a given guild and app ID and updates
        the `last_news_item_timestamp` in the database.

        Args:
            guild_id (int): The unique ID of the Discord guild (server).
            appid (int): The Steam Application ID for the game.
            news_gid (str): The Global ID (GID) of the news item to save.
        """

        with get_db_session() as session:
            try:
                subscription = (
                    session.query(Subscription)
                    .filter_by(server_id=guild_id, steam_id=appid)
                    .first()
                )

                if subscription:
                    subscription.last_news_item_timestamp = int(news_gid)
                    session.commit()
                    logger.info(
                        f"Saved last news GID {news_gid} for guild {guild_id}, appid {appid}."
                    )

                else:
                    logger.warning(
                        f"Attempted to save last news GID for non-existent subscription (guild: {guild_id}, appid: {appid})."
                    )

            except Exception as e:
                session.rollback()
                logger.error(
                    f"Failed to save last news GID {news_gid} for guild {guild_id}, appid {appid}: {e}",
                    exc_info=True,
                )

    def fetch_latest_news(seld, appid: int, count: int = 1) -> List[Dict[str, Any]]:
        """
        Fetches the latest news items for a given app ID from the Steam API.

        Args:
            appid (int): The Steam Application ID for the game.
            count (int, optional): The number of news items to fetch. Defaults to 1.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a news item. Returns an empty list on error.
        """

        return fetch_steam_news(appid, count=count)
