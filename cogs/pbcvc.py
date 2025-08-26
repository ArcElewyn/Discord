# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from utils.pb_handler import handle_pb_command

class Pbcvc(commands.Cog):
    """Cog pour gérer les Personal Bests CvC (sans difficultés)"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pbcvc")
    async def pbcvc(self, ctx, target_user: str = None):
        """Commande !pbcvc"""
        await handle_pb_command(ctx, 'cvc', target_user)

async def setup(bot):
    await bot.add_cog(Pbcvc(bot))
