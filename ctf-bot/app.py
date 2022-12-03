import discord


class AppPlugin:
    """Create a plugin"""

    def __init__(self) -> None: pass

    def apphandler(self, bot: discord.Bot):
        """
        The universal API for a plugin using `AppPlugin`.The arg `bot` in type
        `discord.Bot` would be delivered by `BotController` so that plugin
        could use bot instance.
        """
        pass


class BotController:
    """Create a controller to manage bot and plugins more easily"""

    def __init__(self, bot: discord.Bot):
        """
        Initialize the controller by delivering the bot instance.

        Example as below
        ```python
        bot = discord.Bot()
        app = BotController(bot)
        ```
        """
        self.bot = bot

    def use(self, app: AppPlugin):
        """Use an app (mostly like plugins) which contains method `apphandler`"""
        app.apphandler(self.bot)
