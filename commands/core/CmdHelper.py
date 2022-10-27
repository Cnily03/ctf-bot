import discord
from discord.commands import ApplicationContext
from app import AppPlugin
from functools import wraps
from logger import logger, Extra


def log_command(func):
    """Use this decorator to enable command logging"""
    @wraps(func)
    async def wrapper(*args, **kwds):
        """Mixin codes about logging to the command processor function"""
        # wrapper.__annotations__ = func.__annotations__
        ctx: ApplicationContext = args[0]
        params = kwds.items()
        log_params = [ctx.command.name]
        for k, v in params:
            log_params.append(f"[bold]{k}[/]:{v}")
        COMMAND = "/"+" ".join(log_params)
        logger.info("".join([
            "Receiving command from group ",
            f"[cadet_blue]{ctx.guild.name} ({ctx.guild.id})[/] ",
            f"by user [cadet_blue]{ctx.author.name}#{ctx.author.discriminator}[/]\n",
            f"[magenta]{COMMAND}[/]"]), extra=Extra.PURE_MARK)
        return await func(*args, **kwds)
    return wrapper


class CmdHelper(AppPlugin):
    def register(self, bot: discord.Bot): pass


class CmdHelper(AppPlugin):
    def __init__(self, args: list[CmdHelper] = []) -> None:
        self.cmd_args = args

    def use(self, processor: CmdHelper):
        processor.register(bot=self.bot)

    def useArgs(self, args: list[CmdHelper]):
        for cmd in args:
            self.use(cmd)

    def register(self, bot: discord.Bot): pass

    def apphandler(self, bot: discord.Bot):
        self.bot = bot
        self.useArgs(self.cmd_args)
