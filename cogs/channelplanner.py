# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio

# -----------------------------
# CONFIGURATION (à modifier)
# -----------------------------
HYDRA_CHANNEL_ID = 123456789012345678  # <-- PLACEHOLDER
CHIMERA_CHANNEL_ID = 987654321098765432  # <-- PLACEHOLDER
THREAD_DURATION_DAYS = 7 
DAYS_BEFORE_CREATION = 2 
DAYS_AFTER_END_DELETE = 2 

# -----------------------------
# HELPER
# -----------------------------
def next_weekday(start_date: datetime, weekday: int):
    days_ahead = weekday - start_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)

def format_date_range(start_date: datetime, duration_days: int):
    end_date = start_date + timedelta(days=duration_days)
    return f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"

# -----------------------------
# COG
# -----------------------------
class ClashRotation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.rotation_loop.start()

    def cog_unload(self):
        self.rotation_loop.cancel()

    @tasks.loop(hours=1)
    async def rotation_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()

        # -----------------------------
        # Hydra Clash 
        # -----------------------------
        try:
            hydra_channel = self.bot.get_channel(HYDRA_CHANNEL_ID)
            if hydra_channel:
                next_hydra_start = next_weekday(now, 2)  
                thread_name = f"Hydra Clash {format_date_range(next_hydra_start, THREAD_DURATION_DAYS)}"
                creation_date = next_hydra_start - timedelta(days=DAYS_BEFORE_CREATION)
                deletion_date = next_hydra_start + timedelta(days=THREAD_DURATION_DAYS + DAYS_AFTER_END_DELETE)

                existing = discord.utils.get(hydra_channel.threads, name=thread_name)
                if creation_date <= now <= next_hydra_start + timedelta(days=THREAD_DURATION_DAYS):
                    if existing is None:
                        await hydra_channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)
                        print(f"[Hydra] Thread created : {thread_name}")

                if existing and now >= deletion_date:
                    await existing.delete()
                    print(f"[Hydra] Thread deleted : {thread_name}")

        except Exception as e:
            print(f"Error for Hydra Clash : {e}")

        # -----------------------------
        # Chimera Clash 
        # -----------------------------
        try:
            chimera_channel = self.bot.get_channel(CHIMERA_CHANNEL_ID)
            if chimera_channel:
                next_chimera_start = next_weekday(now, 3)  # 0=lundi, 3=jeudi
                thread_name = f"Chimera Clash {format_date_range(next_chimera_start, THREAD_DURATION_DAYS)}"
                creation_date = next_chimera_start - timedelta(days=DAYS_BEFORE_CREATION)
                deletion_date = next_chimera_start + timedelta(days=THREAD_DURATION_DAYS + DAYS_AFTER_END_DELETE)

                existing = discord.utils.get(chimera_channel.threads, name=thread_name)
                if creation_date <= now <= next_chimera_start + timedelta(days=THREAD_DURATION_DAYS):
                    if existing is None:
                        await chimera_channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)
                        print(f"[Chimera] Thread created : {thread_name}")

                if existing and now >= deletion_date:
                    await existing.delete()
                    print(f"[Chimera] Thread deleted : {thread_name}")

        except Exception as e:
            print(f"Error for Chimera Clash : {e}")

# -----------------------------
# SETUP
# -----------------------------
async def setup(bot):
    await bot.add_cog(ClashRotation(bot))
