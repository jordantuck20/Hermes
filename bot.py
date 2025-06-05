import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from steam_api import fetch_steam_news
from storage import (
    get_update_channel,
    set_update_channel,
    save_last_news_id,
    get_last_news_id,
)
import json
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

with open("data/games.json", "r") as f:
    GAMES = json.load(f)

APPID_TO_NAME = {int(appid): name for name, appid in GAMES.items()}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    if not check_for_updates.is_running():
        check_for_updates.start()


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command(name="setchannel")
@commands.has_permissions(manage_guild=True)
async def setchannel(ctx, channel: discord.TextChannel = None):
    if channel is None:
        await ctx.send("Please mention a channel, e.g. `!setchannel #general`")
        return

    set_update_channel(ctx.guild.id, channel.id)
    await ctx.send(f"Update channel set to {channel.mention}")


@setchannel.error
async def setchannel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "Sorry, you do not have the appropriate permissions to use this command."
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please mention a valid text channel.")
    else:
        await ctx.send("An error occurred while processing the command.")


@tasks.loop(minutes=1)
async def check_for_updates():
    appids = [553850]

    for guild in bot.guilds:
        channel_id = get_update_channel(guild.id)
        if not channel_id:
            continue

        channel = bot.get_channel(channel_id)
        if not channel:
            continue

        for appid in appids:
            newsitems = fetch_steam_news(appid, count=1)
            if not newsitems:
                continue

            latest_news = newsitems[0]
            last_gid = get_last_news_id(guild.id, appid)

            if latest_news["gid"] == last_gid:
                continue

            save_last_news_id(guild.id, appid, latest_news["gid"])

            game_name = APPID_TO_NAME.get(appid, "Unknown Game")

            embed = discord.Embed(
                title=latest_news["title"],
                description=latest_news["contents"][:2048],
                url=latest_news["url"],
                color=discord.Color.blue(),
            )

            embed.set_footer(text=f"{game_name}")

            await channel.send(
                f"New item posted! <t:{latest_news["date"]}:R>", embed=embed
            )


if __name__ == "__main__":
    bot.run(TOKEN)
