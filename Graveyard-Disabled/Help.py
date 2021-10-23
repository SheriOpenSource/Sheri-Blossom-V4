from random import choice

import discord
from discord.ext import commands as dcommands

from main import sheri_colors


class MyHelpCommand(dcommands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            em = discord.Embed(description=page, color=choice(sheri_colors))
            em.set_author(name="Here is the help you requested!")
            await destination.send(embed=em)

    def get_opening_note(self):
        return None

    def get_command_signature(self, command):
        return f"{self.clean_prefix}{command.qualified_name} {self.context.signature(command)}"

    def get_ending_note(self):
        command_name = self.context.invoked_with
        return (
            f"Type `{self.clean_prefix}{command_name} [command]` for more info on a command.\n"
            f"You can also type `{self.clean_prefix}{command_name} [category]` for more info on a category."
        )

    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            joined = ", ".join(c.name for c in commands) + "\n"
            self.paginator.add_line(f"__**{heading}**__")
            self.paginator.add_line(joined)

    def add_subcommand_formatting(self, command):
        fmt = (
            f"{self.clean_prefix}{command.qualified_name} - `{command.help}`"
            if command.description
            else f"{self.clean_prefix}{command.qualified_name}"
        )
        self.paginator.add_line(fmt)

    def add_aliases_formatting(self, aliases):
        self.paginator.add_line(self.aliases_heading + ", ".join(aliases), empty=True)

    def add_command_formatting(self, command):
        if command.description:
            self.paginator.add_line(command.help, empty=True)

        signature = self.get_command_signature(command)
        if command.aliases:
            self.paginator.add_line(signature)
            self.add_aliases_formatting(command.aliases)
        else:
            self.paginator.add_line(signature, empty=True)


class Help(dcommands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand(
            aliases_heading="**Aliases:** ", verify_checks=False
        )
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
