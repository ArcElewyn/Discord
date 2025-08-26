import os
from dotenv import load_dotenv

load_dotenv()

# Token et channel autorisé
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AUTHORIZED_CHANNEL_ID = int(os.getenv("AUTHORIZED_CHANNEL_ID"))

# Chemins
SCREENSHOTS_BASE_PATH = "/app/screenshots"
DATABASE_PATH = "/app/data/bot_data.db"

# Configuration des clans
CLAN_CONFIG = {
    'RTF':  {'name': 'RTF',  'emoji': 'â­', 'color': 0x00ff00},
    'RTFC': {'name': 'RTFC', 'emoji': 'ðŸ”¥', 'color': 0xff4500},
    'RTFR': {'name': 'RTFR', 'emoji': 'âš¡', 'color': 0x1e90ff}
}

# Configuration des boss avec difficultées
BOSS_CONFIG = {
    'hydra':   {'name': 'Hydra',   'emoji': 'ðŸ', 'color': 0xff6b35,
                'difficulties': ['normal', 'hard', 'brutal', 'nightmare']},
    'chimera': {'name': 'Chimera', 'emoji': 'ðŸ¦', 'color': 0x9932cc,
                'difficulties': ['easy', 'normal', 'hard', 'brutal', 'nightmare', 'ultra']},
    'cvc':     {'name': 'Clan vs Clan', 'emoji': 'âš”ï¸', 'color': 0xff0000, 'difficulties': []}
}

# Mappings pour diminutifs de difficultÃ©s
DIFFICULTY_SHORTCUTS = {
    'nm': 'nightmare',
    'unm': 'ultra'
}