import os
import discord
from discord.ext import commands

# ----------------------------
# ENV SAFETY
# ----------------------------
def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing environment variable: {name}")
    return value

TOKEN = require_env("TOKEN")
CLIENT_ID = require_env("CLIENT_ID")
GUILD_ID = require_env("GUILD_ID")

GUILD_ID = int(GUILD_ID)

# ----------------------------
# BOT
# ----------------------------
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# ----------------------------
# SLASH COMMAND DATA
# ----------------------------
slash_commands = [
    {
        "name": "support",
        "description": "Shows the support server!"
    }
]

# ----------------------------
# REGISTER COMMANDS
# ----------------------------
@bot.event
async def on_ready():
    print("Registering slash commands...")

    try:
        await bot.http.put(
            f"/applications/{CLIENT_ID}/guilds/{GUILD_ID}/commands",
            json=slash_commands
        )
        print("Slash commands registered successfully")

    except Exception as error:
        print(f"Error registering commands: {error}")

    await bot.close()

# ----------------------------
# RUN
# ----------------------------
bot.run(TOKEN)
