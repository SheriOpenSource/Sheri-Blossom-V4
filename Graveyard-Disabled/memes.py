import aiohttp
import discord
import skvideo.io
from io import BytesIO
from discord.ext import commands


class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    async def make_text_meme(self, ctx, type, text):
        em = discord.Embed(color=self.bot.color)
        buffer = BytesIO()
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/{type}?text={text}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                with open(f"{type}.png", "wb") as f:
                    #buffer.read(f)
                    abandon = await resp.read()
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url=f"attachment://{type}.png")
                await ctx.send(file=discord.File(f"{type}.png"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

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

    @commands.command()
    async def citation(self, ctx, *, text: str):
        """Custom citation meme"""
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/citation?text={text}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("citation.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://citation.png")
                await ctx.send(file=discord.File("citation.png"), embed=em)

    @commands.command()
    async def brazzers(self, ctx, *, user: discord.Member = None):
        """Custom citation meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/brazzers?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("brazzers.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://brazzers.png")
                await ctx.send(file=discord.File("brazzers.png"), embed=em)

    @commands.command()
    async def dab(self, ctx, *, user: discord.Member = None):
        """Custom dab meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/dab?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("dab.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://dab.png")
                await ctx.send(file=discord.File("dab.png"), embed=em)

    @commands.command()
    async def fedora(self, ctx, *, user: discord.Member = None):
        """Custom fedora meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/fedora?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("fedora.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://fedora.png")
                await ctx.send(file=discord.File("fedora.png"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

    @commands.command()
    async def jail(self, ctx, *, user: discord.Member = None):
        """Custom Jail meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/jail?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("jailed.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://jailed.png")
                await ctx.send(file=discord.File("jailed.png"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

    @commands.command()
    async def laid(self, ctx, *, user: discord.Member = None):
        """Custom laid meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/laid?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("brazzers.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://brazzers.png")
                await ctx.send(file=discord.File("brazzers.png"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

    @commands.command()
    async def rip(self, ctx, *, user: discord.Member = None):
        """Custom Jail meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/rip?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("rip.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://rip.png")
                await ctx.send(file=discord.File("rip.png"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

    @commands.command()
    async def salty(self, ctx, *, user: discord.Member = None):
        """Custom Jail meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/salty?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("salty.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://salty.png")
                await ctx.send(file=discord.File("salty.png"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

    @commands.command()
    async def sickban(self, ctx, *, user: discord.Member = None):
        """Custom Jail meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/sickban?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("brazzers.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://brazzers.png")
                await ctx.send(file=discord.File("brazzers.png"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

    @commands.command()
    async def triggered(self, ctx, *, user: discord.Member = None):
        """Custom triggered meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/trigger?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("triggered.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://triggered.png")
                await ctx.send(file=discord.File("triggered.png"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

    @commands.command()
    async def crab(self, ctx, *, text: str):
        """Custom crab vid"""
        buffer = BytesIO()
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/crab?text={text}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()

                with open("crab.mp4", "wb") as f:
                    f.write(resp.buffer)
                em.set_author(name="Memes!")
                em.set_image(url="attachment://crab.mp4")
                await ctx.send(file=discord.File("crab.mp4"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

    @commands.command()
    async def wanted(self, ctx, *, user: discord.Member = None):
        """Custom warp meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/wanted?avatar1={user.avatar_url_as(format='png')}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("warp.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://warp.png")
                await ctx.send(file=discord.File("warp.png"), embed=em)
            if resp.status == 500:
                return await ctx.send("Something went wrong in the backend when processing the command, Please contact support!")

    @commands.command()
    async def tweet(self, ctx, user: discord.Member, *, text: str):
        """Custom twitter meme"""
        if user is None:
            user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://memes.ourmainfra.me/api/tweet?"
                f"avatar1={user.avatar_url_as(format='png')}?username1={user.name}?text={text}",
                headers={
                    "Authorization": "52ee8800dd89f917b13a4764da416c951867fa467bfc16cdd231ef02523df16f"
                },
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("tweet.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Memes!")
                em.set_image(url="attachment://tweet.png")
                await ctx.send(file=discord.File("tweet.png"), embed=em)

            if resp.status == 500:
                            return await ctx.send(
                                "Something went wrong in the backend when processing the command, Please contact support!")

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
    async def citation(self, ctx, *, text: str):
        """Custom citation meme"""
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


def setup(bot):
    bot.add_cog(Memes(bot))
