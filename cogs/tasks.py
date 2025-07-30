# cogs/tasks.py
import logging

from discord.ext import commands, tasks

from bot import config_manager, game_manager, news_manager, subscription_manager
from utils.embed_manager import EmbedManager

logger = logging.getLogger(__name__)
embed_manager = EmbedManager(game_manager)


class UpdateChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_manager = config_manager
        self.subscription_manager = subscription_manager
        self.news_manager = news_manager
        self.embed_manager = embed_manager
        self.game_manager = game_manager

        self.check_for_updates.start()

    def cog_unload(self):
        self.check_for_updates.cancel()

    @tasks.loop(minutes=1)
    async def check_for_updates(self):
        for guild in self.bot.guilds:
            try:
                guild_cfg = self.config_manager.get_guild_config(guild.id)
                channel_id = guild_cfg.get("channel_id")
                if not channel_id:
                    continue

                channel = self.bot.get_channel(channel_id)
                if not channel:
                    continue

                subscribed_appids = self.subscription_manager.get_subscriptions(
                    guild.id
                )
                for appid in subscribed_appids:
                    newsitems = self.news_manager.fetch_latest_news(appid, count=1)
                    if not newsitems:
                        continue

                    latest_news = newsitems[0]
                    last_gid = self.news_manager.get_last_news_id(guild.id, appid)

                    if latest_news["gid"] == last_gid:
                        continue

                    self.news_manager.save_last_news_id(
                        guild.id, appid, latest_news["gid"]
                    )

                    embed = self.embed_manager.format_news_embed(latest_news, appid)
                    message = self.embed_manager.get_news_message(latest_news, appid)

                    await channel.send(message, embed=embed)
            except Exception as e:
                logger.error(
                    f"Error in check_for_updates for guild {guild.id}: {e}",
                    exc_info=True,
                )


async def setup(bot):
    await bot.add_cog(UpdateChecker(bot))
