import os
import discord
import asyncio
import random
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from collections import defaultdict, deque

load_dotenv()

# ----------------------------
# ENV
# ----------------------------
TOKEN = os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ----------------------------
# BOT SETUP
# ----------------------------
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ----------------------------
# MEMORY
# ----------------------------
memory = defaultdict(lambda: deque(maxlen=12))

# ----------------------------
# LEVI SYSTEM PROMPT
# ----------------------------
SYSTEM_PROMPT = """
You are a polished futuristic AI assistant.

Rules:
- Be calm, intelligent, and concise.
- Use short, clear sentences.
- Sound warm, composed, and confident.
- Be helpful first, stylish second.
- No emojis.
- No long explanations unless asked.
- If the user is vague, ask one brief clarifying question.
"""

# ----------------------------
# AI FUNCTION
# ----------------------------
def generate_response(conversation):
    import requests

    if not OPENROUTER_API_KEY:
        return "Tch... missing API key."

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in conversation:
        if msg.startswith("User:"):
            messages.append({
                "role": "user",
                "content": msg.replace("User:", "").strip()
            })
        elif msg.startswith("Levi:"):
            messages.append({
                "role": "assistant",
                "content": msg.replace("Levi:", "").strip()
            })

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 120
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    if response.status_code != 200:
        print("ERROR:", response.text)
        return "Tch... something went wrong."

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

# ----------------------------
# SLASH COMMANDS
# ----------------------------

@tree.command(name="support", description="Get support server link")
async def support(interaction: discord.Interaction):
    await interaction.response.send_message(
        "discord.gg/kbj3gCMGAb",
        ephemeral=True
    )

@tree.command(name="setup", description="Initialize Levi system in this server")
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Levi system initialized. Ping me to activate conversation mode.",
        ephemeral=True
    )

# ----------------------------
# READY EVENT
# ----------------------------
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

@bot.event
async def on_ready():
    print(f'{bot.user} is online! W in the chat')
    activity = Activity(name='Nathaniel and Haruto', type=ActivityType.watching)
    await bot.change_presence(activity=activity)

# ----------------------------
# MESSAGE HANDLER
# ----------------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    channel_id = message.channel.id

    async with message.channel.typing():

        # store user message
        memory[channel_id].append(f"User: {message.content}")

        conversation = list(memory[channel_id])

        reply = await asyncio.to_thread(generate_response, conversation)

        memory[channel_id].append(f"Levi: {reply}")

    await message.channel.send(reply)

# ----------------------------
# RUN BOT
# ----------------------------
bot.run(TOKEN)
