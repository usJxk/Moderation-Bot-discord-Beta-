import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv #type:ignore

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("La variable de entorno DISCORD_TOKEN no está definida.")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


async def load_cogs():
    cogs_path = Path(__file__).parent / "cogs"
    for file in cogs_path.glob("*.py"):
        if file.name.startswith("_"):
            continue
        await bot.load_extension(f"cogs.{file.stem}")


@bot.event
async def setup_hook():
    await load_cogs()


try:
    bot.run(TOKEN)
except discord.errors.PrivilegedIntentsRequired as exc:
    print("pene")
