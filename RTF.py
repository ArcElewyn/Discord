import discord
from discord.ext import commands
import sqlite3
import os
import aiohttp
from datetime import datetime
import re

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

# Configuration des boss avec difficultés
BOSS_CONFIG = {
    'hydra': {
        'name': 'Hydra',
        'emoji': '🐍',
        'color': 0xff6b35,
        'difficulties': ['normal', 'hard', 'brutal', 'nightmare']
    },
    'chimera': {
        'name': 'Chimera',
        'emoji': '🦁',
        'color': 0x9932cc,
        'difficulties': ['easy', 'normal', 'hard', 'brutal', 'nightmare', 'ultra']
    },
    'cvc': {
        'name': 'Clan vs Clan',
        'emoji': '⚔️',
        'color': 0xff0000,
        'difficulties': []  # Pas de difficultés pour CvC
    }
}

# Mappings pour les diminutifs de difficultés
DIFFICULTY_SHORTCUTS = {
    'nm': 'nightmare',
    'unm': 'ultra'
}

def parse_damage_amount(damage_str):
    """Convertit les montants avec suffixes (K, M, B) en nombres entiers"""
    if not damage_str:
        return None
    
    damage_str = damage_str.strip().upper()
    
    # Si c'est déjà un nombre sans suffixe
    if damage_str.isdigit():
        return int(damage_str)
    
    # Utiliser regex pour extraire le nombre et le suffixe
    match = re.match(r'^([0-9]*\.?[0-9]+)([KMB]?)$', damage_str)
    if not match:
        return None
    
    number_str, suffix = match.groups()
    
    try:
        number = float(number_str)
    except ValueError:
        return None
    
    # Conversion selon le suffixe
    multipliers = {
        'K': 1000,
        'M': 1000000,
        'B': 1000000000,
        '': 1
    }
    
    if suffix in multipliers:
        result = int(number * multipliers[suffix])
        return result
    
    return None

def format_damage_display(damage):
    """Formate un montant de dégâts avec le suffixe approprié"""
    if damage == 0:
        return "0"
    
    if damage >= 1000000000:
        # Milliards
        billions = damage / 1000000000
        if billions == int(billions):
            return f"{int(billions)}B"
        else:
            return f"{billions:.1f}B"
    elif damage >= 1000000:
        # Millions
        millions = damage / 1000000
        if millions == int(millions):
            return f"{int(millions)}M"
        else:
            return f"{millions:.1f}M"
    elif damage >= 1000:
        # Milliers
        thousands = damage / 1000
        if thousands == int(thousands):
            return f"{int(thousands)}K"
        else:
            return f"{thousands:.1f}K"
    else:
        # Moins de 1000
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

class DatabaseManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données avec les nouvelles colonnes pour les difficultés"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table principale avec toutes les difficultés
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_username TEXT UNIQUE,
            
            -- Hydra difficulties
            pb_hydra_normal INTEGER DEFAULT 0,
            pb_hydra_normal_screenshot TEXT,
            pb_hydra_normal_date TIMESTAMP,
            pb_hydra_hard INTEGER DEFAULT 0,
            pb_hydra_hard_screenshot TEXT,
            pb_hydra_hard_date TIMESTAMP,
            pb_hydra_brutal INTEGER DEFAULT 0,
            pb_hydra_brutal_screenshot TEXT,
            pb_hydra_brutal_date TIMESTAMP,
            pb_hydra_nightmare INTEGER DEFAULT 0,
            pb_hydra_nightmare_screenshot TEXT,
            pb_hydra_nightmare_date TIMESTAMP,
            
            -- Chimera difficulties
            pb_chimera_easy INTEGER DEFAULT 0,
            pb_chimera_easy_screenshot TEXT,
            pb_chimera_easy_date TIMESTAMP,
            pb_chimera_normal INTEGER DEFAULT 0,
            pb_chimera_normal_screenshot TEXT,
            pb_chimera_normal_date TIMESTAMP,
            pb_chimera_hard INTEGER DEFAULT 0,
            pb_chimera_hard_screenshot TEXT,
            pb_chimera_hard_date TIMESTAMP,
            pb_chimera_brutal INTEGER DEFAULT 0,
            pb_chimera_brutal_screenshot TEXT,
            pb_chimera_brutal_date TIMESTAMP,
            pb_chimera_nightmare INTEGER DEFAULT 0,
            pb_chimera_nightmare_screenshot TEXT,
            pb_chimera_nightmare_date TIMESTAMP,
            pb_chimera_ultra INTEGER DEFAULT 0,
            pb_chimera_ultra_screenshot TEXT,
            pb_chimera_ultra_date TIMESTAMP,
            
            -- CvC (unchanged)
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
            difficulty TEXT,
            damage INTEGER,
            screenshot_filename TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_pb(self, username, boss_type, difficulty=None):
        """Récupère le PB d'un utilisateur pour un boss et difficulté spécifique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if difficulty:
            column_prefix = f"pb_{boss_type}_{difficulty}"
        else:
            column_prefix = f"pb_{boss_type}"
            
        cursor.execute(
            f"SELECT {column_prefix}, {column_prefix}_screenshot, {column_prefix}_date FROM users WHERE discord_username = ?",
            (username.lower(),)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result if result else (0, None, None)
    
    def update_user_pb(self, username, boss_type, damage, screenshot_filename, difficulty=None):
        """Met à jour le PB d'un utilisateur et supprime l'ancien screenshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupérer l'ancien screenshot pour le supprimer
        old_data = self.get_user_pb(username, boss_type, difficulty)
        old_screenshot = old_data[1] if old_data else None
        
        if difficulty:
            column_prefix = f"pb_{boss_type}_{difficulty}"
        else:
            column_prefix = f"pb_{boss_type}"
        
        # Créer l'utilisateur s'il n'existe pas, sinon mettre à jour
        cursor.execute(f'''
        INSERT INTO users (discord_username, {column_prefix}, {column_prefix}_screenshot, {column_prefix}_date, total_attempts)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
        ON CONFLICT(discord_username) 
        DO UPDATE SET 
            {column_prefix} = ?,
            {column_prefix}_screenshot = ?,
            {column_prefix}_date = CURRENT_TIMESTAMP,
            total_attempts = total_attempts + 1
        ''', (username.lower(), damage, screenshot_filename, damage, screenshot_filename))
        
        # Ajouter à l'historique
        cursor.execute('''
        INSERT INTO pb_history (username, boss_type, difficulty, damage, screenshot_filename)
        VALUES (?, ?, ?, ?, ?)
        ''', (username.lower(), boss_type, difficulty or 'none', damage, screenshot_filename))
        
        conn.commit()
        conn.close()
        
        return old_screenshot
    
    def get_leaderboard(self, boss_type, difficulty=None, limit=10, clan=None):
        """Récupère le classement pour un boss et difficulté spécifique"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if difficulty:
            column_prefix = f"pb_{boss_type}_{difficulty}"
        else:
            column_prefix = f"pb_{boss_type}"
        
        base_query = f'''
        SELECT discord_username, {column_prefix}, {column_prefix}_date 
        FROM users 
        WHERE {column_prefix} > 0
        '''
        
        if clan:
            base_query += ''' AND (
                discord_username LIKE '[''' + clan + '''] %' OR
                discord_username LIKE '[''' + clan + ''']%'
            )'''
        
        base_query += f' ORDER BY {column_prefix} DESC LIMIT ?'
        
        cursor.execute(base_query, (limit,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_user_all_pbs(self, username):
        """Récupère tous les PB d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupérer toutes les colonnes de PB
        cursor.execute('SELECT * FROM users WHERE discord_username = ?', (username.lower(),))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
            
        # Convertir en dictionnaire pour faciliter l'accès
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, result)) if result else None

