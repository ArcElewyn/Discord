import os
import discord
from config import AUTHORIZED_CHANNEL_ID, BOSS_CONFIG
from utils.helpers import (
    parse_damage_amount,
    normalize_difficulty,
    get_difficulty_display_name,
    format_damage_display,
    format_datetime,
)

db_manager = None
screenshot_manager = None

def set_managers(db, ss):
    """Injection des managers (appelée une seule fois depuis bot.py)"""
    global db_manager, screenshot_manager
    db_manager = db
    screenshot_manager = ss

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
