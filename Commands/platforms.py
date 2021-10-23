import discord
from discord.ext import commands

from API.ExAPI import External_Retrieval
from Functions.core import embed_color, send_message


class Platforms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='steam')
    async def steam(self, ctx, user: str):
        request = await External_Retrieval.alexflipnote_api(self.bot, f"steam/user/{user}")
        embed = discord.Embed(color=embed_color(),
                              title=request['profile', 'username'])
        await send_message(ctx, embed=embed)


def setup(bot):
    bot.add_cog(Platforms(bot))