class ScreenshotManager:
    def __init__(self, base_path=SCREENSHOTS_BASE_PATH):
        self.base_path = base_path
        # Créer les dossiers pour chaque boss et difficulté
        for boss_type in BOSS_CONFIG.keys():
            boss_path = os.path.join(base_path, boss_type)
            os.makedirs(boss_path, exist_ok=True)
            
            # Créer sous-dossiers pour les difficultés
            for difficulty in BOSS_CONFIG[boss_type]['difficulties']:
                difficulty_path = os.path.join(boss_path, difficulty)
                os.makedirs(difficulty_path, exist_ok=True)
    
    async def save_screenshot(self, attachment, username, damage, boss_type, difficulty=None):
        """Sauvegarde la screenshot localement"""
        try:
            timestamp = int(datetime.now().timestamp())
            file_extension = attachment.filename.split('.')[-1].lower()
            filename = f"{username.lower()}_{damage}_{timestamp}.{file_extension}"
            
            if difficulty:
                boss_path = os.path.join(self.base_path, boss_type, difficulty)
            else:
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
    
    def get_screenshot_path(self, filename, boss_type, difficulty=None):
        """Retourne le chemin complet de la screenshot"""
        if filename:
            if difficulty:
                return os.path.join(self.base_path, boss_type, difficulty, filename)
            else:
                return os.path.join(self.base_path, boss_type, filename)
        return None
    
    def delete_old_screenshot(self, filename, boss_type, difficulty=None):
        """Supprime l'ancien screenshot"""
        if filename:
            old_path = self.get_screenshot_path(filename, boss_type, difficulty)
            if old_path and os.path.exists(old_path):
                try:
                    os.remove(old_path)
                    print(f"Ancien screenshot supprimé: {filename}")
                except Exception as e:
                    print(f"Erreur suppression screenshot: {e}")

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

# Initialisation des managers
db_manager = DatabaseManager()
screenshot_manager = ScreenshotManager()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

async def handle_pb_command(ctx, boss_type, arg1=None, arg2=None):
    """Fonction générique pour gérer toutes les commandes PB avec difficultés"""
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return
    
    boss_info = BOSS_CONFIG[boss_type]
    difficulties = boss_info['difficulties']
    
    try:
        # Pour CvC (pas de difficultés)
        if not difficulties:
            # Utiliser l'ancienne logique pour CvC avec parsing des montants
            if arg1:
                damage = parse_damage_amount(arg1)
                if damage is not None:
                    await handle_pb_submission(ctx, boss_type, None, damage)
                else:  # Username
                    await show_user_pb(ctx, boss_type, None, arg1)
            else:  # Montrer son propre PB
                await show_user_pb(ctx, boss_type, None, ctx.author.display_name)
            return
        
        # Pour Hydra et Chimera (avec difficultés)
        if not arg1:
            # !pbhydra sans arguments - montrer aide
            difficulty_list = " | ".join([d.title() for d in difficulties])
            await ctx.send(
                f"❌ Please specify difficulty and damage!\n"
                f"**Available difficulties:** {difficulty_list}\n"
                f"**Shortcuts:** `nm` = Nightmare, `unm` = Ultra Nightmare\n"
                f"**Examples:**\n"
                f"`!pb{boss_type} normal 1.5M` - Submit PB with screenshot\n"
                f"`!pb{boss_type} nm 500K` - Submit Nightmare PB\n"
                f"`!pb{boss_type} hard` - Show your Hard PB\n"
                f"`!pb{boss_type} brutal username` - Show user's Brutal PB"
            )
            return
        
        # Normaliser la difficulté (gérer les diminutifs)
        normalized_difficulty = normalize_difficulty(arg1)
        
        # Vérifier si arg1 est une difficulté valide
        if normalized_difficulty in difficulties:
            difficulty = normalized_difficulty
            
            if arg2:
                damage = parse_damage_amount(arg2)
                if damage is not None:
                    # !pbhydra normal 1.5M - Soumission PB
                    await handle_pb_submission(ctx, boss_type, difficulty, damage)
                else:
                    # !pbhydra normal username - Voir PB d'un utilisateur
                    await show_user_pb(ctx, boss_type, difficulty, arg2)
            else:
                # !pbhydra normal - Voir son propre PB
                await show_user_pb(ctx, boss_type, difficulty, ctx.author.display_name)
        else:
            # arg1 n'est pas une difficulté valide
            difficulty_list = " | ".join([d.title() for d in difficulties])
            await ctx.send(
                f"❌ Invalid difficulty: `{arg1}`\n"
                f"**Available difficulties:** {difficulty_list}\n"
                f"**Shortcuts:** `nm` = Nightmare, `unm` = Ultra Nightmare"
            )
            
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

