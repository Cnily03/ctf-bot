import imp
import discord
from discord import option

from commands.core.CmdProcessor import CmdProcessor


class asciify(CmdProcessor):

    def register(bot: discord.Bot):

        @bot.slash_command(
            name="asciify",
            description="asciify string"
        )
        @option(
            "mode", str,
            description="mode of charactor asciifying",
            choices=["all", "quote"]
        )
        @option("string", str, description="string to be asciified")
        async def asciify(ctx, mode, string):
            res = ""
            if mode == "all":
                for i in string:
                    res += '\\x' + '{:02X}'.format(ord(i)).upper()
            elif mode == "quote":
                on_quote = False
                quote_char = ""
                for i in string:
                    on_set = False
                    if on_quote and i == quote_char:
                        on_quote = False
                    elif (not on_quote) and (i == "'" or i == '"'):
                        on_quote = True
                        on_set = True
                        quote_char = i
                    if (not on_set) and on_quote:
                        res += '\\x' + '{:02X}'.format(ord(i)).upper()
                    else:
                        res += i

            await ctx.respond("\n".join([
                f"**Following shows the asciified string of **`{string}`"
                f"```\n{res}\n```"])
            )
