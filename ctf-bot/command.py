from commands.core.CmdHelper import CmdHelper
from commands.about import about
from commands.crypto.asciify import asciify


register_args = [
    about,
    asciify
]
cmd_register = CmdHelper(register_args)