async def handle_pb_submission(ctx, boss_type, difficulty, damage):
    """Gère la soumission d'un nouveau PB"""
    if not ctx.message.attachments:
        await ctx.send("❌ Please attach a screenshot to validate your PB!")
        return
    
    attachment = ctx.message.attachments[0]
    if not any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
        await ctx.send("❌ Please attach a valid image file!")
        return
    
    username = ctx.author.display_name
    current_pb, _, _ = db_manager.get_user_pb(username, boss_type, difficulty)
    
    if damage > current_pb:
        # Sauvegarder la nouvelle screenshot
        screenshot_filename = await screenshot_manager.save_screenshot(
            attachment, username, damage, boss_type, difficulty
        )
        
        if screenshot_filename:
            # Mettre à jour la base et récupérer l'ancien screenshot
            old_screenshot = db_manager.update_user_pb(
                username, boss_type, damage, screenshot_filename, difficulty
            )
            
            # Supprimer l'ancien screenshot
            if old_screenshot:
                screenshot_manager.delete_old_screenshot(old_screenshot, boss_type, difficulty)
            
            improvement = damage - current_pb if current_pb > 0 else damage
            boss_info = BOSS_CONFIG[boss_type]
            difficulty_name = get_difficulty_display_name(difficulty) if difficulty else ""
            
            embed = discord.Embed(
                title=f"🎉 NEW {boss_info['name'].upper()} PB! 🎉",
                description=f"**{username}** just hit **{format_damage_display(damage)} damage** on {difficulty_name} {boss_info['name']}!",
                color=0x00ff00
            )
            embed.add_field(name="📈 Improvement", value=f"+{format_damage_display(improvement)} damage", inline=True)
            embed.set_image(url=attachment.url)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to save screenshot. Please try again.")
    else:
        difficulty_name = get_difficulty_display_name(difficulty) if difficulty else ""
        embed = discord.Embed(
            title="💪 Nice attempt!",
            description=f"Your damage: **{format_damage_display(damage)}**\nCurrent PB: **{format_damage_display(current_pb)}**",
            color=0xffa500
        )
        embed.add_field(
            name="Keep going!", 
            value=f"You need **{format_damage_display(current_pb - damage + 1)}** more damage for a new {difficulty_name} PB!",
            inline=False
        )
        await ctx.send(embed=embed)

async def show_user_pb(ctx, boss_type, difficulty, username):
    """Affiche le PB d'un utilisateur"""
    pb_data = db_manager.get_user_pb(username, boss_type, difficulty)
    pb_damage, screenshot_filename, pb_date = pb_data
    
    boss_info = BOSS_CONFIG[boss_type]
    difficulty_name = get_difficulty_display_name(difficulty) if difficulty else ""
    
    if pb_damage == 0:
        embed = discord.Embed(
            title=f"{boss_info['emoji']} {username}'s {difficulty_name} {boss_info['name']} PB",
            description="**No record yet**",
            color=0x666666
        )
        embed.add_field(
            name="💡 Get started!", 
            value=f"Use `!pb{boss_type} {difficulty} <damage>` with a screenshot to set your first record!\nAccepts K/M/B suffixes: `1.5M`, `500K`, etc.",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"{boss_info['emoji']} {username}'s {difficulty_name} {boss_info['name']} PB",
        description=f"**{format_damage_display(pb_damage)} damage**",
        color=boss_info['color']
    )
    if pb_date:
        formatted_date = format_datetime(pb_date)
        if formatted_date:
            embed.add_field(name="📅 Record Date", value=formatted_date, inline=False)
    
    # Envoyer la screenshot si elle existe
    if screenshot_filename:
        screenshot_path = screenshot_manager.get_screenshot_path(screenshot_filename, boss_type, difficulty)
        if screenshot_path and os.path.exists(screenshot_path):
            file = discord.File(screenshot_path, filename=f"{username}_{boss_type}_{difficulty}_pb.png")
            embed.set_image(url=f"attachment://{username}_{boss_type}_{difficulty}_pb.png")
            await ctx.send(embed=embed, file=file)
            return
    
    await ctx.send(embed=embed)

# Commandes pour chaque boss
@bot.command()
async def pbhydra(ctx, arg1: str = None, arg2: str = None):
    """Commande !pbhydra avec gestion des difficultés"""
    await handle_pb_command(ctx, 'hydra', arg1, arg2)

@bot.command()
async def pbchimera(ctx, arg1: str = None, arg2: str = None):
    """Commande !pbchimera avec gestion des difficultés"""
    await handle_pb_command(ctx, 'chimera', arg1, arg2)

@bot.command()
async def pbcvc(ctx, target_user: str = None):
    """Commande !pbcvc (sans difficultés)"""
    await handle_pb_command(ctx, 'cvc', target_user)

