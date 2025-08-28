# -*- coding: utf-8 -*-
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
            if arg1:
                damage = parse_damage_amount(arg1)
                if damage is not None:
                    await handle_pb_submission(ctx, boss_type, None, damage)
                else:
                    await show_user_pb(ctx, boss_type, None, arg1)
            else:
                await show_user_pb(ctx, boss_type, None, ctx.author.display_name)
            return
        
        # Pour Hydra et Chimera (avec difficultés)
        if not arg1:
            difficulty_list = " | ".join([d.title() for d in difficulties])
            await ctx.send(
                f"⚠️ Please specify difficulty and damage!\n"
                f"**Available difficulties:** {difficulty_list}\n"
                f"**Shortcuts:** `nm` = Nightmare, `unm` = Ultra Nightmare\n"
                f"**Examples:**\n"
                f"`!pb{boss_type} normal 1.5M` - Submit PB with screenshot\n"
                f"`!pb{boss_type} nm 500K` - Submit Nightmare PB\n"
                f"`!pb{boss_type} hard` - Show your Hard PB\n"
                f"`!pb{boss_type} brutal username` - Show user's Brutal PB"
            )
            return
        
        normalized_difficulty = normalize_difficulty(arg1)
        
        if normalized_difficulty in difficulties:
            difficulty = normalized_difficulty
            
            if arg2:
                damage = parse_damage_amount(arg2)
                if damage is not None:
                    await handle_pb_submission(ctx, boss_type, difficulty, damage)
                else:
                    await show_user_pb(ctx, boss_type, difficulty, arg2)
            else:
                await show_user_pb(ctx, boss_type, difficulty, ctx.author.display_name)
        else:
            difficulty_list = " | ".join([d.title() for d in difficulties])
            await ctx.send(
                f"⚠️ Invalid difficulty: `{arg1}`\n"
                f"**Available difficulties:** {difficulty_list}\n"
                f"**Shortcuts:** `nm` = Nightmare, `unm` = Ultra Nightmare"
            )
            
    except Exception as e:
        await ctx.send(f"⚠️ Error: {str(e)}")

async def handle_pb_submission(ctx, boss_type, difficulty, damage):
    """Gère la soumission d'un nouveau PB"""
    if not ctx.message.attachments:
        await ctx.send("⚠️ Please attach a screenshot to validate your PB!")
        return
    
    attachment = ctx.message.attachments[0]
    if not any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
        await ctx.send("⚠️ Please attach a valid image file!")
        return
    
    user_id = ctx.author.id
    username = ctx.author.display_name
    current_pb, _, _ = db_manager.get_user_pb(user_id, boss_type, difficulty)
    
    if damage > current_pb:
        screenshot_filename = await screenshot_manager.save_screenshot(
            attachment, username, damage, boss_type, difficulty
        )
        
        if screenshot_filename:
            old_screenshot = db_manager.update_user_pb(
                user_id, username, boss_type, damage, screenshot_filename, difficulty
            )
            
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

            # Envoi du screenshot correctement pour Discord
            screenshot_path = screenshot_manager.get_screenshot_path(screenshot_filename, boss_type, difficulty)
            if screenshot_path and os.path.exists(screenshot_path):
                file = discord.File(screenshot_path, filename=screenshot_filename)
                embed.set_image(url=f"attachment://{screenshot_filename}")
                await ctx.send(embed=embed, file=file)
            else:
                await ctx.send(embed=embed)
        else:
            await ctx.send("⚠️ Failed to save screenshot. Please try again.")
    else:
        # Si le PB n'est pas battu, on montre le PB existant
        await show_user_pb(ctx, boss_type, difficulty, username)

async def show_user_pb(ctx, boss_type, difficulty, target_user):
    """Affiche le PB actuel d'un utilisateur"""
    # Si target_user est un nom d'utilisateur, on essaie de le trouver
    if isinstance(target_user, str) and not target_user.isdigit():
        # D'abord, vérifier si c'est l'utilisateur actuel
        if target_user.lower() == ctx.author.display_name.lower():
            user_id = ctx.author.id
            display_name = ctx.author.display_name
        else:
            # Chercher dans la base de données
            matches = db_manager.find_user_by_name(target_user)
            if not matches:
                await ctx.send(f"⚠️ User **{target_user}** not found in database.")
                return
            elif len(matches) > 1:
                await ctx.send(f"⚠️ Multiple users found for **{target_user}**. Please be more specific.")
                return
            else:
                user_id, display_name = matches[0]
    else:
        # Si c'est l'utilisateur actuel
        user_id = ctx.author.id
        display_name = ctx.author.display_name
    
    current_pb, screenshot, date = db_manager.get_user_pb(user_id, boss_type, difficulty)
    boss_info = BOSS_CONFIG[boss_type]
    difficulty_name = get_difficulty_display_name(difficulty) if difficulty else ""
    
    if current_pb > 0:
        embed = discord.Embed(
            title=f"📊 {display_name}'s {difficulty_name} {boss_info['name']} PB",
            description=f"**{format_damage_display(current_pb)} damage**",
            color=0x00bfff
        )
        if date:
            embed.add_field(name="📅 Date", value=format_datetime(date), inline=True)

        # Envoi du screenshot local correctement
        if screenshot:
            screenshot_path = screenshot_manager.get_screenshot_path(screenshot, boss_type, difficulty)
            if screenshot_path and os.path.exists(screenshot_path):
                file = discord.File(screenshot_path, filename=screenshot)
                embed.set_image(url=f"attachment://{screenshot}")
                await ctx.send(embed=embed, file=file)
                return

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"⚠️ No PB found for **{display_name}** on {difficulty_name} {boss_info['name']}.")