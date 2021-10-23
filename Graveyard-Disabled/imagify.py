import os

import discord
from discord.ext import commands


class Imagify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session


def setup(bot):
    bot.add_cog(Imagify(bot))
