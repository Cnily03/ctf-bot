import discord

from app import AppPlugin


class CmdProcessor(AppPlugin):
    def register(self, bot: discord.Bot): pass


class CmdProcessor(AppPlugin):
    def __init__(self, args: list[CmdProcessor] = []) -> None:
        self.cmd_args = args

    def use(self, processor: CmdProcessor):
        processor.register(bot=self.bot)

    def useArgs(self, args: list[CmdProcessor]):
        for cmd in args:
            self.use(cmd)

    def register(self, bot: discord.Bot): pass

    def apphandler(self, bot: discord.Bot):
        self.bot = bot
        self.useArgs(self.cmd_args)
