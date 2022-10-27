import asyncio
import os
from time import sleep
from app import BotController
from logger import logger, Extra
import yaml
import mixin.pycord.client
import discord
from commands.core.CmdHelper import CmdHelper
from commands.asciify import asciify
# import interactions

# Token
logger.debug("Loading discord token from [yellow]token[/]", extra=Extra.MARK_UP)
if os.path.exists("token"):
    TOKEN = open("token", "r", encoding="utf-8").read().strip()
else:
    logger.error(
        "No token file found. Please create 'token' with your discord bot token at the root dir of the project.")
    exit()

# Config
logger.debug("Loading configure from [yellow]config.yml[/]", extra=Extra.MARK_UP)
with open("config.yml", 'r', encoding="utf-8") as file:
    CONFIG = yaml.load(file, Loader=yaml.FullLoader)

# - Proxy
if CONFIG["Proxy"]["enable"]:
    bot = discord.Bot(proxy=CONFIG["Proxy"]["proxy"])
    logger.debug(f"Use config [bold magenta]{'Proxy'}[/]:[magenta]{CONFIG['Proxy']['proxy']}[/]",
                 extra=Extra.PURE_MARK)
else:
    bot = discord.Bot()

# Set bot plugin
app = BotController(bot)

# Set commands
register_args = [
    asciify
]
app.use(CmdHelper(register_args))


# login
bot.run(TOKEN)
