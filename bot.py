# bot.py
import json
import logging
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils.config_manager import ConfigManager
from utils.game_manager import GameManager
from utils.news_manager import NewsManager
from utils.subscription_manager import SubscriptionManager

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/error.log",
    level=logging.ERROR,
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
)

logger = logging.getLogger("bot")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

config_manager = ConfigManager()
subscription_manager = SubscriptionManager(config_manager)
game_manager = GameManager()
news_manager = NewsManager(config_manager)


async def load_cogs():
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.subscriptions")
    await bot.load_extension("cogs.tasks")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

    await load_cogs()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that. Shoo.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Uh oh. I don't have permission to do that 🥲")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command. What are you even trying to do...?")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument. Bruh, get it together 😆")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bad argument. Do you even know how to type? 🤦")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send("Chilllll. It's on cooldown...")
    else:
        logging.error(
            f"Unhandled exception in command '{ctx.command}':", exc_info=error
        )
        await ctx.send(
            "Umm even I don't know what happened... but I'll figure it out... eventually..."
        )


if __name__ == "__main__":
    bot.run(TOKEN)
