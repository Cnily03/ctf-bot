import discord
from discord.commands import ApplicationContext
from discord import option
from commands.core.CmdHelper import CmdHelper, log_command


class about(CmdHelper):

    def register(bot: discord.Bot):

        @bot.slash_command(
            name="about",
            description="Show about info"
        )
        async def about(ctx: ApplicationContext):
            res = "\n".join([
                "**About**",
                "",
                "A discord bot for CTF crafting offering many useful utilities with wonderful functions.",
                "",
                "Use this link to invite CTF Helper to your server: https://discord.cnily.me/invite/bot/ctf-bot",
                "",
                "Github: https://github.com/Cnily03/ctf-bot"
            ])
            # TODO: Complete the About Info (I am too lazy lol)
            if ctx.guild == None:
                await ctx.respond(res)
            else:
                await ctx.author.send(res)
                await ctx.respond("About Info has been sent to your DMs!")
