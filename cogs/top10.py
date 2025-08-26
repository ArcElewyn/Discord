# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from utils.leaderboard_handler import show_leaderboard
from utils.helpers import normalize_difficulty
from config import BOSS_CONFIG

class Top10(commands.Cog):
    """Cog regroupant toutes les commandes de leaderboard globales et par clan"""

    def __init__(self, bot):
        self.bot = bot

    # --- Commandes globales ---
    @commands.command()
    async def top10hydra(self, ctx, difficulty: str = None):
        if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['hydra']['difficulties']:
            await show_leaderboard(ctx, 'hydra', difficulty)
        else:
            difficulties = " | ".join(BOSS_CONFIG['hydra']['difficulties'])
            await ctx.send(f"❌ Please specify difficulty: `!top10hydra <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare")

    @commands.command()
    async def top10chimera(self, ctx, difficulty: str = None):
        if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG['chimera']['difficulties']:
            await show_leaderboard(ctx, 'chimera', difficulty)
        else:
            difficulties = " | ".join(BOSS_CONFIG['chimera']['difficulties'])
            await ctx.send(f"❌ Please specify difficulty: `!top10chimera <difficulty>`\n**Available:** {difficulties}\n**Shortcuts:** `nm` = Nightmare, `unm` = Ultra")

    @commands.command()
    async def top10cvc(self, ctx):
        await show_leaderboard(ctx, 'cvc')

    # --- Commandes par clan RTF ---
    @commands.command()
    async def rtfhydra(self, ctx, difficulty: str = None):
        await self._show_clan_leaderboard(ctx, 'hydra', difficulty, 'RTF')

    @commands.command()
    async def rtfchimera(self, ctx, difficulty: str = None):
        await self._show_clan_leaderboard(ctx, 'chimera', difficulty, 'RTF')

    @commands.command()
    async def rtfcvc(self, ctx):
        await show_leaderboard(ctx, 'cvc', clan='RTF')

    # --- Commandes par clan RTFC ---
    @commands.command()
    async def rtfchydra(self, ctx, difficulty: str = None):
        await self._show_clan_leaderboard(ctx, 'hydra', difficulty, 'RTFC')

    @commands.command()
    async def rtfcchimera(self, ctx, difficulty: str = None):
        await self._show_clan_leaderboard(ctx, 'chimera', difficulty, 'RTFC')

    @commands.command()
    async def rtfccvc(self, ctx):
        await show_leaderboard(ctx, 'cvc', clan='RTFC')

    # --- Commandes par clan RTFR ---
    @commands.command()
    async def rtfrhydra(self, ctx, difficulty: str = None):
        await self._show_clan_leaderboard(ctx, 'hydra', difficulty, 'RTFR')

    @commands.command()
    async def rtfrchimera(self, ctx, difficulty: str = None):
        await self._show_clan_leaderboard(ctx, 'chimera', difficulty, 'RTFR')

    @commands.command()
    async def rtfrcvc(self, ctx):
        await show_leaderboard(ctx, 'cvc', clan='RTFR')

    # --- Méthode interne pour éviter la répétition ---
    async def _show_clan_leaderboard(self, ctx, boss_type, difficulty, clan):
        """Affiche le leaderboard pour un boss et un clan spécifique"""
        if difficulty and normalize_difficulty(difficulty) in BOSS_CONFIG[boss_type]['difficulties']:
            await show_leaderboard(ctx, boss_type, difficulty, clan)
        elif boss_type != 'cvc':  # CvC n’a pas de difficultés
            difficulties = " | ".join(BOSS_CONFIG[boss_type]['difficulties'])
            await ctx.send(
                f"❌ Please specify difficulty: `!{ctx.command.name} <difficulty>`\n"
                f"**Available:** {difficulties}\n"
                f"**Shortcuts:** `nm` = Nightmare, `unm` = Ultra"
            )
        else:
            await show_leaderboard(ctx, boss_type, clan=clan)

async def setup(bot):
    await bot.add_cog(Top10(bot))
