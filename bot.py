# -*- coding: utf-8 -*-
import discord
import os
import sys
from discord.ext import commands
from config import DISCORD_TOKEN

from utils.DatabaseManager_class import DatabaseManager
from utils.ScreenshotManager_class import ScreenshotManager
from utils.MercyManager_class import MercyManager
from utils.pb_handler import set_managers
from utils.leaderboard_handler import set_db_manager

# Force UTF-8

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

# Définir les intents
intents = discord.Intents.default()
intents.message_content = True

# Initialisation des managers
db_manager = DatabaseManager()
screenshot_manager = ScreenshotManager()
mercy_manager = MercyManager()

# Injection des managers dans les handlers
set_managers(db_manager, screenshot_manager)  # pb_handler
set_db_manager(db_manager)                    # leaderboard_handler

# Liste des cogs
initial_cogs = [
    "cogs.guide",
    "cogs.pbhydra",
    "cogs.pbchimera",
    "cogs.pbcvc",
    "cogs.top10",
    "cogs.mystats",
    "cogs.mercy",
]

# Liste des dossiers
folders = [
    "screenshots/hydra/normal",
    "screenshots/hydra/hard",
    "screenshots/hydra/brutal",
    "screenshots/hydra/nightmare",
    "screenshots/chimera/easy",
    "screenshots/chimera/normal",
    "screenshots/chimera/hard",
    "screenshots/chimera/brutal",
    "screenshots/chimera/nightmare",
    "screenshots/chimera/ultra",
    "screenshots/cvc",
]

# Création des dossiers si nécessaire (exist_ok=True évite d'écraser)
for f in folders:
    os.makedirs(f, exist_ok=True)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.db_manager = db_manager
        self.screenshot_manager = screenshot_manager
        self.mercy_manager = mercy_manager

    async def setup_hook(self):
        for cog in initial_cogs:
            try:
                await self.load_extension(cog)
                print(f"[OK] Cog {cog} chargé")
            except Exception as e:
                print(f"[ERREUR] Impossible de charger {cog}: {e}")

    async def on_ready(self):
        print(f"{self.user.name} est connecté !")

bot = MyBot()
bot.run(DISCORD_TOKEN)
