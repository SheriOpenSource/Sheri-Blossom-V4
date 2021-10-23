import io
from io import BytesIO

import aiohttp
import discord
from PIL import Image
from discord.ext import commands

from API.ExAPI import user_agent, base_urls
from Checks.bot_checks import check_nsfw


async def main_fetch(link):
    header = {
        "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=header) as resp:
            if resp.status == 200:
                bg = BytesIO(await resp.read())
                return bg
            else:
                return None


async def alex_fetch(link):
    async with aiohttp.ClientSession() as session:
        async with session.get(link, headers=user_agent) as resp:
            if resp.status == 200:
                bg = BytesIO(await resp.read())
                return bg
            else:
                return None


def render_image(bg):
    buffer = BytesIO()

    bg = Image.open(bg).convert("RGBA")
    x = bg.size[0]
    y = bg.size[1]
    bg.save(io.BytesIO(), format="PNG")
    im = Image.new("RGBA", (x, y), (0, 0, 0, 0))
    im.paste(bg, (0, 0), bg)
    im.save(buffer, format="png")
    buffer.seek(0)

    return buffer


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    async def make_text_meme(self, ctx, type, text):
        return
        em = discord.Embed(color=self.bot.color)
        link = f"https://memes.ourmainfra.me/api/{type}?text={text}"
        bg = await main_fetch(link)
        if not bg:
            return await ctx.send(
                    "Something went wrong in the backend when processing the command, Please contact support!")
            
        buffer = render_image(bg)

        em.set_author(name="Memes!")
        em.set_image(url=f"attachment://{type}.png")
        await ctx.send(file=discord.File(fp=buffer, filename=f"{type}.png"), embed=em)

    async def alex_make_text_meme(self, ctx, type, text):
        em = discord.Embed(color=self.bot.color)
        link = f"{base_urls['alexflipnote']}{type}?text={text}"
        bg = await alex_fetch(link)
        if not bg:
            return await ctx.send(
                    "Something went wrong in the backend when processing the command, Please contact support!")
        buffer = render_image(bg)

        em.set_author(name="Memes!")
        em.set_image(url=f"attachment://{type}.png")
        await ctx.send(file=discord.File(fp=buffer, filename=f"{type}.png"), embed=em)

    async def alex_make_text_meme_top_bottom(self, ctx, type, top, bottom):
        em = discord.Embed(color=self.bot.color)
        link = f"{base_urls['alexflipnote']}{type}?top={top}&?bottom={bottom}"
        bg = await alex_fetch(link)
        if not bg:
            return await ctx.send(
                    "Something went wrong in the backend when processing the command, Please contact support!")
        buffer = render_image(bg)

        em.set_author(name="Memes!")
        em.set_image(url=f"attachment://{type}.png")
        await ctx.send(file=discord.File(fp=buffer, filename=f"{type}.png"), embed=em)

    async def alex_filters(self, ctx, type):
        if ctx.author.avatar is None:
            return await ctx.send("You need an avatar to use this meme")
        em = discord.Embed(color=self.bot.color)

        link = f"{base_urls['alexflipnote']}/filter/{type}?image={ctx.author.avatar_url}"
        bg = await alex_fetch(link)
        if not bg:
            return await ctx.send(
                    "Something went wrong in the backend when processing the command, Please contact support!")
        buffer = render_image(bg)

        em.set_author(name="Memes!")
        em.set_image(url=f"attachment://{type}.png")
        await ctx.send(file=discord.File(fp=buffer, filename=f"{type}.png"), embed=em)

    async def alex_make_text_meme_text_text2(self, ctx, type, top, bottom):
        em = discord.Embed(color=self.bot.color)
        link = f"{base_urls['alexflipnote']}{type}?text={top}&?text2={bottom}"
        bg = await alex_fetch(link)
        if not bg:
            return await ctx.send(
                    "Something went wrong in the backend when processing the command, Please contact support!")
        buffer = render_image(bg)

        em.set_author(name="Memes!")
        em.set_image(url=f"attachment://{type}.png")
        await ctx.send(file=discord.File(fp=buffer, filename=f"{type}.png"), embed=em)

    async def make_user_meme(self, ctx, type, user):
        return
        if ctx.author.avatar is None:
            return await ctx.send("You need an avatar to use this meme")
        em = discord.Embed(color=self.bot.color)
        link = f"https://memes.ourmainfra.me/api/{type}?avatar1={user.avatar_url_as(format='png')}"
        bg = await main_fetch(link)
        if not bg:
            return await ctx.send(
                    "Something went wrong in the backend when processing the command, Please contact support!")
        buffer = render_image(bg)

        em.set_author(name="Memes!")
        em.set_image(url=f"attachment://{type}.png")
        await ctx.send(file=discord.File(fp=buffer, filename=f"{type}.png"), embed=em)

    @commands.command()
    async def magik(self, ctx, url: str = None):
        """Magikify an image"""
        if url is None:
            image = False
            async for message in ctx.channel.history(limit=5):
                if message.attachments:
                    file = message.attachments[0]
                    if file.url.lower().endswith(("png", "jpeg", "jpg", "gif", "webp")):
                        image = True
                        url = file.url
                if message.embeds:
                    file = message.embeds[0].image
                    if file.url:
                        image = True
                        url = file.url
            if not image:
                em = discord.Embed(color=self.bot.color)
                em.set_author(name="Error ❌")
                em.description = "No image found in the last 5 messages, please either upload an image or supply a URL!"
                await ctx.send(embed=em)
        else:
            if isinstance(ctx.channel, discord.DMChannel):
                em = discord.Embed(color=self.bot.color)
            else:
                em = discord.Embed(color=self.bot.color)
            try:
                async with self.bot.session.get(
                        "https://discord.services/api/magik/?url=" + url
                ) as resp:
                    if resp.status == 200:
                        try:
                            test = await resp.json()
                            if "some error sry :/" in test:
                                em = discord.Embed(color=self.bot.color)
                                em.set_author(name="Error ❌")
                                em.description = "Invalid URL!"
                                return await ctx.send(embed=em)
                        except aiohttp.ContentTypeError:
                            magik = await resp.read()
                            with open("magik.png", "wb") as f:
                                f.write(magik)
                                em.set_author(name="Magik!")
                            em.set_image(url="attachment://magik.png")
                            em.set_footer(text="Powered by discord.services")
                            await ctx.send(file=discord.File("magik.png"), embed=em)
                    else:
                        em = discord.Embed(color=self.bot.color)
                        em.set_author(name="Error ❌")
                        em.description = "Error is over at the API, nothing we can do :("
                        await ctx.send(embed=em)
            except aiohttp.ClientConnectorCertificateError:
                return 

    '''
    @commands.command()
    async def fedora(self, ctx, *, user: discord.Member = None):
        """Custom fedora meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "fedora", user)

    @commands.command()
    @commands.check(check_nsfw)
    async def brazzers(self, ctx, *, user: discord.Member = None):
        """Custom citation meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "brazzers", user)

    @commands.command()
    async def dab(self, ctx, *, user: discord.Member = None):
        """Custom dab meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "dab", user)

    @commands.command()
    async def jail(self, ctx, *, user: discord.Member = None):
        """Custom Jail meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "jail", user)

    @commands.command()
    async def laid(self, ctx, *, user: discord.Member = None):
        """Custom laid meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "laid", user)

    @commands.command()
    async def rip(self, ctx, *, user: discord.Member = None):
        """Custom RIP meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "rip", user)

    @commands.command()
    async def salty(self, ctx, *, user: discord.Member = None):
        """Custom Salty meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "salty", user)

    @commands.command()
    async def sickban(self, ctx, *, user: discord.Member = None):
        """Custom Sick ban meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "sickban", user)

    @commands.command()
    async def triggered(self, ctx, *, user: discord.Member = None):
        """Custom triggered meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "trigger", user)

    @commands.command()
    async def wanted(self, ctx, *, user: discord.Member = None):
        """Custom wanted meme"""
        if user is None:
            user = ctx.author
        await self.make_user_meme(ctx, "wanted", user)

    @commands.command()
    async def tweet(self, ctx, user: discord.Member, *, text: str):
        """Custom twitter meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        link = f"https://memes.ourmainfra.me/api/tweet?" + \
               f"avatar1={user.avatar_url_as(format='png')}?username1={user.name}?text={text}"
        buffer = BytesIO()
        bg = await main_fetch(link)
        buffer = render_image(bg)

        em.set_author(name="Memes!")
        em.set_image(url="attachment://salty.png")
        await ctx.send(file=discord.File(fp=buffer, filename="salty.png"), embed=em)

    @commands.command()
    async def armor(self, ctx, *, text: str):
        """Custom armor meme"""
        await self.make_text_meme(ctx, "armor", text)

    @commands.command()
    async def balloon(self, ctx, *, text: str):
        """Custom balloon meme"""
        await self.make_text_meme(ctx, "balloon", text)

    @commands.command()
    async def boo(self, ctx, *, text: str):
        """Custom boo meme"""
        await self.make_text_meme(ctx, "boo", text)

    @commands.command()
    async def brain(self, ctx, *, text: str):
        """Custom brain meme"""
        await self.make_text_meme(ctx, "brain", text)

    @commands.command()
    async def changemymind(self, ctx, *, text: str):
        """Custom change my mind meme"""
        await self.make_text_meme(ctx, "changemymind", text)

    @commands.command()
    async def citation(self, ctx, *, text: commands.clean_content):
        """Custom citation meme"""
        text = str(text)
        await self.make_text_meme(ctx, "citation", text)

    @commands.command()
    async def cry(self, ctx, *, text: str):
        """Custom cry meme"""
        await self.make_text_meme(ctx, "cry", text)

    @commands.command()
    async def excuseme(self, ctx, *, text: str):
        """Custom excuseme meme"""
        await self.make_text_meme(ctx, "excuseme", text)

    @commands.command()
    async def humansgood(self, ctx, *, text: str):
        """Custom humansgood meme"""
        await self.make_text_meme(ctx, "humansgood", text)

    @commands.command()
    async def knowyourlocation(self, ctx, *, text: str):
        """Custom knowyourlocation meme"""
        await self.make_text_meme(ctx, "knowyourlocation", text)

    @commands.command()
    async def master(self, ctx, *, text: str):
        """Custom master meme"""
        await self.make_text_meme(ctx, "master", text)

    @commands.command()
    async def note(self, ctx, *, text: str):
        """Custom note meme"""
        await self.make_text_meme(ctx, "note", text)

    @commands.command()
    async def ohno(self, ctx, *, text: str):
        """Custom ohno meme"""
        await self.make_text_meme(ctx, "ohno", text)

    @commands.command()
    async def plan(self, ctx, *, text: str):
        """Custom plan meme"""
        await self.make_text_meme(ctx, "plan", text)

    @commands.command()
    async def presentation(self, ctx, *, text: str):
        """Custom presentation meme"""
        await self.make_text_meme(ctx, "presentation", text)

    @commands.command()
    async def savehumanity(self, ctx, *, text: str):
        """Custom savehumanity meme"""
        await self.make_text_meme(ctx, "savehumanity", text)

    @commands.command()
    async def shit(self, ctx, *, text: str):
        """Custom shit meme"""
        await self.make_text_meme(ctx, "shit", text)

    @commands.command()
    async def slapsroof(self, ctx, *, text: str):
        """Custom slapsroof meme"""
        await self.make_text_meme(ctx, "slapsroof", text)

    @commands.command()
    async def stroke(self, ctx, *, text: str):
        """Custom stroke meme"""
        await self.make_text_meme(ctx, "stroke", text)

    @commands.command()
    async def surprised(self, ctx, *, text: str):
        """Custom surprised meme"""
        await self.make_text_meme(ctx, "surprised", text)

    @commands.command()
    async def thesearch(self, ctx, *, text: str):
        """Custom thesearch meme"""
        await self.make_text_meme(ctx, "thesearch", text)

    @commands.command()
    async def vr(self, ctx, *, text: str):
        """Custom vr meme"""
        await self.make_text_meme(ctx, "vr", text)

    @commands.command()
    async def walking(self, ctx, *, text: str):
        """Custom walking meme"""
        await self.make_text_meme(ctx, "walking", text)

    @commands.command()
    async def calling(self, ctx, *, text: str):
        """Custom Calling Meme"""
        await self.alex_make_text_meme(ctx, 'calling', text)

    @commands.command()
    async def captcha(self, ctx, *, text: str):
        """Custom Captcha Meme"""
        await self.alex_make_text_meme(ctx, 'captcha', text)

    @commands.command()
    async def challenge(self, ctx, *, text: str):
        """Custom Minecraft challenge"""
        await self.alex_make_text_meme(ctx, 'challenge', text)

    @commands.command()
    async def achievement(self, ctx, *, text: str):
        """Custom Minecraft achievement"""
        await self.alex_make_text_meme(ctx, 'achievement', text)

    @commands.command()
    async def scroll(self, ctx, *, text: str):
        """Custom scroll meme"""
        await self.alex_make_text_meme(ctx, 'scroll', text)

    @commands.command()
    async def facts(self, ctx, *, text: str):
        """Custom facts meme"""
        await self.alex_make_text_meme(ctx, 'facts', text)

    @commands.command()
    async def didyoumean(self, ctx, top_text: str, bottom_text: str):
        """Custom didyoumean meme"""
        await self.alex_make_text_meme_top_bottom(ctx, 'didyoumean', top_text, bottom_text)

    @commands.command()
    async def drake(self, ctx, top_text: str, bottom_text: str):
        """Custom didyoumean meme"""
        await self.alex_make_text_meme_top_bottom(ctx, 'drake', top_text, bottom_text)

    @commands.command()
    async def pornhub(self, ctx, text: str, text2: str):
        """Custom didyoumean meme"""
        await self.alex_make_text_meme_top_bottom(ctx, 'drake', text, text2)

    @commands.command()
    async def goblur(self, ctx):
        """Custom Avatar Alex Manipular"""

        await self.alex_filters(ctx, "blur")

    @commands.command()
    async def goinvert(self, ctx):
        """Custom Avatar Alex Manipular"""

        await self.alex_filters(ctx, "invert")

    @commands.command()
    async def gobw(self, ctx):
        """Custom Avatar Alex Manipular"""

        await self.alex_filters(ctx, "b&w")

    @commands.command()
    async def godeepfry(self, ctx):
        """Custom Avatar Alex Manipular"""

        await self.alex_filters(ctx, "deepfry")

    @commands.command()
    async def gopixel(self, ctx):
        """Custom Avatar Alex Manipular"""

        await self.alex_filters(ctx, "pixelate")

    @commands.command()
    async def gosnow(self, ctx):
        """Custom Avatar Alex Manipular"""

        await self.alex_filters(ctx, "snow")

    @commands.command()
    async def gogay(self, ctx):
        """Custom Avatar Alex Manipular"""

        await self.alex_filters(ctx, "gay")
    '''


def setup(bot):
    bot.add_cog(Memes(bot))
