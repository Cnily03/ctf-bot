import asyncio
import os
from app import BotController
from logger import logger
import yaml
import discord
from commands.core.CmdHelper import CmdHelper
from commands.asciify import asciify
# import interactions

# config
logger.debug("Loading configure from config.yml")
with open("config.yml", 'r', encoding="utf-8") as file:
    CONFIG = yaml.load(file, Loader=yaml.FullLoader)

# token
logger.debug("Loading discord token from token")
if os.path.exists("token"):
    TOKEN = open("token", "r", encoding="utf-8").read().strip()
else:
    logger.error("No token file found. Please create 'token' with your discord bot token at the root dir of the project.")
    exit()

# set config
# - proxy
if CONFIG["Proxy"]["enable"]:
    bot = discord.Bot(proxy=CONFIG["Proxy"]["proxy"])
else:
    bot = discord.Bot()

# set bot plugin
app = BotController(bot)

register_args = [
    asciify
]
app.use(CmdHelper(register_args))


# login
async def setup():
    logger.debug("Bot is logging to the server")
    await bot.login(TOKEN)
    logger.info("Bot successfully logged in!")
    await bot.connect(reconnect=True)

asyncio.run(setup())
