# cogs/admin.py
import discord
from discord.ext import commands

from bot import config_manager, game_manager


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        """
        Initializes the AdminCommands cog.

        This cog handles administrative commands for the bot, such as setting the
        news channel and reloading game data from the database.

        Args:
            bot (commands.Bot): The bot instance.
        """
        self.bot = bot
        self.config_manager = config_manager
        self.game_manager = game_manager

    @commands.command(name="setchannel")
    @commands.has_permissions(manage_guild=True)
    async def setchannel(self, ctx, channel: discord.TextChannel = None):
        """
        Sets the news update channel for the server.

        This command requires 'Manage Guild' permissions. The channel is saved
        to the database for persistent storage.

        Args:
            ctx (commands.Contexdt): The context in which the command was called.
            channel (discord.TextChannel, optional): The channel to set. Defaults to the current channel.
        """
        guild_id = ctx.guild.id
        channel = channel or ctx.channel

        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return

        await self.config_manager.set_guild_channel_id(guild_id, channel.id)

        await ctx.send(f"Set {channel.mention} as the update channel for this server.")

    @commands.command(name="reloadgames")
    @commands.is_owner()
    async def reload_games(self, ctx):
        """
        Reloads the list of trackable games from the database.

        This command is restricted to the bot's owner. It clears the in-memory
        game cache and reloads the latest data from the `games` table.

        Args:
            ctx (commands.Context): The context in which the command was called.
        """
        try:
            self.game_manager.load_games_from_db()
            await ctx.send("Game list reloaded from the database!")
        except Exception as e:
            await ctx.send(f"Failed to reload game list: {e}")
            self.bot.logger.error(f"Error reloading game list: {e}", exc_info=True)


async def setup(bot):
    """
    Adds the AdminCommands cog to the bot.
    """
    await bot.add_cog(AdminCommands(bot))
