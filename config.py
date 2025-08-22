import os
from dotenv import load_dotenv

load_dotenv()

# Token et channel autorisé
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AUTHORIZED_CHANNEL_ID = int(os.getenv("AUTHORIZED_CHANNEL_ID"))

# Chemins
SCREENSHOTS_BASE_PATH = "/share/Container/discord-bot/screenshots"
DATABASE_PATH = "/share/Container/discord-bot/bot_data.db"

# Configuration des clans
CLAN_CONFIG = {
    'RTF':  {'name': 'RTF',  'emoji': '⭐', 'color': 0x00ff00},
    'RTFC': {'name': 'RTFC', 'emoji': '🔥', 'color': 0xff4500},
    'RTFR': {'name': 'RTFR', 'emoji': '⚡', 'color': 0x1e90ff}
}

# Configuration des boss avec difficultés
BOSS_CONFIG = {
    'hydra':   {'name': 'Hydra',   'emoji': '🐍', 'color': 0xff6b35,
                'difficulties': ['normal', 'hard', 'brutal', 'nightmare']},
    'chimera': {'name': 'Chimera', 'emoji': '🦁', 'color': 0x9932cc,
                'difficulties': ['easy', 'normal', 'hard', 'brutal', 'nightmare', 'ultra']},
    'cvc':     {'name': 'Clan vs Clan', 'emoji': '⚔️', 'color': 0xff0000, 'difficulties': []}
}

# Mappings pour diminutifs de difficultés
DIFFICULTY_SHORTCUTS = {
    'nm': 'nightmare',
    'unm': 'ultra'
}