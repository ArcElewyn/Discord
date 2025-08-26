import os
import asyncio
import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from utils.DatabaseManager_class import DatabaseManager
from utils.ScreenshotManager_class import ScreenshotManager

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

db_manager = DatabaseManager()
screenshot_manager = ScreenshotManager()

initial_cogs = [
    "cogs.guide",
    "cogs.pbhydra",
    "cogs.pbchimera",
    "cogs.pbcvc",
    "cogs.top10",
    "cogs.mystats",
    "cogs.mercy",
]

async def load_all_cogs():
    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
            print(f"[OK] Cog {cog} chargé")
        except Exception as e:
            print(f"[ERREUR] Impossible de charger {cog}: {e}")

@bot.event
async def on_ready():
    print(f"{bot.user.name} est connecté !")

async def main():
    await load_all_cogs()
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

