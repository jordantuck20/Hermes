# cogs/subscriptions.py
from discord.ext import commands

from bot import game_manager, subscription_manager


class SubscriptionCommands(commands.Cog):
    def __init__(self, bot):
        """
        Initializes the SubscriptionCommands cog.

        This cog handles user-facing commands for managing game subscriptions,
        including listing available games, subscribing, and unsubscribing.

        Args:
            bot (commands.Bot): The bot instance.
        """
        self.bot = bot
        self.subscription_manager = subscription_manager
        self.game_manager = game_manager

    @commands.command(name="listgames")
    async def list_games(self, ctx):
        """
        Lists all trackable games and your server's subscription status.

        This command fetches the list of games from the in-memory cache and
        compares it with the server's active subscriptions from the database.

        Args:
            ctx (commands.Context): The context in which the command was called.
        """
        guild_id = ctx.guild.id
        subs = await self.subscription_manager.get_subscriptions(guild_id)

        lines = []

        sorted_games = sorted(
            self.game_manager.appid_to_name.items(), key=lambda item: item[1].lower()
        )

        for appid, game_name in sorted_games:
            subscribed = "✅" if appid in subs else "❌"
            lines.append(f"{subscribed} {game_name}")

        if not lines:
            message = "No games are currently available for subscription. Please contact an admin."
        else:
            message = "Games available for subscription:\n" + "\n".join(lines)

        if len(message) > 2000:
            await ctx.send("The list of games is too long. Please contact an admin. ")
        else:
            await ctx.send(message)

    @commands.command(name="subscribe")
    async def subscribe(self, ctx, *, game_name: str):
        """
        Subscribes your server to receive news updates for a game.

        This command attempts to add a new subscription entry to the database
        for the given server and game name.

        Args:
            ctx (commands.Context): The context in which the command was called.
            game_name (str): The name of the game to subscribe to.
        """
        appid = self.game_manager.get_appid_by_name(game_name)

        if appid is None:
            await ctx.send(f"Game '{game_name}' not found. Please check the spelling.")
            return

        guild_id = ctx.guild.id

        success = await self.subscription_manager.add_subscription(guild_id, appid)

        if success:
            await ctx.send(
                f"Subscribed to {self.game_manager.get_name(appid)} successfully!"
            )
        else:
            await ctx.send(
                f"Could not subscribe to {self.game_manager.get_name(appid)}. You might already be subscribed."
            )

    @commands.command(name="unsubscribe")
    async def unsubscribe(self, ctx, *, game_name: str):
        """
        Unsubscribes your server from news updates for a game.

        This command attempts to remove a subscription entry from the database
        for the given server and game name.

        Args:
            ctx (commands.Context): The context in which the command was called.
            game_name (str): The name of the game to unsubscribe from.
        """
        appid = self.game_manager.get_appid_by_name(game_name)

        if appid is None:
            await ctx.send(f"Game '{game_name}' not found. Please check the spelling.")
            return

        guild_id = ctx.guild.id

        success = await self.subscription_manager.remove_subscription(guild_id, appid)

        if success:
            await ctx.send(
                f"Unsubscribed from {self.game_manager.get_name(appid)} successfully!"
            )
        else:
            await ctx.send(
                f"Could not unsubscribe to {self.game_manager.get_name(appid)}. You might not be subscribed."
            )


async def setup(bot):
    """
    Adds the SubscriptionCommands cog to the bot.
    """
    await bot.add_cog(SubscriptionCommands(bot))
