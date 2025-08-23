import discord
from discord.ext import commands
from utils.DatabaseManager_class import DatabaseManager
from config import AUTHORIZED_CHANNEL_ID
from datetime import datetime

# Règles de mercy
MERCY_RULES = {
    "ancient": {"threshold": 200, "increment": 0.5, "base": 0},
    "void": {"threshold": 200, "increment": 0.5, "base": 0},
    "sacred": {"threshold": 12, "increment": 2, "base": 0},
    "primal_legendary": {"threshold": 75, "increment": 1, "base": 0},
    "primal_mythical": {"threshold": 200, "increment": 10, "base": 0},
    "remnant": {"threshold": 24, "increment": 1, "base": 0},
}

db_manager = DatabaseManager()

class Mercy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Création de la table si elle n’existe pas
        db_manager.execute("""
            CREATE TABLE IF NOT EXISTS mercy_counters (
                user_id TEXT,
                shard_type TEXT,
                pulls INTEGER DEFAULT 0,
                last_reset TIMESTAMP,
                PRIMARY KEY(user_id, shard_type)
            )
        """)

    def get_mercy_chance(self, shard_type, pulls):
        rule = MERCY_RULES[shard_type]
        if pulls <= rule["threshold"]:
            return rule["base"]
        return rule["base"] + (pulls - rule["threshold"]) * rule["increment"]

    @commands.command(name="mercy")
    async def mercy(self, ctx, action: str = None, arg1: str = None, arg2: str = None):
        """Gestion de la mercy : !mercy add <nb> <type>, !mercy reset <type>, !mercy show"""
        if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
            return

        user_id = str(ctx.author.id)

        # ----- SHOW -----
        if action == "show":
            rows = db_manager.fetchall("SELECT shard_type, pulls FROM mercy_counters WHERE user_id = ?", (user_id,))
            if not rows:
                await ctx.send("❌ You don't have any mercy data yet.")
                return

            embed = discord.Embed(
                title=f"🎲 Mercy Status for {ctx.author.display_name}",
                color=0x00bfff
            )

            for shard_type, pulls in rows:
                chance = self.get_mercy_chance(shard_type, pulls)
                embed.add_field(
                    name=shard_type.replace("_", " ").title(),
                    value=f"**{pulls} pulls** → {chance:.1f}% chance",
                    inline=False
                )

            await ctx.send(embed=embed)

        # ----- ADD -----
        elif action == "add" and arg1 and arg2:
            try:
                pulls = int(arg1)
            except ValueError:
                await ctx.send("❌ Number of pulls must be an integer.")
                return

            shard_type = arg2.lower()
            if shard_type not in MERCY_RULES:
                await ctx.send(f"❌ Invalid shard type. Available: {', '.join(MERCY_RULES.keys())}")
                return

            # Update DB
            current = db_manager.fetchone(
                "SELECT pulls FROM mercy_counters WHERE user_id = ? AND shard_type = ?",
                (user_id, shard_type)
            )
            if current:
                new_value = current["pulls"] + pulls
                db_manager.execute(
                    "UPDATE mercy_counters SET pulls = ?, last_reset = ? WHERE user_id = ? AND shard_type = ?",
                    (new_value, datetime.utcnow(), user_id, shard_type)
                )
            else:
                db_manager.execute(
                    "INSERT INTO mercy_counters (user_id, shard_type, pulls, last_reset) VALUES (?, ?, ?, ?)",
                    (user_id, shard_type, pulls, datetime.utcnow())
                )

            await ctx.send(f"✅ Added {pulls} pulls to **{shard_type}** mercy.")

        # ----- RESET -----
        elif action == "reset" and arg1:
            shard_type = arg1.lower()
            if shard_type not in MERCY_RULES:
                await ctx.send(f"❌ Invalid shard type. Available: {', '.join(MERCY_RULES.keys())}")
                return

            db_manager.execute(
                "UPDATE mercy_counters SET pulls = 0, last_reset = ? WHERE user_id = ? AND shard_type = ?",
                (datetime.utcnow(), user_id, shard_type)
            )
            await ctx.send(f"🔄 Mercy for **{shard_type}** has been reset.")

        else:
            await ctx.send("❌ Usage: `!mercy add <nb> <type>`, `!mercy reset <type>`, `!mercy show`")

def setup(bot):
    bot.add_cog(Mercy(bot))
