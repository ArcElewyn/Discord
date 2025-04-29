import discord
from discord.ext import commands
import pandas as pd

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Replace this with your authorized channel ID
AUTHORIZED_CHANNEL_ID =   # TODO: input channel ID here

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

def read_google_sheet(url):
    file_id = url.split("/d/")[1].split("/")[0]
    csv_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"  
    df = pd.read_csv(csv_url)
    return df

@bot.command()
async def siege(ctx):
    # If not in the authorized channel, silently ignore the command
    if ctx.channel.id != AUTHORIZED_CHANNEL_ID:
        return

    try:
        df = read_google_sheet("") # TODO: set public sheet url

        user_pseudo = ctx.author.name.lower()
        first_column = df.columns[0]

        matching_row = df[df[first_column].str.lower() == user_pseudo]

        if matching_row.empty:
            await ctx.send("No data found for your username.")
        else:
            info = matching_row.iloc[0].to_dict()
            response = "\n".join([f"**{col}**: {val}" for col, val in info.items() if col != first_column])
            await ctx.send(f"Data for **{ctx.author.name}**:\n{response}")

    except Exception as e:
        await ctx.send(f"Error: {e}")
