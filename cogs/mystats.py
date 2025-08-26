import discord
from discord.ext import commands
from config import AUTHORIZED_CHANNEL_ID, BOSS_CONFIG
from utils.helpers import format_damage_display, format_date_only
from utils.pb_handler import db_manager  # ou set_db_manager si nÃ©cessaire

class MyStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mystats")
    async def mystats(self, ctx, target_user: str = None):
        """Affiche tous les PB d'un utilisateur avec les nouvelles difficultÃ©s"""
        if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
            return
        
        try:
            username = target_user if target_user else ctx.author.display_name
            user_data = db_manager.get_user_all_pbs(username)
            
            if not user_data:
                await ctx.send(f"âŒ No data found for **{username}**.")
                return
            
            embed = discord.Embed(
                title=f"ðŸ“Š {username}'s Complete Stats",
                color=0x00bfff
            )
            
            # Hydra - toutes les difficultÃ©s
            hydra_stats = []
            for difficulty in BOSS_CONFIG['hydra']['difficulties']:
                pb_key = f'pb_hydra_{difficulty}'
                date_key = f'pb_hydra_{difficulty}_date'
                
                if pb_key in user_data and user_data[pb_key] > 0:
                    pb_value = user_data[pb_key]
                    pb_date = user_data.get(date_key)
                    date_text = f" â€¢ {format_date_only(pb_date)}" if pb_date else ""
                    hydra_stats.append(f"**{difficulty.title()}:** {format_damage_display(pb_value)}{date_text}")
            
            hydra_text = "\n".join(hydra_stats) if hydra_stats else "No records"
            embed.add_field(name="ðŸ Hydra PBs", value=hydra_text, inline=False)
            
            # Chimera - toutes les difficultÃ©s
            chimera_stats = []
            for difficulty in BOSS_CONFIG['chimera']['difficulties']:
                pb_key = f'pb_chimera_{difficulty}'
                date_key = f'pb_chimera_{difficulty}_date'
                
                if pb_key in user_data and user_data[pb_key] > 0:
                    pb_value = user_data[pb_key]
                    pb_date = user_data.get(date_key)
                    date_text = f" â€¢ {format_date_only(pb_date)}" if pb_date else ""
                    display_name = "Ultra Nightmare" if difficulty == "ultra" else difficulty.title()
                    chimera_stats.append(f"**{display_name}:** {format_damage_display(pb_value)}{date_text}")
            
            chimera_text = "\n".join(chimera_stats) if chimera_stats else "No records"
            embed.add_field(name="ðŸ¦ Chimera PBs", value=chimera_text, inline=False)
            
            # CvC
            cvc_pb = user_data.get('pb_cvc', 0)
            cvc_date = user_data.get('pb_cvc_date')
            cvc_text = f"**{format_damage_display(cvc_pb)} damage**" if cvc_pb > 0 else "No record"
            if cvc_pb > 0 and cvc_date:
                formatted_date = format_date_only(cvc_date)
                if formatted_date:
                    cvc_text += f" â€¢ {formatted_date}"
            embed.add_field(name="âš”ï¸ CvC PB", value=cvc_text, inline=False)
            
            # Total combinÃ©
            total_damage = 0
            for difficulty in BOSS_CONFIG['hydra']['difficulties']:
                total_damage += user_data.get(f'pb_hydra_{difficulty}', 0)
            for difficulty in BOSS_CONFIG['chimera']['difficulties']:
                total_damage += user_data.get(f'pb_chimera_{difficulty}', 0)
            total_damage += user_data.get('pb_cvc', 0)
            
            embed.add_field(name="ðŸ’¯ Total Combined Damage", value=f"**{format_damage_display(total_damage)}**", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"âŒ Error: {e}")


# Pour charger le Cog
async def setup(bot):
    await bot.add_cog(MyStats(bot))
