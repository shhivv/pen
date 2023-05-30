#type: ignore

import discord
from discord.ext import commands
from dotenv import load_dotenv

import aiohttp
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

    # Create a shared aiohttp ClientSession for making requests
    bot.session = aiohttp.ClientSession()

    

@bot.event
async def on_disconnect():
    # Close the shared aiohttp ClientSession when the bot disconnects
    await bot.session.close()

# Load the web crawler cog
bot.load_extension('cogs.web_crawler')

bot.run(environ.get("BOT_TOKEN"))
