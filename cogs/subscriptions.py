# cogs/subscriptions.py
from discord.ext import commands

from bot import game_manager, subscription_manager


class SubscriptionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.subscription_manager = subscription_manager
        self.game_manager = game_manager

    @commands.command(name="listgames")
    async def list_games(self, ctx):
        guild_id = ctx.guild.id
        subs = self.subscription_manager.get_subscriptions(guild_id)
        games = self.game_manager.games

        lines = []
        for game_name, appid_str in games.items():
            appid = int(appid_str)
            subscribed = "✅" if appid in subs else "❌"
            lines.append(f"{subscribed} {game_name}")

        message = "Games available for subscription:\n" + "\n".join(lines)
        await ctx.send(message)

    @commands.command(name="subscribe")
    async def subscribe(self, ctx, *, game_name: str):
        appid = None
        for name, aid_str in self.game_manager.games.items():
            if name.lower() == game_name.lower():
                appid = int(aid_str)
                break

        if appid is None:
            await ctx.send(f"Game '{game_name}' not found. Please check the spelling.")
            return

        guild_id = ctx.guild.id
        subs = set(self.subscription_manager.get_subscriptions(guild_id))
        if appid in subs:
            await ctx.send(f"You're already subscribed to {game_name}.")
            return

        self.subscription_manager.add_subscription(guild_id, appid)
        await ctx.send(f"Subscribed to {game_name} successfully!")

    @commands.command(name="unsubscribe")
    async def unsubscribe(self, ctx, *, game_name: str):
        appid = None
        for name, aid_str in self.game_manager.games.items():
            if name.lower() == game_name.lower():
                appid = int(aid_str)
                break

        if appid is None:
            await ctx.send(f"Game '{game_name}' not found. Please check the spelling.")
            return

        guild_id = ctx.guild.id
        subs = set(self.subscription_manager.get_subscriptions(guild_id))
        if appid not in subs:
            await ctx.send(f"You are not subscribed to {game_name}.")
            return

        self.subscription_manager.remove_subscription(guild_id, appid)
        await ctx.send(f"Unsubscribed from {game_name} successfully!")


async def setup(bot):
    await bot.add_cog(SubscriptionCommands(bot))
