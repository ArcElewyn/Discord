"""
DISCORD BOT - Personal Best Tracker for Multiple Bosses
======================================================

COMMANDS DOCUMENTATION:
=====================

📊 PERSONAL BEST COMMANDS:
--------------------------
!pbhydra                    → Show your Hydra PB + screenshot
!pbhydra <username>         → Show username's Hydra PB + screenshot  
!pbhydra <damage>           → Submit new Hydra PB (requires screenshot attachment)

!pbchimera                  → Show your Chimera PB + screenshot
!pbchimera <username>       → Show username's Chimera PB + screenshot
!pbchimera <damage>         → Submit new Chimera PB (requires screenshot attachment)

!pbcvc                      → Show your CvC PB + screenshot  
!pbcvc <username>           → Show username's CvC PB + screenshot
!pbcvc <damage>             → Submit new CvC PB (requires screenshot attachment)

🏆 LEADERBOARD COMMANDS (GLOBAL):
--------------------------------
!top10hydra                 → Top 10 Hydra records (all clans)
!top10chimera               → Top 10 Chimera records (all clans)
!top10cvc                   → Top 10 CvC records (all clans)

⭐ LEADERBOARD COMMANDS (RTF CLAN):
----------------------------------
!rtfhydra                   → Top 10 Hydra records (RTF clan only)
!rtfchimera                 → Top 10 Chimera records (RTF clan only)
!rtfcvc                     → Top 10 CvC records (RTF clan only)

🔥 LEADERBOARD COMMANDS (RTFC CLAN):
-----------------------------------
!rtfchydra                  → Top 10 Hydra records (RTFC clan only)
!rtfcchimera                → Top 10 Chimera records (RTFC clan only)
!rtfccvc                    → Top 10 CvC records (RTFC clan only)

⚡ LEADERBOARD COMMANDS (RTFR CLAN):
-----------------------------------
!rtfrhydra                  → Top 10 Hydra records (RTFR clan only)
!rtfrchimera                → Top 10 Chimera records (RTFR clan only)
!rtfrcvc                    → Top 10 CvC records (RTFR clan only)

📈 STATS COMMANDS:
-----------------
!mystats                    → Show all your PBs across all bosses
!mystats <username>         → Show all PBs for specified user
!help                       → Show user-friendly command list

💡 USAGE EXAMPLES:
-----------------
!pbhydra [RTF]Alice        → Shows Alice's Hydra PB and screenshot
!pbchimera 850000          → Submit 850k damage (with screenshot attached)
!rtfhydra                  → Shows RTF clan's top 10 Hydra records
!mystats [RTFC]Bob         → Shows Bob's complete PB overview

🏛️ CLAN SYSTEM:
--------------
Clans are auto-detected from username prefixes:
- RTF members: [RTF]Username or RTFUsername
- RTFC members: [RTFC]Username or RTFCUsername  
- RTFR members: [RTFR]Username or RTFRUsername

🔧 REQUIREMENTS:
---------------
- Screenshot must be attached when submitting new PBs
- Only works in authorized channel
- Supported image formats: PNG, JPG, JPEG, GIF, WEBP
"""

import discord
from discord.ext import commands
import sqlite3
import os
import aiohttp
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration
AUTHORIZED_CHANNEL_ID = 0  # TODO: input channel ID here
SCREENSHOTS_BASE_PATH = "/share/Container/discord-bot/screenshots"
DATABASE_PATH = "/share/Container/discord-bot/bot_data.db"

# Configuration des clans
CLAN_CONFIG = {
    'RTF': {
        'name': 'RTF',
        'emoji': '⭐',
        'color': 0x00ff00
    },
    'RTFC': {
        'name': 'RTFC',
        'emoji': '🔥',
        'color': 0xff4500
    },
    'RTFR': {
        'name': 'RTFR', 
        'emoji': '⚡',
        'color': 0x1e90ff
    }
}
BOSS_CONFIG = {
    'hydra': {
        'name': 'Hydra',
        'emoji': '🔥',
        'color': 0xff6b35
    },
    'chimera': {
        'name': 'Chimera',
        'emoji': '⚡',
        'color': 0x9932cc
    },
    'cvc': {
        'name': 'Clan vs Clan',
        'emoji': '⚔️',
        'color': 0xff0000
    }
}

class DatabaseManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_username TEXT UNIQUE,
            pb_hydra INTEGER DEFAULT 0,
            pb_hydra_screenshot TEXT,
            pb_hydra_date TIMESTAMP,
            pb_chimera INTEGER DEFAULT 0,
            pb_chimera_screenshot TEXT,
            pb_chimera_date TIMESTAMP,
            pb_cvc INTEGER DEFAULT 0,
            pb_cvc_screenshot TEXT,
            pb_cvc_date TIMESTAMP,
            total_attempts INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table pour l'historique global
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pb_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            boss_type TEXT,
            damage INTEGER,
            screenshot_filename TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_pb(self, username, boss_type):
        """Récupère le PB d'un utilisateur pour un boss spécifique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            f"SELECT pb_{boss_type}, pb_{boss_type}_screenshot, pb_{boss_type}_date FROM users WHERE discord_username = ?",
            (username.lower(),)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result if result else (0, None, None)
    
    def update_user_pb(self, username, boss_type, damage, screenshot_filename):
        """Met à jour le PB d'un utilisateur pour un boss spécifique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Créer l'utilisateur s'il n'existe pas, sinon mettre à jour
        cursor.execute(f'''
        INSERT INTO users (discord_username, pb_{boss_type}, pb_{boss_type}_screenshot, pb_{boss_type}_date, total_attempts)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
        ON CONFLICT(discord_username) 
        DO UPDATE SET 
            pb_{boss_type} = ?,
            pb_{boss_type}_screenshot = ?,
            pb_{boss_type}_date = CURRENT_TIMESTAMP,
            total_attempts = total_attempts + 1
        ''', (username.lower(), damage, screenshot_filename, damage, screenshot_filename))
        
        # Ajouter à l'historique
        cursor.execute('''
        INSERT INTO pb_history (username, boss_type, damage, screenshot_filename)
        VALUES (?, ?, ?, ?)
        ''', (username.lower(), boss_type, damage, screenshot_filename))
        
        conn.commit()
        conn.close()
    
    def get_leaderboard(self, boss_type, limit=10, clan=None):
        """Récupère le classement pour un boss spécifique, optionnellement filtré par clan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if clan:
            cursor.execute(f'''
            SELECT discord_username, pb_{boss_type}, pb_{boss_type}_date 
            FROM users 
            WHERE pb_{boss_type} > 0 AND (
                discord_username LIKE '[{clan}]%' OR
                discord_username LIKE '{clan}%'
            )
            ORDER BY pb_{boss_type} DESC 
            LIMIT ?
            ''', (limit,))
        else:
            cursor.execute(f'''
            SELECT discord_username, pb_{boss_type}, pb_{boss_type}_date 
            FROM users 
            WHERE pb_{boss_type} > 0 
            ORDER BY pb_{boss_type} DESC 
            LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_user_all_pbs(self, username):
        """Récupère tous les PB d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT pb_hydra, pb_hydra_date, pb_chimera, pb_chimera_date, pb_cvc, pb_cvc_date
        FROM users WHERE discord_username = ?
        ''', (username.lower(),))
        
        result = cursor.fetchone()
        conn.close()
        return result

class ScreenshotManager:
    def __init__(self, base_path=SCREENSHOTS_BASE_PATH):
        self.base_path = base_path
        # Créer les dossiers pour chaque boss
        for boss_type in BOSS_CONFIG.keys():
            os.makedirs(os.path.join(base_path, boss_type), exist_ok=True)
    
    async def save_screenshot(self, attachment, username, damage, boss_type):
        """Sauvegarde la screenshot localement"""
        try:
            timestamp = int(datetime.now().timestamp())
            file_extension = attachment.filename.split('.')[-1].lower()
            filename = f"{username.lower()}_{damage}_{timestamp}.{file_extension}"
            boss_path = os.path.join(self.base_path, boss_type)
            filepath = os.path.join(boss_path, filename)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        with open(filepath, 'wb') as f:
                            f.write(await resp.read())
                        return filename
            return None
            
        except Exception as e:
            print(f"Erreur sauvegarde screenshot: {e}")
            return None
    
    def get_screenshot_path(self, filename, boss_type):
        """Retourne le chemin complet de la screenshot"""
        if filename:
            return os.path.join(self.base_path, boss_type, filename)
        return None

# Fonctions utilitaires
def get_user_clan(username):
    """Détermine le clan d'un utilisateur basé sur son pseudo"""
    username_upper = username.upper()
    for clan_tag in ['[RTF]', '[RTFC]', '[RTFR]', 'RTF', 'RTFC', 'RTFR']:
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

# Initialisation des managers
db_manager = DatabaseManager()
screenshot_manager = ScreenshotManager()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

async def handle_pb_command(ctx, boss_type, target_user=None, damage=None):
    """Fonction générique pour gérer toutes les commandes PB"""
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return
    
    boss_info = BOSS_CONFIG[boss_type]
    
    try:
        # Cas 1: !pb{boss} username (afficher le PB d'un autre utilisateur)
        if target_user and damage is None and not target_user.isdigit():
            pb_data = db_manager.get_user_pb(target_user, boss_type)
            pb_damage, screenshot_filename, pb_date = pb_data
            
            if pb_damage == 0:
                await ctx.send(f"❌ **{target_user}** has no {boss_info['name']} PB recorded yet.")
                return
            
            embed = discord.Embed(
                title=f"{boss_info['emoji']} {target_user}'s {boss_info['name']} PB",
                description=f"**{pb_damage:,} damage**",
                color=boss_info['color']
            )
            if pb_date:
                formatted_date = format_datetime(pb_date)
                if formatted_date:
                    embed.add_field(name="📅 Record Date", value=formatted_date, inline=False)
            
            # Envoyer la screenshot si elle existe
            if screenshot_filename:
                screenshot_path = screenshot_manager.get_screenshot_path(screenshot_filename, boss_type)
                if screenshot_path and os.path.exists(screenshot_path):
                    file = discord.File(screenshot_path, filename=f"{target_user}_{boss_type}_pb.png")
                    embed.set_image(url=f"attachment://{target_user}_{boss_type}_pb.png")
                    await ctx.send(embed=embed, file=file)
                    return
            
            await ctx.send(embed=embed)
            return
        
        # Cas 2: !pb{boss} 1500000 (soumettre un nouveau PB)
        if target_user and target_user.isdigit():
            damage = int(target_user)  # Le premier argument est en fait le damage
            
            if not ctx.message.attachments:
                await ctx.send("❌ Please attach a screenshot to validate your PB!")
                return
            
            attachment = ctx.message.attachments[0]
            if not any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                await ctx.send("❌ Please attach a valid image file!")
                return
            
            username = ctx.author.name
            current_pb, _, _ = db_manager.get_user_pb(username, boss_type)
            
            if damage > current_pb:
                # Sauvegarder la screenshot
                screenshot_filename = await screenshot_manager.save_screenshot(attachment, username, damage, boss_type)
                
                if screenshot_filename:
                    # Mettre à jour la base
                    db_manager.update_user_pb(username, boss_type, damage, screenshot_filename)
                    
                    improvement = damage - current_pb if current_pb > 0 else damage
                    embed = discord.Embed(
                        title=f"🎉 NEW {boss_info['name'].upper()} PB! 🎉",
                        description=f"**{username}** just hit **{damage:,} damage** on {boss_info['name']}!",
                        color=0x00ff00
                    )
                    embed.add_field(name="📈 Improvement", value=f"+{improvement:,} damage", inline=True)
                    embed.set_image(url=attachment.url)
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to save screenshot. Please try again.")
            else:
                embed = discord.Embed(
                    title="💪 Nice attempt!",
                    description=f"Your damage: **{damage:,}**\nCurrent PB: **{current_pb:,}**",
                    color=0xffa500
                )
                embed.add_field(
                    name="Keep going!", 
                    value=f"You need **{current_pb - damage + 1:,}** more damage for a new PB!",
                    inline=False
                )
                await ctx.send(embed=embed)
            return
        
        # Cas 3: !pb{boss} (afficher son propre PB)
        username = ctx.author.name
        pb_data = db_manager.get_user_pb(username, boss_type)
        pb_damage, screenshot_filename, pb_date = pb_data
        
        if pb_damage == 0:
            embed = discord.Embed(
                title=f"{boss_info['emoji']} Your {boss_info['name']} PB",
                description="**No record yet**",
                color=0x666666
            )
            embed.add_field(
                name="💡 Get started!", 
                value=f"Use `!pb{boss_type} <damage>` with a screenshot to set your first record!",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"{boss_info['emoji']} {username}'s {boss_info['name']} PB",
            description=f"**{pb_damage:,} damage**",
            color=boss_info['color']
        )
        if pb_date:
            formatted_date = format_datetime(pb_date)
            if formatted_date:
                embed.add_field(name="📅 Record Date", value=formatted_date, inline=False)
        
        # Envoyer la screenshot si elle existe
        if screenshot_filename:
            screenshot_path = screenshot_manager.get_screenshot_path(screenshot_filename, boss_type)
            if screenshot_path and os.path.exists(screenshot_path):
                file = discord.File(screenshot_path, filename=f"{username}_{boss_type}_pb.png")
                embed.set_image(url=f"attachment://{username}_{boss_type}_pb.png")
                await ctx.send(embed=embed, file=file)
                return
        
        await ctx.send(embed=embed)
        
    except ValueError:
        await ctx.send(f"❌ Please provide a valid damage number!\nExample: `!pb{boss_type} 1500000`")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# Commandes pour chaque boss
@bot.command()
async def pbhydra(ctx, target_user: str = None, damage: int = None):
    """Commande !pbhydra"""
    await handle_pb_command(ctx, 'hydra', target_user, damage)

@bot.command()
async def pbchimera(ctx, target_user: str = None, damage: int = None):
    """Commande !pbchimera"""
    await handle_pb_command(ctx, 'chimera', target_user, damage)

@bot.command()
async def pbcvc(ctx, target_user: str = None, damage: int = None):
    """Commande !pbcvc"""
    await handle_pb_command(ctx, 'cvc', target_user, damage)

# Commandes de classement global
@bot.command()
async def top10hydra(ctx):
    """Affiche le top 10 des PB Hydra (tous clans)"""
    await show_leaderboard(ctx, 'hydra')

@bot.command()
async def top10chimera(ctx):
    """Affiche le top 10 des PB Chimera (tous clans)"""
    await show_leaderboard(ctx, 'chimera')

@bot.command()
async def top10cvc(ctx):
    """Affiche le top 10 des PB CvC (tous clans)"""
    await show_leaderboard(ctx, 'cvc')

# Commandes de classement par clan - RTF
@bot.command()
async def rtfhydra(ctx):
    """Affiche le top 10 Hydra du clan RTF"""
    await show_leaderboard(ctx, 'hydra', 'RTF')

@bot.command()
async def rtfchimera(ctx):
    """Affiche le top 10 Chimera du clan RTF"""
    await show_leaderboard(ctx, 'chimera', 'RTF')

@bot.command()
async def rtfcvc(ctx):
    """Affiche le top 10 CvC du clan RTF"""
    await show_leaderboard(ctx, 'cvc', 'RTF')

# Commandes de classement par clan - RTFC
@bot.command()
async def rtfchydra(ctx):
    """Affiche le top 10 Hydra du clan RTFC"""
    await show_leaderboard(ctx, 'hydra', 'RTFC')

@bot.command()
async def rtfcchimera(ctx):
    """Affiche le top 10 Chimera du clan RTFC"""
    await show_leaderboard(ctx, 'chimera', 'RTFC')

@bot.command()
async def rtfccvc(ctx):
    """Affiche le top 10 CvC du clan RTFC"""
    await show_leaderboard(ctx, 'cvc', 'RTFC')

# Commandes de classement par clan - RTFR
@bot.command()
async def rtfrhydra(ctx):
    """Affiche le top 10 Hydra du clan RTFR"""
    await show_leaderboard(ctx, 'hydra', 'RTFR')

@bot.command()
async def rtfrchimera(ctx):
    """Affiche le top 10 Chimera du clan RTFR"""
    await show_leaderboard(ctx, 'chimera', 'RTFR')

@bot.command()
async def rtfrcvc(ctx):
    """Affiche le top 10 CvC du clan RTFR"""
    await show_leaderboard(ctx, 'cvc', 'RTFR')

async def show_leaderboard(ctx, boss_type, clan=None):
    """Fonction générique pour afficher les classements"""
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return
    
    try:
        boss_info = BOSS_CONFIG[boss_type]
        leaderboard = db_manager.get_leaderboard(boss_type, 10, clan)
        
        if not leaderboard:
            clan_text = f" for clan {clan}" if clan else ""
            await ctx.send(f"❌ No {boss_info['name']} records found{clan_text} yet!")
            return
        
        # Titre avec clan si spécifié
        title = f"🏆 {boss_info['name']} Leaderboard - Top 10"
        if clan:
            clan_info = CLAN_CONFIG.get(clan, {'name': clan, 'emoji': '🏛️'})
            title = f"{clan_info['emoji']} {clan_info['name']} - {boss_info['name']} Top 10"
        
        embed = discord.Embed(
            title=title,
            color=boss_info['color'] if not clan else CLAN_CONFIG.get(clan, {'color': boss_info['color']})['color']
        )
        
        medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        
        for i, (username, damage, date) in enumerate(leaderboard):
            date_text = ""
            if date:
                formatted_date = format_date_only(date)
                if formatted_date:
                    date_text = f" • {formatted_date}"
            
            # Afficher le clan dans le nom si pas de filtre par clan
            display_name = username
            if not clan:
                user_clan = get_user_clan(username)
                if user_clan:
                    clan_emoji = CLAN_CONFIG.get(user_clan, {'emoji': '🏛️'})['emoji']
                    display_name = f"{clan_emoji} {username}"
            
            embed.add_field(
                name=f"{medals[i]} #{i+1} {display_name}",
                value=f"**{damage:,}** damage{date_text}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def mystats(ctx, target_user: str = None):
    """Affiche tous les PB d'un utilisateur"""
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return
    
    try:
        username = target_user if target_user else ctx.author.name
        user_data = db_manager.get_user_all_pbs(username)
        
        if not user_data:
            await ctx.send(f"❌ No data found for **{username}**.")
            return
        
        hydra_pb, hydra_date, chimera_pb, chimera_date, cvc_pb, cvc_date = user_data
        
        embed = discord.Embed(
            title=f"📊 {username}'s Complete Stats",
            color=0x00bfff
        )
        
        # Hydra
        hydra_text = f"**{hydra_pb:,} damage**" if hydra_pb > 0 else "No record"
        if hydra_pb > 0 and hydra_date:
            formatted_date = format_date_only(hydra_date)
            if formatted_date:
                hydra_text += f"\n📅 {formatted_date}"
        embed.add_field(name="🔥 Hydra PB", value=hydra_text, inline=True)
        
        # Chimera
        chimera_text = f"**{chimera_pb:,} damage**" if chimera_pb > 0 else "No record"
        if chimera_pb > 0 and chimera_date:
            formatted_date = format_date_only(chimera_date)
            if formatted_date:
                chimera_text += f"\n📅 {formatted_date}"
        embed.add_field(name="⚡ Chimera PB", value=chimera_text, inline=True)
        
        # CvC
        cvc_text = f"**{cvc_pb:,} damage**" if cvc_pb > 0 else "No record"
        if cvc_pb > 0 and cvc_date:
            formatted_date = format_date_only(cvc_date)
            if formatted_date:
                cvc_text += f"\n📅 {formatted_date}"
        embed.add_field(name="⚔️ CvC PB", value=cvc_text, inline=True)
        
        # Total des PB
        total_damage = (hydra_pb or 0) + (chimera_pb or 0) + (cvc_pb or 0)
        embed.add_field(name="💯 Total Combined", value=f"**{total_damage:,} damage**", inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def help(ctx):
    """Affiche la liste des commandes disponibles - Notice utilisateur"""
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return
    
    embed = discord.Embed(
        title="🤖 RTF Bot - Commands Help",
        description="Here are all available commands for tracking your Personal Bests!",
        color=0x00bfff
    )
    
    # Commandes PB
    embed.add_field(
        name="📊 Personal Best Commands",
        value="`!pbhydra` `!pbchimera` `!pbcvc`\n" +
              "• Use alone to see your PB\n" +
              "• Add username to see someone else's PB\n" +
              "• Add damage + screenshot to submit new PB",
        inline=False
    )
    
    # Classements globaux
    embed.add_field(
        name="🌍 Global Leaderboards",
        value="`!top10hydra` `!top10chimera` `!top10cvc`\n" +
              "Shows top 10 records across all clans",
        inline=False
    )
    
    # Classements par clan
    embed.add_field(
        name="⭐ RTF Clan Rankings",
        value="`!rtfhydra` `!rtfchimera` `!rtfcvc`",
        inline=True
    )
    
    embed.add_field(
        name="🔥 RTFC Clan Rankings", 
        value="`!rtfchydra` `!rtfcchimera` `!rtfccvc`",
        inline=True
    )
    
    embed.add_field(
        name="⚡ RTFR Clan Rankings",
        value="`!rtfrhydra` `!rtfrchimera` `!rtfrcvc`",
        inline=True
    )
    
    # Stats et aide
    embed.add_field(
        name="📈 Stats & Info",
        value="`!mystats` - View all your PBs\n" +
              "`!mystats <username>` - View someone's PBs\n" +
              "`!help` - Show this help message",
        inline=False
    )
    
    # Instructions
    embed.add_field(
        name="💡 How to Submit a PB",
        value="1. Type `!pbhydra <damage>` (example: `!pbhydra 1500000`)\n" +
              "2. **Attach a screenshot** to your message\n" +
              "3. Bot will automatically save if it's a new record!",
        inline=False
    )
    
    # Note sur les clans
    embed.add_field(
        name="🏛️ Clan Detection",
        value="Your clan is auto-detected from your username:\n" +
              "• RTF: `[RTF]Name` or `RTFName`\n" +
              "• RTFC: `[RTFC]Name` or `RTFCName`\n" +
              "• RTFR: `[RTFR]Name` or `RTFRName`",
        inline=False
    )
    
    embed.set_footer(text="🎮 Good luck with your records!")
    
    await ctx.send(embed=embed)

# TODO: Add your bot token here
# bot.run("YOUR_DISCORD_TOKEN")
