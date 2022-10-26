import discord


class AppPlugin:
    def __init__(self) -> None:
        pass

    def apphandler(self, bot: discord.Bot): pass


class BotController:
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    def use(self, plugin: AppPlugin):
        plugin.apphandler(self.bot)
