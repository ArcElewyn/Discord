# -*- coding: utf-8 -*-
import os
import discord
from discord.ext import commands
from config import DISCORD_TOKEN

# Import des managers
from utils.DatabaseManager_class import DatabaseManager
from utils.ScreenshotManager_class import ScreenshotManager

# Définir les intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Initialisation unique des managers
db_manager = DatabaseManager()
screenshot_manager = ScreenshotManager()

# Liste des Cogs à charger
initial_cogs = [
    "cogs.guide",
    "cogs.pbhydra",
    "cogs.pbchimera",
    "cogs.pbcvc",
    "cogs.top10",
    "cogs.mystats",
    "cogs.mercy",
]

async def load_cogs():
    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
            print(f"[OK] Cog {cog} chargé")
        except Exception as e:
            print(f"[ERREUR] Impossible de charger {cog}: {e}")

@bot.event
async def on_ready():
    print(f"{bot.user.name} est connecté !")

# Charger les cogs avant le run
bot.loop.create_task(load_cogs())

# Lancer le bot
bot.run(DISCORD_TOKEN)
