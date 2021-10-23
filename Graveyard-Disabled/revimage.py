import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands


class Revimage(commands.Cog):
    """Reverse image search commands"""

    def __init__(self, bot):
        self.bot = bot
        self.tineye_session = aiohttp.ClientSession()

    def __unload(self):
        self.tineye_session.close()

    def _tag_to_title(self, tag):
        return tag.replace(' ', ', ').replace('_', ' ').title()

    @commands.command()
    async def tineye(self, ctx, link=None):
        """
        Reverse image search using tineye
        usage:  .tineye <image-link> or
                .tineye on image upload comment
        """
        file = ctx.message.attachments
        embed = discord.Embed(title='Reverse Image Details', color=16776960)
        if (link is None) and (not file):
            await ctx.send("Message didn't contain Image")
        else:
            async with ctx.channel.typing():
                if file:
                    url = file[0]['proxy_url']
                else:
                    url = link
                    await ctx.message.delete()
            response = await (await self.bot.session.get(f'https://tineye.com/search/?url={url}')).text()
            soup = BeautifulSoup(response, 'lxml')
            pages = []
            image_link = None
            try:
                match = soup.findAll('span', attrs={'class': 'search-details'})
                hidden = soup.find(class_='search-details').select('.hidden-xs')[0]
                if hidden.contents[0].startswith('Page:'):
                    pages.append('<{}>'.format(hidden.next_sibling['href']))
                else:
                    image_link = hidden.a['href']
            except AttributeError or IndexError:
                embed.add_field(name='Original Link', value='<{}>'.format(url), inline=False)
                #                embed.add_field(name='Matches', value='**No Matches Found**', inline=False)
                embed.add_field(name='Full Search', value='https://tineye.com/search/?url={}'.format(url),
                                inline=False)
            if image_link is not None:
                embed.add_field(name='Original Link', value='<{}>'.format(url), inline=False)
                #                embed.add_field(name='Matches', value='<{}>'.format(image_link), inline=False)
                embed.add_field(name='Full Search', value='https://tineye.com/search/?url={}'.format(url), inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Revimage(bot))
