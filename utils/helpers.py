# -*- coding: utf-8 -*-
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
    multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000, '': 1}
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
    if difficulty_lower in DIFFICULTY_SHORTCUTS:
        return DIFFICULTY_SHORTCUTS[difficulty_lower]
    return difficulty_lower

def get_user_clan(username):
    """Détermine le clan d'un utilisateur basé sur son pseudo"""
    username_upper = username.upper()
    # Tags avec crochets et espace
    for clan_tag in ['[RTF] ', '[RTFC] ', '[RTFR] ']:
        if username_upper.startswith(clan_tag):
            return clan_tag.replace('[', '').replace(']', '').strip()
    # Tags avec crochets sans espace
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

MERCY_RULES = {
    "ancient": {"start": 200, "increment": 5, "base": 0.5},
    "void": {"start": 200, "increment": 5, "base": 0.5},
    "sacred": {"start": 12, "increment": 2, "base": 6},
    "primal_legendary": {"start": 75, "increment": 1, "base": 1},
    "primal_mythical": {"start": 200, "increment": 10, "base": 0.5},
    "remnant": {"start": 24, "increment": 1, "base": 0},
}

def calc_chance_and_guarantee(shard_type, pulls):
    """Retourne chance, pull garanti et pulls restants"""
    if shard_type not in MERCY_RULES:
        return 0, None, None
    rule = MERCY_RULES[shard_type]
    chance = rule["base"] if pulls < rule["start"] else rule["base"] + (pulls - rule["start"]) * rule["increment"]
    guaranteed_at = int(rule["start"] + (100 - rule["base"]) / rule["increment"])
    remaining = max(0, guaranteed_at - pulls)
    return chance, guaranteed_at, remaining
