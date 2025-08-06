# utils/embed_manager.py
import discord

from utils.game_manager import GameManager


class EmbedManager:
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager

    def format_news_embed(self, latest_news: dict, appid: int) -> discord.Embed:
        """
        Formats a Steam news item into a Discord embed.

        This method take a dictionary containing news details and an app ID,
        then formats a rich Discord embed with the news title, a truncated
        description, and a link to the full news post.

        Args:
            latest_news (dict): A dictionary containing the news item details from the Steam API.
            appid (int): The Steam Application ID for the game.

        Returns:
            discord.Embed: A formatted Discord embed object.
        """
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
        """
        Formats a simple text message for a news update.

        This method creates a human-readable text message that includes the game's
        name and a relative timestamp for the news update.

        Args:
            latest_news (dict): A dictionary containing the news item details from the Steam API.
            appid (int): The Steam Application ID for the game.

        Returns:
            str: A formatted string message ready to be sent to a Discord channel.
        """
        game_name = self.game_manager.get_name(appid)
        return f"New update for {game_name} <t:{latest_news["date"]}:R>"
