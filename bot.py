import os
import discord
from discord.ext import commands
from config import DISCORD_TOKEN

# Import des managers
from utils.DatabaseManager_class import DatabaseManager
from utils.ScreenshotManager_class import ScreenshotManager

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
]

for cog in initial_cogs:
    bot.load_extension(cog)

@bot.event
async def on_ready():
    print(f"{bot.user.name} est connecté !")

bot.run(DISCORD_TOKEN)
