# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from config import AUTHORIZED_CHANNEL_ID
from utils.MercyManager_class import MercyManager


VALID_SHARDS = ["ancient", "void", "sacred", "remnant", "primal", "primal_legendary", "primal_mythical"]


class Mercy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mercy = MercyManager()

    @commands.command(name="mercy")
    async def mercy_cmd(self, ctx, action=None, arg1=None, arg2=None):
        if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
            return

        user_id = str(ctx.author.id)

        if action == "show":
            return await self.show(ctx, user_id)

        if action == "add":
            return await self.add(ctx, user_id, arg1, arg2)

        if action == "reset":
            return await self.reset(ctx, user_id, arg1, arg2)

        await ctx.send("ℹ️ Usage: `!mercy show`, `!mercy add <nb> <type>`, `!mercy reset <type> [subtype]`")

    # -------------------------
    # SHOW
    # -------------------------
    async def show(self, ctx, user_id):
        pulls = self.mercy.get_all_pulls(user_id)

        if not pulls:
            await ctx.send("ℹ️ No mercy data yet.")
            return

        embed = discord.Embed(
            title=f"🎲 Mercy status for {ctx.author.name}",
            color=0x00BFFF
        )

        for shard, count in pulls.items():
            chance, guaranteed_at, remaining = self.mercy.get_display_info(shard, count)

            embed.add_field(
                name=shard.replace("_", " ").title(),
                value=(
                    f"Pulled: **{count}**\n"
                    f"Chance: **{chance:.1f}%**\n"
                    f"Guaranteed at: **{guaranteed_at}** "
                    f"({remaining} remaining)"
                ),
                inline=False
            )

        await ctx.send(embed=embed)

    # -------------------------
    # ADD
    # -------------------------
    async def add(self, ctx, user_id, amount, shard_type):
        if shard_type is None:
            await ctx.send("❌ Missing shard type.")
            return

        shard_type = shard_type.lower()

        if shard_type not in VALID_SHARDS:
            await ctx.send(f"❌ Invalid shard. Valid: {', '.join(VALID_SHARDS)}")
            return

        try:
            amount = int(amount)
        except:
            await ctx.send("❌ Amount must be a number.")
            return

        # primal = add on both
        if shard_type == "primal":
            out = []
            for s in ["primal_legendary", "primal_mythical"]:
                new = self.mercy.add_pulls(user_id, s, amount)
                chance, g_at, rem = self.mercy.get_display_info(s, new)
                out.append(f"→ **{s.replace('_',' ').title()}**: {new} pulls, {chance:.1f}%, G@{g_at}")
            return await ctx.send("\n".join(out))

        # non primal
        new = self.mercy.add_pulls(user_id, shard_type, amount)
        chance, g_at, rem = self.mercy.get_display_info(shard_type, new)

        await ctx.send(
            f"✅ Added {amount} to **{shard_type}**\n"
            f"Now: {new} pulls → {chance:.1f}% (Guaranteed at {g_at}, {rem} remaining)"
        )

    # -------------------------
    # RESET
    # -------------------------
    async def reset(self, ctx, user_id, shard_type, subtype):
        if shard_type is None:
            return await ctx.send("❌ Missing shard type.")

        shard_type = shard_type.lower()

        if shard_type == "primal":
            # reset both
            if subtype is None:
                for s in ["primal_legendary", "primal_mythical"]:
                    self.mercy.reset_pulls(user_id, s)
                return await ctx.send("🧾 Primal Legendary + Mythical reset.")

            subtype = subtype.lower()
            if subtype == "legendary":
                self.mercy.reset_pulls(user_id, "primal_legendary")
                return await ctx.send("🧾 Primal Legendary reset.")
            if subtype == "mythical":
                self.mercy.reset_pulls(user_id, "primal_mythical")
                return await ctx.send("🧾 Primal Mythical reset.")

            return await ctx.send("❌ Invalid subtype (use legendary/mythical).")

        # non primal
        if shard_type not in VALID_SHARDS:
            return await ctx.send(f"❌ Invalid shard.")

        self.mercy.reset_pulls(user_id, shard_type)
        await ctx.send(f"🧾 Mercy reset for **{shard_type}**.")
