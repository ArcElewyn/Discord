import discord
from discord.ext import commands
from config import AUTHORIZED_CHANNEL_ID
from utils.pb_handler import handle_pb_command

class Pbhydra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pbhydra")
    async def pbhydra(self, ctx, arg1: str = None, arg2: str = None):
        """Commande !pbhydra avec gestion des difficultés"""
        await handle_pb_command(ctx, 'hydra', arg1, arg2)

def setup(bot):
    bot.add_cog(Pbhydra(bot))