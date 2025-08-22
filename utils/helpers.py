import re
from datetime import datetime
from config import AUTHORIZED_CHANNEL_ID, DIFFICULTY_SHORTCUTS 

def parse_damage_amount(damage_str):
    """Convertit les montants avec suffixes (K, M, B) en nombres entiers"""
    if not damage_str:
        return None
    damage_str = damage_str.strip().upper()
    if damage_str.isdigit():
        return int(damage_str)
    match = re.match(r'^([0-9]*\.?[0-9]+)([KMB]?)$', damage_str)
    if not match:
        return None
    number_str, suffix = match.groups()
    try:
        number = float(number_str)
    except ValueError:
        return None
    multipliers = {'K': 1000, 'M': 1_000_000, 'B': 1_000_000_000, '': 1}
    return int(number * multipliers[suffix])

def format_damage_display(damage):
    """Formate un montant de dégâts avec le suffixe approprié"""
    if damage >= 1_000_000_000:
        billions = damage / 1_000_000_000
        return f"{int(billions)}B" if billions == int(billions) else f"{billions:.1f}B"
    elif damage >= 1_000_000:
        millions = damage / 1_000_000
        return f"{int(millions)}M" if millions == int(millions) else f"{millions:.1f}M"
    elif damage >= 1_000:
        thousands = damage / 1_000
        return f"{int(thousands)}K" if thousands == int(thousands) else f"{thousands:.1f}K"
    return str(damage)

def normalize_difficulty(difficulty):
    """Normalise une difficulté en gérant les diminutifs"""
    if not difficulty:
        return None
    
    difficulty_lower = difficulty.lower()
    
    # Vérifier les diminutifs d'abord
    if difficulty_lower in DIFFICULTY_SHORTCUTS:
        return DIFFICULTY_SHORTCUTS[difficulty_lower]
    
    # Sinon retourner tel quel
    return difficulty_lower

# Fonctions utilitaires
def get_user_clan(username):
    """Détermine le clan d'un utilisateur basé sur son pseudo - Version corrigée"""
    username_upper = username.upper()
    
    # Chercher les tags avec crochets et espace
    for clan_tag in ['[RTF] ', '[RTFC] ', '[RTFR] ']:
        if username_upper.startswith(clan_tag):
            return clan_tag.replace('[', '').replace(']', '').strip()
    
    # Chercher les tags avec crochets sans espace  
    for clan_tag in ['[RTF]', '[RTFC]', '[RTFR]']:
        if username_upper.startswith(clan_tag):
            return clan_tag.replace('[', '').replace(']', '')
    
    return None

def format_datetime(date_str):
    """Formate une date en format AM/PM"""
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%m/%d/%Y at %I:%M %p")
    except:
        return None

def format_date_only(date_str):
    """Formate une date sans l'heure"""
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%m/%d/%Y")
    except:
        return None

def get_difficulty_display_name(difficulty):
    """Convertit le nom de difficulté en nom d'affichage"""
    difficulty_names = {
        'ultra': 'Ultra Nightmare',
        'nightmare': 'Nightmare',
        'brutal': 'Brutal', 
        'hard': 'Hard',
        'normal': 'Normal',
        'easy': 'Easy'
    }
    return difficulty_names.get(difficulty, difficulty.title())

def is_authorized_channel(ctx):
    return ctx.channel.id == AUTHORIZED_CHANNEL_ID

