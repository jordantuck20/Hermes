# utils/news_manager.py
import logging
from typing import Any, Optional, List, Dict

from utils.steam_api import fetch_steam_news

from utils.bot_database import get_db_session, Subscription


logger = logging.getLogger(__name__)


class NewsManager:
    def __init__(self):
        logger.info("NewsManager initialized for database operations.")

    async def get_last_news_id(self, guild_id: int, appid: int) -> Optional[int]:
        """
        Retrieves the last recorded news GID for a specific game and guild.
        Returns the GID (as int) if found, otherwise None.
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
        Saves (updates) the last recorded news GID for a specific game and guiild.
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
        Fetches the latest news items for a given app ID from the Steam API.\
        """

        return fetch_steam_news(appid, count=count)
