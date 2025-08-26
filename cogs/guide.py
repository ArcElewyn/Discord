import discord
from discord.ext import commands
from config import AUTHORIZED_CHANNEL_ID

class Guide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="guide")
    async def guide(self, ctx):
        """Affiche la liste des commandes disponibles avec les nouvelles difficultÃ©s"""
        if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
            return
        
        embed = discord.Embed(
            title="ðŸ¤– RTF Bot - Commands Guide",
            description="Here are all available commands for tracking your Personal Bests!",
            color=0x00bfff
        )
        
        # Info sur les formats de dÃ©gÃ¢ts
        embed.add_field(
            name="ðŸ’° Damage Formats",
            value="**Accepted formats:** `1500000`, `1.5M`, `500K`, `2B`\n" +
                  "**Suffixes:** K = thousands, M = millions, B = billions\n" +
                  "**Shortcuts:** `nm` = Nightmare, `unm` = Ultra Nightmare",
            inline=False
        )
        
        # Commandes PB Hydra
        embed.add_field(
            name="ðŸ Hydra Commands",
            value="**Difficulties:** Normal | Hard | Brutal | Nightmare (nm)\n" +
                  "`!pbhydra <difficulty> <damage>` - Submit PB + screenshot\n" +
                  "`!pbhydra <difficulty>` - Show your PB\n" +
                  "`!pbhydra <difficulty> <user>` - Show user's PB",
            inline=False
        )
        
        # Commandes PB Chimera
        embed.add_field(
            name="ðŸ¦ Chimera Commands",
            value="**Difficulties:** Easy | Normal | Hard | Brutal | Nightmare (nm) | Ultra (unm)\n" +
                  "`!pbchimera <difficulty> <damage>` - Submit PB + screenshot\n" +
                  "`!pbchimera <difficulty>` - Show your PB\n" +
                  "`!pbchimera <difficulty> <user>` - Show user's PB",
            inline=False
        )
        
        # Commandes PB CvC
        embed.add_field(
            name="âš”ï¸ CvC Commands",
            value="`!pbcvc <damage>` - Submit PB + screenshot\n" +
                  "`!pbcvc` - Show your PB\n" +
                  "`!pbcvc <username>` - Show user's PB",
            inline=False
        )
        
        # Commandes Mercy
        embed.add_field(
            name="ðŸŽ² Mercy Commands",
            value="`!mercy show` - Show your current mercy pulls\n" +
                  "`!mercy add <nb> <type>` - Add pulls to a shard type\n" +
                  "`!mercy reset <type>` - Reset pulls for a shard type\n" +
                  "**Available types:** ancient, void, sacred, primal_legendary, primal_mythical, remnant",
            inline=False
        )
        
        # Classements globaux
        embed.add_field(
            name="ðŸŒ Global Leaderboards",
            value="`!top10hydra <difficulty>` - Global Hydra rankings\n" +
                  "`!top10chimera <difficulty>` - Global Chimera rankings\n" +
                  "`!top10cvc` - Global CvC rankings",
            inline=False
        )
        
        # Classements par clan
        embed.add_field(
            name="ðŸ›ï¸ Clan Leaderboards",
            value="**RTF:** `!rtfhydra <diff>` `!rtfchimera <diff>` `!rtfcvc`\n" +
                  "**RTFC:** `!rtfchydra <diff>` `!rtfcchimera <diff>` `!rtfccvc`\n" +
                  "**RTFR:** `!rtfrhydra <diff>` `!rtfrchimera <diff>` `!rtfrcvc`",
            inline=False
        )
        
        # Stats et aide
        embed.add_field(
            name="ðŸ“ˆ Stats & Info",
            value="`!mystats` - View all your PBs\n" +
                  "`!mystats <username>` - View someone's PBs\n" +
                  "`!guide` - Show this help message",
            inline=False
        )
        
        # Instructions
        embed.add_field(
            name="ðŸ’¡ Examples",
            value="`!pbhydra brutal 1.5M` - Submit Brutal Hydra PB\n" +
                  "`!pbchimera unm 500K` - Submit Ultra Nightmare PB\n" +
                  "`!pbcvc 2.3M` - Submit CvC PB\n" +
                  "`!mercy add 50 ancient` - Add 50 pulls to Ancient shard\n" +
                  "`!mercy show` - Show your mercy pulls\n" +
                  "`!rtfhydra nm` - RTF clan Nightmare rankings\n" +
                  "**Always attach screenshot when submitting PBs!**",
            inline=False
        )
        
        embed.set_footer(text="ðŸŽ® Old screenshots are automatically deleted when you set new PBs!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Guide(bot))
