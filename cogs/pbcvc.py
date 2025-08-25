import discord
from discord.ext import commands
from config import AUTHORIZED_CHANNEL_ID
from utils.pb_handler import handle_pb_command

class Pbcvc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pbcvc")
    async def pbcvc(self, ctx, target_user: str = None):
        """Commande !pbcvc (sans difficultées)"""
        await handle_pb_command(ctx, 'cvc', target_user)

async def setup(bot):
    await bot.add_cog(Pbcvc(bot))