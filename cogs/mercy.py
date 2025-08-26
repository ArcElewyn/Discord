import discord
from discord.ext import commands
from config import AUTHORIZED_CHANNEL_ID
from utils.MercyManager_class import MercyManager
from utils.helpers import calc_chance_and_guarantee

VALID_SHARDS = ["ancient", "void", "sacred", "primal", "remnant"]

class Mercy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mercy_manager = MercyManager()

    @commands.command(name="mercy")
    async def mercy(self, ctx, action: str = None, arg1: str = None, arg2: str = None):
        if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
            return

        user_id = str(ctx.author.id)

        if action == "show":
            pulls_dict = self.mercy_manager.get_all_pulls(user_id)
            if not pulls_dict:
                await ctx.send("âŒ You don't have any mercy data yet.")
                return

            embed = discord.Embed(title=f"ðŸŽ² Mercy Status for {ctx.author.display_name}", color=0x00bfff)

            for shard_type, pulls in pulls_dict.items():
                if shard_type == "primal":
                    for sub_type in ["primal_legendary", "primal_mythical"]:
                        chance, guaranteed_at = self.calc_chance_and_guarantee(sub_type, pulls)
                        guaranteed_text = f" (Guaranteed at {int(guaranteed_at)} pulls)" if guaranteed_at else ""
                        embed.add_field(
                            name=sub_type.replace("_", " ").title(),
                            value=f"Pulled: **{pulls} shards** â†’ {chance:.1f}% chance{guaranteed_text}",
                            inline=False
                        )
                else:
                    chance, guaranteed_at = self.calc_chance_and_guarantee(shard_type, pulls)
                    guaranteed_text = f" (Guaranteed at {int(guaranteed_at)} pulls)" if guaranteed_at else ""
                    embed.add_field(
                        name=shard_type.replace("_", " ").title(),
                        value=f"Pulled: **{pulls} shards** â†’ {chance:.1f}% chance{guaranteed_text}",
                        inline=False
                    )

            await ctx.send(embed=embed)

        elif action == "add" and arg1 and arg2:
            try:
                pulls_to_add = int(arg1)
            except ValueError:
                await ctx.send("âŒ Number of pulls must be an integer.")
                return

            shard_type = arg2.lower()
            if shard_type not in VALID_SHARDS:
                await ctx.send(f"âŒ Invalid shard type. Available: {', '.join(VALID_SHARDS)}")
                return

            new_pulls = self.mercy_manager.add_pulls(user_id, shard_type, pulls_to_add)
            await ctx.send(f"âœ… Added {pulls_to_add} pulls to **{shard_type}** mercy. Total: {new_pulls}")

        elif action == "reset" and arg1:
            shard_type = arg1.lower()
            if shard_type not in VALID_SHARDS:
                await ctx.send(f"âŒ Invalid shard type. Available: {', '.join(VALID_SHARDS)}")
                return

            self.mercy_manager.reset_pulls(user_id, shard_type)
            await ctx.send(f"ðŸ”„ Mercy for **{shard_type}** has been reset.")

        else:
            await ctx.send("âŒ Usage: `!mercy add <nb> <type>`, `!mercy reset <type>`, `!mercy show`")

async def setup(bot):
    await bot.add_cog(Mercy(bot))
