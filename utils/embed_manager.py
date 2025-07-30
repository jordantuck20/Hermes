# utils/embed_manager.py
import discord
from utils.game_manager import GameManager


class EmbedManager:
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager

    def format_news_embed(self, latest_news: dict, appid: int) -> discord.Embed:
        game_name = self.game_manager.get_name(appid)

        embed = discord.Embed(
            title=latest_news["title"],
            description=latest_news["contents"][:300],
            url=latest_news["url"],
            color=discord.Color.blue(),
        )

        embed.set_footer(text=game_name)
        return embed

    def get_news_message(self, latest_news: dict, appid: int) -> str:
        game_name = self.game_manager.get_name(appid)
        return f"New update for {game_name} <t:{latest_news["date"]}:R>"
