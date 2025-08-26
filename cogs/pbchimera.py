# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from utils.pb_handler import handle_pb_command

class Pbchimera(commands.Cog):
    """Cog pour gérer les Personal Bests Chimera"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pbchimera")
    async def pbchimera(self, ctx, arg1: str = None, arg2: str = None):
        """Commande !pbchimera avec gestion des difficultés"""
        await handle_pb_command(ctx, 'chimera', arg1, arg2)

async def setup(bot):
    await bot.add_cog(Pbchimera(bot))
