from discord.client import Client
from logger import logger, Extra

_login = Client.login
_connect = Client.connect
_close = Client.close


async def login(self, token: str) -> None:
    logger.debug("[green]Bot is logging to the server", extra=Extra.PURE_MARK)
    await _login(self, token)
    logger.info("Bot successfully logged in")


async def connect(self, *, reconnect: bool = True) -> None:
    logger.info("[green]Bot is running on the server[/]", extra=Extra.PURE_MARK)
    await _connect(self, reconnect=reconnect)


async def close(self) -> None:
    logger.info("Disconnecting")
    await _close(self)

Client.login = login
Client.connect = connect
Client.close = close