async def show_leaderboard(ctx, boss_type, difficulty=None, clan=None):
    """Fonction générique pour afficher les classements"""
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return
    
    try:
        # Normaliser la difficulté si spécifiée
        if difficulty:
            difficulty = normalize_difficulty(difficulty)
            if difficulty not in BOSS_CONFIG[boss_type]['difficulties']:
                difficulties = " | ".join(BOSS_CONFIG[boss_type]['difficulties'])
                await ctx.send(f"❌ Invalid difficulty. Available: {difficulties}")
                return
        
        boss_info = BOSS_CONFIG[boss_type]
        leaderboard = db_manager.get_leaderboard(boss_type, difficulty, 10, clan)
        
        if not leaderboard:
            clan_text = f" for clan {clan}" if clan else ""
            difficulty_text = f" {get_difficulty_display_name(difficulty)}" if difficulty else ""
            await ctx.send(f"❌ No{difficulty_text} {boss_info['name']} records found{clan_text} yet!")
            return
        
        # Titre avec clan et difficulté si spécifiés
        difficulty_name = get_difficulty_display_name(difficulty) if difficulty else ""
        title = f"🏆 {difficulty_name} {boss_info['name']} Leaderboard - Top 10"
        
        if clan:
            clan_info = CLAN_CONFIG.get(clan, {'name': clan, 'emoji': '🏛️'})
            title = f"{clan_info['emoji']} {clan_info['name']} - {difficulty_name} {boss_info['name']} Top 10"
        
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
                value=f"**{format_damage_display(damage)} damage**{date_text}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# Commandes de classement global avec difficultés
@bot.command()
async def top10hydra(ctx, difficulty: str = None):
    """Affiche le top 10 des PB Hydra pour une difficulté"""
    if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['hydra']['difficulties']:
        await show_leaderboard(ctx, 'hydra', difficulty)
    else:
        difficulties = " | ".join(BOSS_CONFIG['hydra']['difficulties'])
        await ctx.send(f"❌ Please specify difficulty: `!top10hydra <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare")

@bot.command()
async def top10chimera(ctx, difficulty: str = None):
    """Affiche le top 10 des PB Chimera pour une difficulté"""
    if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['chimera']['difficulties']:
        await show_leaderboard(ctx, 'chimera', difficulty)
    else:
        difficulties = " | ".join(BOSS_CONFIG['chimera']['difficulties'])
        await ctx.send(f"❌ Please specify difficulty: `!top10chimera <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare, `unm` = Ultra")

@bot.command()
async def top10cvc(ctx):
    """Affiche le top 10 des PB CvC"""
    await show_leaderboard(ctx, 'cvc')

# Commandes de classement par clan - RTF
@bot.command()
async def rtfhydra(ctx, difficulty: str = None):
    """Affiche le top 10 Hydra du clan RTF"""
    if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['hydra']['difficulties']:
        await show_leaderboard(ctx, 'hydra', difficulty, 'RTF')
    else:
        difficulties = " | ".join(BOSS_CONFIG['hydra']['difficulties'])
        await ctx.send(f"❌ Please specify difficulty: `!rtfhydra <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare")

@bot.command()
async def rtfchimera(ctx, difficulty: str = None):
    """Affiche le top 10 Chimera du clan RTF"""
    if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['chimera']['difficulties']:
        await show_leaderboard(ctx, 'chimera', difficulty, 'RTF')
    else:
        difficulties = " | ".join(BOSS_CONFIG['chimera']['difficulties'])
        await ctx.send(f"❌ Please specify difficulty: `!rtfchimera <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare, `unm` = Ultra")

@bot.command()
async def rtfcvc(ctx):
    """Affiche le top 10 CvC du clan RTF"""
    await show_leaderboard(ctx, 'cvc', None, 'RTF')

# Commandes de classement par clan - RTFC
@bot.command()
async def rtfchydra(ctx, difficulty: str = None):
    """Affiche le top 10 Hydra du clan RTFC"""
    if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['hydra']['difficulties']:
        await show_leaderboard(ctx, 'hydra', difficulty, 'RTFC')
    else:
        difficulties = " | ".join(BOSS_CONFIG['hydra']['difficulties'])
        await ctx.send(f"❌ Please specify difficulty: `!rtfchydra <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare")

