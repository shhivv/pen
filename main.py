#type: ignore

import discord
from discord.ext import commands
from dotenv import load_dotenv

from os import environ

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

ready = False

@bot.event
async def on_ready():
    print(f'Logged in')
    await bot.load_extension('cogs.web_crawler') #TODO: bad code



bot.run(environ.get("BOT_TOKEN"))
