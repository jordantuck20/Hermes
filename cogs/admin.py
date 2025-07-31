# cogs/admin.py
import discord
from discord.ext import commands

from bot import config_manager, game_manager


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_manager = config_manager
        self.game_manager = game_manager

    @commands.command(name="setchannel")
    @commands.has_permissions(manage_guild=True)
    async def setchannel(self, ctx, channel: discord.TextChannel = None):
        """Set the update channel for the guild."""
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
        """Reloads the list of trackable games from the databsae."""
        try:
            self.game_manager.load_games_from_db()
            await ctx.send("Game list reloaded from the database!")
        except Exception as e:
            await ctx.send(f"Failed to reload game list: {e}")
            self.bot.logger.error(f"Error reloading game list: {e}", exc_info=True)


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
