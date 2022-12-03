import re
import discord
from discord.commands import ApplicationContext
from discord import option
from commands.core.CmdHelper import CmdHelper, log_command, Area, template


class asciify(CmdHelper):

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
        @log_command
        async def asciify(ctx: ApplicationContext, mode, string):
            res = ""
            if mode == "all":
                for char in string:
                    res += '\\x' + '{:02X}'.format(ord(char)).upper()
            elif mode == "quote":
                on_quote = False
                quote_char = ""
                jump = False
                for i in range(len(string)):
                    if jump:
                        jump = False
                        continue
                    char = string[i]
                    on_set = False
                    if on_quote and char == quote_char:  # end
                        on_quote = False
                    elif (not on_quote) and (char == "'" or char == '"'):  # start
                        on_quote = True
                        on_set = True
                        quote_char = char
                    if (not on_set) and on_quote:  # modify
                        if char == "\\" and (string[i+1] == "'" or string[i+1] == '"'):  # \" \'
                            res += '\\x' + '{:02X}'.format(ord(string[i+1])).upper()
                            jump = True
                        elif char == "\\":
                            res += '\\x' + '{:02X}'.format(ord(eval("'\\"+string[i+1]+"'"))).upper()
                            jump = True
                        else:  # normal
                            res += '\\x' + '{:02X}'.format(ord(char)).upper()
                    else:
                        res += char

            await ctx.respond(template(
                method="Asciify Encode",
                area=Area.CRYPTO,
                input=string,
                result=res
            ))

        @bot.slash_command(
            name="unasciify",
            description="unasciify string"
        )
        @option("string", str, description="string to be unasciified")
        @log_command
        async def unasciify(ctx: ApplicationContext, string):
            res = ""
            str_list = re.split(r"(\\x[0-9a-fA-F]{2})", string)
            for i in range(len(str_list)):
                if re.search(r"(\\x[0-9a-fA-F]{2})", str_list[i]):
                    str_list[i] = eval("'"+str_list[i]+"'")
            res = "".join(str_list)
            await ctx.respond(template(
                method="Asciify Decode",
                area=Area.CRYPTO,
                input=string,
                result=res
            ))
