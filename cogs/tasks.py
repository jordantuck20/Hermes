# cogs/tasks.py
import logging

import discord
from discord.ext import commands, tasks

from bot import config_manager, game_manager, news_manager, subscription_manager
from utils.embed_manager import EmbedManager

logger = logging.getLogger(__name__)
embed_manager = EmbedManager(game_manager)


class UpdateChecker(commands.Cog):
    def __init__(self, bot):
        """
        Initializes the UpdateChecker cog.

        This cog handles the bot's primary recurring rask of checking for and
        sending new game news updates to subscribed guilds.

        Args:
            bot (commands.Bot): The bot instance.
        """
        self.bot = bot
        self.config_manager = config_manager
        self.subscription_manager = subscription_manager
        self.news_manager = news_manager
        self.embed_manager = embed_manager
        self.game_manager = game_manager

        self.check_for_updates.start()

    def cog_unload(self):
        """
        Performs cleanup when the cog is unloaded.

        This method ensures the background task is properly cancelled to
        prevent it from running after the bot shuts down.
        """
        self.check_for_updates.cancel()

    @tasks.loop(minutes=15)
    async def check_for_updates(self):
        """
        Periodically checks for new game news for subscribed guilds.

        This task runs every 15 minutes, iterates through all guilds, and
        sends news updates for any subscribed games that have new news.
        """

        await self.bot.wait_until_ready()
        if not self.bot.is_ready():
            return

        for guild in self.bot.guilds:
            try:
                channel_id = await self.config_manager.get_guild_channel_id(guild.id)
                if not channel_id:
                    logger.debug(
                        f"Guild {guild.name} ({guild.id}) has no update channel configured. Skipping."
                    )
                    continue

                channel = self.bot.get_channel(channel_id)
                if not channel:
                    logger.warning(
                        f"Configured channel {channel_id} not found for guild {guild.name} ({guild.id}. Skipping.)"
                    )
                    continue

                subscribed_appids = await self.subscription_manager.get_subscriptions(
                    guild.id
                )

                if not subscribed_appids:
                    logger.debug(
                        f"Guild {guild.name} ({guild.id}) has no active subscriptions. Skipping."
                    )
                    continue

                for appid in subscribed_appids:
                    newsitems = self.news_manager.fetch_latest_news(appid, count=1)
                    if not newsitems:
                        logger.debug(
                            f"No new news for appid {appid} for guild {guild.id}."
                        )
                        continue

                    latest_news = newsitems[0]
                    latest_news_gid = int(latest_news["gid"])

                    last_gid_stored = await self.news_manager.get_last_news_id(
                        guild.id, appid
                    )

                    if last_gid_stored and latest_news_gid <= last_gid_stored:
                        logger.debug(
                            f"News GID {latest_news_gid} for appid {appid} is not newer than stored {last_gid_stored} for guild {guild.id}. Skipping."
                        )
                        continue

                    await self.news_manager.save_last_news_id(
                        guild.id, appid, str(latest_news_gid)
                    )

                    embed = self.embed_manager.format_news_embed(latest_news, appid)
                    message = self.embed_manager.get_news_message(latest_news, appid)

                    try:
                        await channel.send(message, embed=embed)
                        logger.info(
                            f"Sent new news for appid {appid} (GID: {latest_news_gid}) to guild {guild.id}."
                        )
                    except discord.Forbidden:
                        logger.warning(
                            f"Bot lacks permissions to send messages to channel {channel.name} ({channel.id}) in guild {guild.name} ({guild.id})."
                        )
                    except discord.HTTPException as http_exc:
                        logger.error(
                            f"Failed to send message to guild {guild.id} channel {channel.id}: {http_exc}",
                            exc_info=True,
                        )

            except Exception as e:
                logger.error(
                    f"Unhandled exception in check_for_updates for guild {guild.id}: {e}",
                    exc_info=True,
                )


async def setup(bot):
    """
    Adds the UpdateChecker cog tot he bot.

    This is the entry point for the cog, called by `bot.load_extension`.
    """
    await bot.add_cog(UpdateChecker(bot))
