# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from config import AUTHORIZED_CHANNEL_ID, BOSS_CONFIG
from utils.helpers import format_damage_display, format_date_only
from utils.pb_handler import db_manager

class MyStats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mystats")
    async def mystats(self, ctx, target_user: str = None):
        
        if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
            return

        try:

        if not target_user:
            # Pas d'argument -> soi-même
            target_id = ctx.author.id
            display_name = ctx.author.display_name

        else:
            arg = target_user.strip()

            # mention <@123456789>
            if arg.startswith("<@") and arg.endswith(">"):
                target_id = int(arg.strip("<@!>"))
                user = ctx.guild.get_member(target_id)
                display_name = user.display_name if user else f"<@{target_id}>"

            # ID numérique
            elif arg.isdigit():
                target_id = int(arg)
                user = ctx.guild.get_member(target_id)
                display_name = user.display_name if user else f"<@{target_id}>"

            # nom (fallback)
            else:
                matches = db_manager.find_user_by_name(arg)
                if not matches:
                    await ctx.send(f"❌ User **{arg}** not found.")
                    return
                if len(matches) > 1:
                    await ctx.send(f"⚠️ Multiple users found for **{arg}**, please be more specific.")
                    return

                target_id, display_name = matches[0]

        user_data = db_manager.get_user_all_pbs(target_id)

        if not user_data:
            await ctx.send(f"❌ No data found for **{display_name}**.")
            return

        embed = discord.Embed(
            title=f"📊 {display_name}'s Complete Stats",
            color=0x00bfff
        )

        # Hydra
        hydra_stats = []
        for difficulty in BOSS_CONFIG['hydra']['difficulties']:
            pb_key = f'pb_hydra_{difficulty}'
            date_key = f'pb_hydra_{difficulty}_date'

            if pb_key in user_data and user_data[pb_key] > 0:
                pb_value = user_data[pb_key]
                pb_date = user_data.get(date_key)
                date_text = f" • {format_date_only(pb_date)}" if pb_date else ""
                hydra_stats.append(f"**{difficulty.title()}:** {format_damage_display(pb_value)}{date_text}")

        embed.add_field(
            name="⚔️ Hydra PBs",
            value="\n".join(hydra_stats) if hydra_stats else "No records",
            inline=False
        )

        # Chimera
        chimera_stats = []
        for difficulty in BOSS_CONFIG['chimera']['difficulties']:
            pb_key = f'pb_chimera_{difficulty}'
            date_key = f'pb_chimera_{difficulty}_date'

            if pb_key in user_data and user_data[pb_key] > 0:
                pb_value = user_data[pb_key]
                pb_date = user_data.get(date_key)
                date_text = f" • {format_date_only(pb_date)}" if pb_date else ""
                name = "Ultra Nightmare" if difficulty == "ultra" else difficulty.title()
                chimera_stats.append(f"**{name}:** {format_damage_display(pb_value)}{date_text}")

        embed.add_field(
            name="🛡️ Chimera PBs",
            value="\n".join(chimera_stats) if chimera_stats else "No records",
            inline=False
        )

        # CvC
        cvc_pb = user_data.get('pb_cvc', 0)
        cvc_date = user_data.get('pb_cvc_date')
        cvc_text = f"**{format_damage_display(cvc_pb)} damage**" if cvc_pb > 0 else "No record"
        if cvc_pb and cvc_date:
            cvc_text += f" • {format_date_only(cvc_date)}"
        embed.add_field(name="🗡️ CvC PB", value=cvc_text, inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