@bot.command()
async def rtfcchimera(ctx, difficulty: str = None):
    """Affiche le top 10 Chimera du clan RTFC"""
    if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['chimera']['difficulties']:
        await show_leaderboard(ctx, 'chimera', difficulty, 'RTFC')
    else:
        difficulties = " | ".join(BOSS_CONFIG['chimera']['difficulties'])
        await ctx.send(f"❌ Please specify difficulty: `!rtfcchimera <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare, `unm` = Ultra")

@bot.command()
async def rtfccvc(ctx):
    """Affiche le top 10 CvC du clan RTFC"""
    await show_leaderboard(ctx, 'cvc', None, 'RTFC')

# Commandes de classement par clan - RTFR
@bot.command()
async def rtfrhydra(ctx, difficulty: str = None):
    """Affiche le top 10 Hydra du clan RTFR"""
    if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['hydra']['difficulties']:
        await show_leaderboard(ctx, 'hydra', difficulty, 'RTFR')
    else:
        difficulties = " | ".join(BOSS_CONFIG['hydra']['difficulties'])
        await ctx.send(f"❌ Please specify difficulty: `!rtfrhydra <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare")

@bot.command()
async def rtfrchimera(ctx, difficulty: str = None):
    """Affiche le top 10 Chimera du clan RTFR"""
    if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['chimera']['difficulties']:
        await show_leaderboard(ctx, 'chimera', difficulty, 'RTFR')
    else:
        difficulties = " | ".join(BOSS_CONFIG['chimera']['difficulties'])
        await ctx.send(f"❌ Please specify difficulty: `!rtfrchimera <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare, `unm` = Ultra")

@bot.command()
async def rtfrcvc(ctx):
    """Affiche le top 10 CvC du clan RTFR"""
    await show_leaderboard(ctx, 'cvc', None, 'RTFR')

