# cogs/admin.py
import discord
from discord.ext import commands

from bot import config_manager


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_manager = config_manager

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


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
