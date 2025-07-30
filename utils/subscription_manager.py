# utils/subscription_manager.py
import logging
from typing import List

from utils.bot_database import get_db_session, Subscription, DiscordServer, Game

logger = logging.getLogger(__name__)


class SubscriptionManager:
    def __init__(self):
        logger.info("SubscriptionManager initialized for database operations.")

    async def get_subscriptions(self, guild_id: int) -> List[int]:
        """Retrieves a list of app IDs to which a guild is subscribed."""

        with get_db_session() as session:
            subscriptions = (
                session.query(Subscription).filter_by(server_id=guild_id).all()
            )
            return [sub.steam_id for sub in subscriptions]

    async def add_subscription(self, guild_id: int, appid: int) -> bool:
        """
        Adds a game subscription for a guild.
        Returns True if added, False if already subscribed or an error occurs.
        """

        with get_db_session() as session:
            try:
                server = (
                    session.query(DiscordServer).filter_by(server_id=guild_id).first()
                )
                if not server:
                    logger.warning(
                        f"Attempted to add subscription for non-existent server {guild_id}."
                    )
                    return False

                game = session.query(Game).filter_by(steam_id=appid).first()
                if not game:
                    logger.warning(
                        f"Attempted to add subscription for unknown game appid {appid}. Game must be added via GameManager first."
                    )
                    return False

                existing_sub = (
                    session.query(Subscription)
                    .filter_by(server_id=guild_id, steam_id=appid)
                    .first()
                )

                if existing_sub:
                    logger.info(
                        f"Guild {guild_id} is already subscribed to appid {appid}."
                    )
                    return False

                new_subscription = Subscription(server_id=guild_id, steam_id=appid)
                session.add(new_subscription)
                session.commit()
                logger.info(
                    f"Added subscription for guild {guild_id} to appid {appid}."
                )
                return True

            except Exception as e:
                session.rollback()
                logger.error(
                    f"Failed to add subscription for guild {guild_id} and appid {appid}: {e}",
                    exc_info=True,
                )
                return False

    async def remove_subscription(self, guild_id: int, appid: int) -> bool:
        """
        Removes a game subscription from a guild.
        Returns True if removed, False if not subscribed or an error occurs.
        """

        with get_db_session() as session:
            try:
                subscription_to_remove = (
                    session.query(Subscription)
                    .filter_by(server_id=guild_id, steam_id=appid)
                    .first()
                )

                if not subscription_to_remove:
                    logger.info(f"Guild {guild_id} is not subscribed to appid {appid}.")
                    return False

                session.delete(subscription_to_remove)
                session.commit()
                logger.info(
                    f"Removed subscription for guild {guild_id} to appid {appid}."
                )
                return True

            except Exception as e:
                session.rollback()
                logger.error(
                    f"Failed to remove subscription for guild {guild_id} and appid {appid}: {e}",
                    exc_info=True,
                )
                return False