@bot.command()
async def mystats(ctx, target_user: str = None):
    """Affiche tous les PB d'un utilisateur avec les nouvelles difficultés"""
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return
    
    try:
        username = target_user if target_user else ctx.author.display_name
        user_data = db_manager.get_user_all_pbs(username)
        
        if not user_data:
            await ctx.send(f"❌ No data found for **{username}**.")
            return
        
        embed = discord.Embed(
            title=f"📊 {username}'s Complete Stats",
            color=0x00bfff
        )
        
        # Hydra - toutes les difficultés
        hydra_stats = []
        for difficulty in BOSS_CONFIG['hydra']['difficulties']:
            pb_key = f'pb_hydra_{difficulty}'
            date_key = f'pb_hydra_{difficulty}_date'
            
            if pb_key in user_data and user_data[pb_key] > 0:
                pb_value = user_data[pb_key]
                pb_date = user_data.get(date_key)
                date_text = f" • {format_date_only(pb_date)}" if pb_date else ""
                hydra_stats.append(f"**{difficulty.title()}:** {format_damage_display(pb_value)}{date_text}")
        
        hydra_text = "\n".join(hydra_stats) if hydra_stats else "No records"
        embed.add_field(name="🐍 Hydra PBs", value=hydra_text, inline=False)
        
        # Chimera - toutes les difficultés
        chimera_stats = []
        for difficulty in BOSS_CONFIG['chimera']['difficulties']:
            pb_key = f'pb_chimera_{difficulty}'
            date_key = f'pb_chimera_{difficulty}_date'
            
            if pb_key in user_data and user_data[pb_key] > 0:
                pb_value = user_data[pb_key]
                pb_date = user_data.get(date_key)
                date_text = f" • {format_date_only(pb_date)}" if pb_date else ""
                display_name = "Ultra Nightmare" if difficulty == "ultra" else difficulty.title()
                chimera_stats.append(f"**{display_name}:** {format_damage_display(pb_value)}{date_text}")
        
        chimera_text = "\n".join(chimera_stats) if chimera_stats else "No records"
        embed.add_field(name="🦁 Chimera PBs", value=chimera_text, inline=False)
        
        # CvC
        cvc_pb = user_data.get('pb_cvc', 0)
        cvc_date = user_data.get('pb_cvc_date')
        cvc_text = f"**{format_damage_display(cvc_pb)} damage**" if cvc_pb > 0 else "No record"
        if cvc_pb > 0 and cvc_date:
            formatted_date = format_date_only(cvc_date)
            if formatted_date:
                cvc_text += f" • {formatted_date}"
        embed.add_field(name="⚔️ CvC PB", value=cvc_text, inline=False)
        
        # Total combiné
        total_damage = 0
        for difficulty in BOSS_CONFIG['hydra']['difficulties']:
            total_damage += user_data.get(f'pb_hydra_{difficulty}', 0)
        for difficulty in BOSS_CONFIG['chimera']['difficulties']:
            total_damage += user_data.get(f'pb_chimera_{difficulty}', 0)
        total_damage += user_data.get('pb_cvc', 0)
        
        embed.add_field(name="💯 Total Combined Damage", value=f"**{format_damage_display(total_damage)}**", inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def guide(ctx):
    """Affiche la liste des commandes disponibles avec les nouvelles difficultés"""
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return
    
    embed = discord.Embed(
        title="🤖 RTF Bot - Commands Guide",
        description="Here are all available commands for tracking your Personal Bests!",
        color=0x00bfff
    )
    
    # Info sur les formats de dégâts
    embed.add_field(
        name="💰 Damage Formats",
        value="**Accepted formats:** `1500000`, `1.5M`, `500K`, `2B`\n" +
              "**Suffixes:** K = thousands, M = millions, B = billions\n" +
              "**Shortcuts:** `nm` = Nightmare, `unm` = Ultra Nightmare",
        inline=False
    )
    
    # Commandes PB Hydra
    embed.add_field(
        name="🐍 Hydra Commands",
        value="**Difficulties:** Normal | Hard | Brutal | Nightmare (nm)\n" +
              "`!pbhydra <difficulty> <damage>` - Submit PB + screenshot\n" +
              "`!pbhydra <difficulty>` - Show your PB\n" +
              "`!pbhydra <difficulty> <user>` - Show user's PB",
        inline=False
    )
    
    # Commandes PB Chimera
    embed.add_field(
        name="🦁 Chimera Commands",
        value="**Difficulties:** Easy | Normal | Hard | Brutal | Nightmare (nm) | Ultra (unm)\n" +
              "`!pbchimera <difficulty> <damage>` - Submit PB + screenshot\n" +
              "`!pbchimera <difficulty>` - Show your PB\n" +
              "`!pbchimera <difficulty> <user>` - Show user's PB",
        inline=False
    )
    
    # Commandes PB CvC
    embed.add_field(
        name="⚔️ CvC Commands",
        value="`!pbcvc <damage>` - Submit PB + screenshot\n" +
              "`!pbcvc` - Show your PB\n" +
              "`!pbcvc <username>` - Show user's PB",
        inline=False
    )
    
    # Classements globaux
    embed.add_field(
        name="🌍 Global Leaderboards",
        value="`!top10hydra <difficulty>` - Global Hydra rankings\n" +
              "`!top10chimera <difficulty>` - Global Chimera rankings\n" +
              "`!top10cvc` - Global CvC rankings",
        inline=False
    )
    
    # Classements par clan
    embed.add_field(
        name="🏛️ Clan Leaderboards",
        value="**RTF:** `!rtfhydra <diff>` `!rtfchimera <diff>` `!rtfcvc`\n" +
              "**RTFC:** `!rtfchydra <diff>` `!rtfcchimera <diff>` `!rtfccvc`\n" +
              "**RTFR:** `!rtfrhydra <diff>` `!rtfrchimera <diff>` `!rtfrcvc`",
        inline=False
    )
    
    # Stats et aide
    embed.add_field(
        name="📈 Stats & Info",
        value="`!mystats` - View all your PBs\n" +
              "`!mystats <username>` - View someone's PBs\n" +
              "`!guide` - Show this help message",
        inline=False
    )
    
    # Instructions
    embed.add_field(
        name="💡 Examples",
        value="`!pbhydra brutal 1.5M` - Submit Brutal Hydra PB\n" +
              "`!pbchimera unm 500K` - Submit Ultra Nightmare PB\n" +
              "`!pbcvc 2.3M` - Submit CvC PB\n" +
              "`!rtfhydra nm` - RTF clan Nightmare rankings\n" +
              "**Always attach screenshot when submitting PBs!**",
        inline=False
    )
    
    embed.set_footer(text="🎮 Old screenshots are automatically deleted when you set new PBs!")
    
    await ctx.send(embed=embed)

# Ajout du token bot (à remplacer par votre token)
# bot.run('YOUR_BOT_TOKEN_HERE')
