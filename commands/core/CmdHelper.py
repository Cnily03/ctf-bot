import discord

from app import AppPlugin


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
