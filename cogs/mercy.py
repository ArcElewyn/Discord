# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from config import AUTHORIZED_CHANNEL_ID
from utils.MercyManager_class import MercyManager
from utils.helpers import calc_chance_and_guarantee

VALID_SHARDS = ["ancient", "void", "sacred", "primal", "remnant"]

class Mercy(commands.Cog):
    """Cog pour gérer les pulls de Mercy"""

    def __init__(self, bot):
        self.bot = bot
        self.mercy_manager = MercyManager()

    @commands.command(name="mercy")
    async def mercy(self, ctx, action: str = None, arg1: str = None, arg2: str = None):
        if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
            return

        user_id = str(ctx.author.id)

        # ----- SHOW -----
        if action == "show":
            pulls_dict = self.mercy_manager.get_all_pulls(user_id)
            if not pulls_dict:
                await ctx.send("ℹ️ You don't have any mercy data yet.")
                return

            embed = discord.Embed(
                title=f"🎲 Mercy Status for {ctx.author.display_name}",
                color=0x00bfff
            )

            for shard_type, pulls in pulls_dict.items():
                if shard_type == "primal":
                    for sub_type in ["primal_legendary", "primal_mythical"]:
                        sub_pulls = pulls_dict.get(sub_type, 0)
                        chance, guaranteed_at, remaining = calc_chance_and_guarantee(sub_type, sub_pulls)
                        guaranteed_text = f" (Guaranteed at {guaranteed_at} pulls, {remaining} remaining)" if guaranteed_at else ""
                        embed.add_field(
                            name=sub_type.replace("_", " ").title(),
                            value=f"Pulled: **{sub_pulls}/{guaranteed_at} shards** → {chance:.1f}% chance{guaranteed_text}",
                            inline=False
                        )
                else:
                    chance, guaranteed_at, remaining = calc_chance_and_guarantee(shard_type, pulls)
                    guaranteed_text = f" (Guaranteed at {guaranteed_at} pulls, {remaining} remaining)" if guaranteed_at else ""
                    embed.add_field(
                        name=shard_type.replace("_", " ").title(),
                        value=f"Pulled: **{pulls}/{guaranteed_at} shards** → {chance:.1f}% chance{guaranteed_text}",
                        inline=False
                    )

            await ctx.send(embed=embed)

        # ----- ADD -----
        elif action == "add" and arg1 and arg2:
            try:
                pulls_to_add = int(arg1)
            except ValueError:
                await ctx.send("❌ Number of pulls must be an integer.")
                return

            shard_type = arg2.lower()
            if shard_type not in VALID_SHARDS:
                await ctx.send(f"❌ Invalid shard type. Available: {', '.join(VALID_SHARDS)}")
                return

            if shard_type == "primal":
                messages = []
                for sub_type in ["primal_legendary", "primal_mythical"]:
                    new_pulls = self.mercy_manager.add_pulls(user_id, sub_type, pulls_to_add)
                    chance, guaranteed_at, remaining = calc_chance_and_guarantee(sub_type, new_pulls)
                    messages.append(f"✅ Added {pulls_to_add} pulls to **{sub_type.replace('_', ' ').title()}**: {new_pulls}/{guaranteed_at} → {chance:.1f}% ({remaining} remaining)")
                await ctx.send("\n".join(messages))
            else:
                new_pulls = self.mercy_manager.add_pulls(user_id, shard_type, pulls_to_add)
                chance, guaranteed_at, remaining = calc_chance_and_guarantee(shard_type, new_pulls)
                await ctx.send(f"✅ Added {pulls_to_add} pulls to **{shard_type}** mercy. Now: **{new_pulls}/{guaranteed_at}** pulls → {chance:.1f}% chance ({remaining} remaining)")

        # ----- RESET -----
        elif action == "reset" and arg1:
            shard_type = arg1.lower()
            sub_type = arg2.lower() if arg2 else None

            if shard_type == "primal":
                if sub_type == "legendary":
                    self.mercy_manager.reset_pulls(user_id, "primal_legendary")
                    await ctx.send("🧾 Mercy for Primal Legendary has been reset.")
                elif sub_type == "mythical":
                    self.mercy_manager.reset_pulls(user_id, "primal_mythical")
                    await ctx.send("🧾 Mercy for Primal Mythical has been reset.")
                elif sub_type is None:
                    messages = []
                    for s in ["primal_legendary", "primal_mythical"]:
                        self.mercy_manager.reset_pulls(user_id, s)
                        messages.append(f"🧾 Mercy for {s.replace('_', ' ').title()} has been reset.")
                    await ctx.send("\n".join(messages))
                else:
                    await ctx.send("❌ Invalid primal subtype. Use `legendary` or `mythical`.")
            else:
                if shard_type not in VALID_SHARDS:
                    await ctx.send(f"❌ Invalid shard type. Available: {', '.join(VALID_SHARDS)}")
                    return
                self.mercy_manager.reset_pulls(user_id, shard_type)
                await ctx.send(f"🧾 Mercy for **{shard_type}** has been reset.")

        # ----- HELP -----
        else:
            await ctx.send("ℹ️ Usage: `!mercy add <nb> <type>`, `!mercy reset <type> [subtype]`, `!mercy show`")


async def setup(bot):
    await bot.add_cog(Mercy(bot))
