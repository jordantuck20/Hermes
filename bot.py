# bot.py
import logging
from logging.handlers import RotatingFileHandler
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils.config_manager import ConfigManager
from utils.game_manager import GameManager
from utils.news_manager import NewsManager
from utils.subscription_manager import SubscriptionManager


# --- Set up logging ---
os.makedirs("logs", exist_ok=True)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")

error_handler = RotatingFileHandler(
    "logs/error.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
root_logger.addHandler(error_handler)

bot_log_handler = RotatingFileHandler(
    "logs/bot.log", maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
bot_log_handler.setLevel(logging.INFO)
bot_log_handler.setFormatter(formatter)
root_logger.addHandler(bot_log_handler)

logger = logging.getLogger("bot")


# --- Load discord token ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


# --- Load necessary intents and managers ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

config_manager = ConfigManager()
subscription_manager = SubscriptionManager()
game_manager = GameManager()
news_manager = NewsManager()


async def load_cogs():
    await bot.load_extension("cogs.admin")
    await bot.load_extension("cogs.subscriptions")
    await bot.load_extension("cogs.tasks")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    # Call create_tables once at bot startup to ensure tables exist
    from utils.bot_database import create_tables

    create_tables()

    print("\n--- Ensuring Guild Configurations ---")
    for guild in bot.guilds:
        await config_manager.get_or_create_guild_config(guild.id, guild.name)
        print(f"Ensured config for guild: {guild.name} ({guild.id})")
    print("--- Guild Configurations Ensured ---\n")

    await load_cogs()


@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a new guild."""
    print(f"Joined new guild: {guild.name} ({guild.id})")
    await config_manager.get_or_create_guild_config(guild.id, guild.name)
    print(f"Created default config for new guild: {guild.name} ({guild.id})")


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
