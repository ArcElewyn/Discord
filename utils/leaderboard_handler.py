import os
import discord
from discord.ext import commands
from config import AUTHORIZED_CHANNEL_ID, BOSS_CONFIG, CLAN_CONFIG
from utils.helpers import normalize_difficulty, get_difficulty_display_name, format_damage_display, format_date_only, get_user_clan

db_manager = None

def set_db_manager(db):
    global db_manager
    db_manager = db

async def show_leaderboard(ctx, boss_type, difficulty=None, clan=None):
    """Fonction gÃ©nÃ©rique pour afficher les classements"""
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return
    
    try:
        # Normaliser la difficultÃ© si spÃ©cifiÃ©e
        if difficulty:
            difficulty = normalize_difficulty(difficulty)
            if difficulty not in BOSS_CONFIG[boss_type]['difficulties']:
                difficulties = " | ".join(BOSS_CONFIG[boss_type]['difficulties'])
                await ctx.send(f"âŒ Invalid difficulty. Available: {difficulties}")
                return
        
        boss_info = BOSS_CONFIG[boss_type]
        leaderboard = db_manager.get_leaderboard(boss_type, difficulty, 10, clan)
        
        if not leaderboard:
            clan_text = f" for clan {clan}" if clan else ""
            difficulty_text = f" {get_difficulty_display_name(difficulty)}" if difficulty else ""
            await ctx.send(f"âŒ No{difficulty_text} {boss_info['name']} records found{clan_text} yet!")
            return
        
        # Titre avec clan et difficultÃ© si spÃ©cifiÃ©s
        difficulty_name = get_difficulty_display_name(difficulty) if difficulty else ""
        title = f"ðŸ† {difficulty_name} {boss_info['name']} Leaderboard - Top 10"
        
        if clan:
            clan_info = CLAN_CONFIG.get(clan, {'name': clan, 'emoji': 'ðŸ›ï¸'})
            title = f"{clan_info['emoji']} {clan_info['name']} - {difficulty_name} {boss_info['name']} Top 10"
        
        embed = discord.Embed(
            title=title,
            color=boss_info['color'] if not clan else CLAN_CONFIG.get(clan, {'color': boss_info['color']})['color']
        )
        
        medals = ["ðŸ¥‡", "ðŸ¥ˆ", "ðŸ¥‰"] + ["ðŸ…"] * 7
        
        for i, (username, damage, date) in enumerate(leaderboard):
            date_text = ""
            if date:
                formatted_date = format_date_only(date)
                if formatted_date:
                    date_text = f" â€¢ {formatted_date}"
            
            # Afficher le clan dans le nom si pas de filtre par clan
            display_name = username
            if not clan:
                user_clan = get_user_clan(username)
                if user_clan:
                    clan_emoji = CLAN_CONFIG.get(user_clan, {'emoji': 'ðŸ›ï¸'})['emoji']
                    display_name = f"{clan_emoji} {username}"
            
            embed.add_field(
                name=f"{medals[i]} #{i+1} {display_name}",
                value=f"**{format_damage_display(damage)} damage**{date_text}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"âŒ Error: {e}")