import asyncio
import os
from datetime import datetime
import aiohttp

import discord
from discord.ext import commands
from Checks.bot_checks import check_nsfw
from API.ExAPI import External_Retrieval as ExGet
from Checks.bot_checks import can_embed, can_send
from Formats.formats import pagify, avatar_check
from Functions.randomization import advchoice
from Lines.copypastas import get as pastas
from Lines.misc_functions import get as Get
from Lines.names import Names
from Functions.core import send_message


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    @commands.command()
    async def tdance(self, ctx, *, text: str):
        """Converts text/sentence to dancing emojis"""
        t = ""
        try:
            for l in text.lower():
                for letter, emote in Get["dance letters"].items():
                    if l.lower() == letter:
                        t += l.lower().replace(letter, emote)
            await ctx.send(t)

        except discord.Forbidden:
            await ctx.send("Error")

        except discord.HTTPException:
            await ctx.send(f"Cannot Dancify **{text}**")

    @commands.command()
    async def binary(self, ctx, *, text: str):
        """Convert text to binary"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        embed = discord.Embed(
            color=self.bot.color,
            description=" ".join(format(ord(x), "b") for x in text),
        )

        embed.set_author(
            name=ctx.message.author.name + " says",
            icon_url=avatar_check(ctx.message.author),
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def unbinary(self, ctx, *, text: str):
        """Convert binary to text"""
        embed = discord.Embed(color=self.bot.color, title="Binary >,<")
        embed.set_author(
            name=self.bot.user.name + " Decrypting",
            icon_url=avatar_check(self.bot.user),
        )

        embed.add_field(name="Input", value=text, inline=False)
        embed.add_field(
            name="Output",
            value="".join(chr(int(i, 2)) for i in text.split())
                .replace("@everyone", "everyone")
                .replace("@here", "here"),
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def pressf(self, ctx, msg: discord.Message = None):
        author = ctx.author
        respecters = []
        if msg is None:
            desc = f"{author.mention} has offered to pay respects."
        else:
            desc = f"{author.mention} has offered to pay respects on `{msg.content}` by `{msg.author.display_name}`."
        embed = discord.Embed(
            description=desc,
            timestamp=datetime.utcnow(),
            color=discord.Color(0xe62169)
        )

        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        embed.set_footer(text='React to this message to pay respects!')
        sent = await ctx.send(embed=embed)
        await sent.add_reaction('🇫')

        while True:
            def check(r, u):
                return str(r.emoji) == '🇫' and r.message.channel == ctx.channel and not u.bot

            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)

                if user not in respecters:
                    respecters.append(user)
                    await ctx.send(f"***{user.display_name}** has paid respects..*", delete_after=7)
            except asyncio.TimeoutError:
                new_embed = embed.copy()

                if len(respecters) != 1:
                    text = f"{len(respecters)} people have paid respects"
                else:
                    text = f"1 person has paid respect"

                new_embed.set_footer(text="{}.".format(text))

                if msg is None:
                    await ctx.send(f"{text} to **{author.display_name}**.")
                else:
                    await ctx.send(f"{text} to **{msg.author.display_name}**.")
                try:
                    await sent.edit(embed=new_embed)
                except discord.NotFound:
                    pass

                break
            else:
                continue

    # @commands.cooldown(1, 35, type=commands.BucketType.user)
    # @commands.command(pass_context=True)
    # async def flip(self, ctx, user: discord.Member = None):
    #    """Flips names
    #    """
    #    if not user:
    #        user = ctx.author
    #    char = "abcdefghijklmnopqrstuvwxyz"
    #    tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
    #    table = str.maketrans(char, tran)
    #    name = user.display_name.translate(table)
    #    char = char.upper()
    #    tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
    #    table = str.maketrans(char, tran)
    #    name = name.translate(table)
    #    try:
    #        await user.edit(
    #            nick=name[::-1],
    #            reason="Set Nick Command was ran by {}".format(ctx.message.author),
    #        )
    #        await ctx.send("(╯°□°）╯︵ " + name[::-1])
    #    except discord.Forbidden:
    #        await ctx.send("(╯°□°）╯︵ " + name[::-1])

    @commands.command()
    async def owo(self, ctx, *, text):
        """Translates text into owo-speak from https://nekos.life/"""
        if len(text) > 199:
            return await ctx.send("Hey! That's too much text! No more than 200 characters please~")
        page = await self.bot.session.get(
            f"https://nekos.life/api/v2/owoify?text={text}"
        )
        neko = await page.json()
        e = discord.Embed(color=self.bot.color, title="OwO", description=neko["owo"])
        await send_message(ctx, embed=e)

    @commands.command(name="8ball")
    async def _8ball(self, ctx, *, text: str):
        """Seek wisdom from the magic eight ball via https://nekos.life/"""
        author = ctx.author
        askme = await self.session.get("https://nekos.life/api/v2/8ball")
        try:
            judgement = await askme.json()
        except aiohttp.ContentTypeError:
            return await ctx.send("Unavailable")
        okhay = f"{author.mention}, {judgement['response']}. 👌"
        embed = discord.Embed(color=self.bot.color, description=f"You asked: {text}")
        embed.set_image(url=judgement["url"])

        await ctx.send(content=okhay, embed=embed)

    @commands.command(name="fact")
    async def facts(self, ctx):
        """Grab a random fact from https://nekos.life/"""
        author = ctx.author

        embed = discord.Embed(color=self.bot.color, title="Random Fact")
        fact = await self.session.get("https://nekos.life/api/v2/fact")
        retrieved = await fact.json()
        embed.set_author(
            name="Fun facts with " + self.bot.user.name,
            icon_url=avatar_check(self.bot.user),
        )
        embed.add_field(
            name=f"Hey {author.display_name}! Here's a random fact for you!",
            value=f"**{retrieved['fact']}**",
        )
        await ctx.send(embed=embed)

    @commands.command(name="nicknameme", aliases=["party"])
    async def nickname_me(self, ctx):
        best_choice = Names.get_name()
        message = ""
        if ctx.author.nick is None:
            message += f"**{ctx.author.name}**, your nickname is **{best_choice}**.\n"
        else:
            message += f"**{ctx.author.name}**, your new nickname is **{best_choice}**.\n"
        try:
            await ctx.author.edit(nick=best_choice, reason="Nickname change ran")
        except discord.Forbidden:
            message += f"<a:error:474000184263573544> Oops! I can't change your nickname! " \
                       f"Double check that I have the `Manage Nicknames` permission; " \
                       f"and that my role is placed high enough in your server settings. " \
                       f"I also can't change the nickname of a server owner " \
                       f"because the Discord API doesn't allow bots to do that. Yeah, I know, it's pretty dumb." \
                       f"Your nickname *would* have been **{best_choice}**."
        embed = discord.Embed(color=self.bot.color, title="Fun Nicknames", description=message)
        if can_send(ctx) and can_embed(ctx):
            await ctx.send(embed=embed)
        elif can_send(ctx):
            await ctx.send(message)

    @commands.command(pass_context=True, no_pm=False)
    async def why(self, ctx, user: discord.Member = None):
        """A random question."""
        whytho = advchoice(Get["why"])
        author = ctx.message.author
        embed = discord.Embed(color=self.bot.color)
        if user is None:
            embed.add_field(name=f"{author.display_name} asks", value=f"**{whytho}**")
            await ctx.send(embed=embed)
        else:
            em = discord.Embed(color=self.bot.color)
            em.add_field(
                name=f"{author.display_name} asks",
                value=f"**{user.mention}, {whytho}**",
            )
            await ctx.send(embed=em)

    @commands.command()
    async def pun(self, ctx, user: discord.Member = None):
        """Puns :D"""
        logic = advchoice(Get["puns"])
        author = ctx.message.author
        em = discord.Embed(color=self.bot.color)
        em.set_author(name="Bad puns with " + self.bot.user.name + "!", icon_url=avatar_check(self.bot.user))
        em.add_field(name=f"Here's your pun, {author.display_name}", value=f"**{logic}**", inline=False)
        await ctx.send(embed=em)

    @commands.command()
    async def joke(self, ctx, user: discord.Member = None):
        """Have a laugh"""
        logic = advchoice(Get["jokes"])
        author = ctx.message.author
        em = discord.Embed(color=self.bot.color)
        em.set_author(name="Funny jokes with " + self.bot.user.name + "!", icon_url=avatar_check(self.bot.user))
        em.add_field(name=f"Have a laugh, {author.display_name}!", value=f"**{logic}**", inline=False)
        await ctx.send(embed=em)

    @commands.command()
    @commands.check(check_nsfw)
    async def roast(self, ctx):
        """Roasting Copypasta"""
        user = ctx.author.name
        logic = advchoice(pastas["roast"])
        em = discord.Embed(color=self.bot.color, title="Roasted!")
        paged = pagify(f"{logic}", delims=".", page_length=1000)
        for page in paged:
            page = page.strip(".").strip() + "."
            em.add_field(name=f"{user},", value=page)
        # em.set_footer(text=f"🐾 {s['roast']} roasts delivered")
        await ctx.send(embed=em)

    @commands.command()
    async def what(self, ctx):
        """have your copypastas"""
        user = ctx.author.name
        logic = advchoice(pastas["haveyour"])
        em = discord.Embed(color=self.bot.color, title="Dayum")
        paged = pagify(f"{logic}", delims=".", page_length=1000)
        for page in paged:
            page = page.strip(".").strip() + "."
            em.add_field(name=f"{user},", value=page)
        await ctx.send(embed=em)

    @commands.command(aliases=["ic"])
    async def identitycrisis(self, ctx):
        """Identifcation CopyPastas"""
        user = ctx.author.name
        logic = advchoice(pastas["identify"])
        em = discord.Embed(color=self.bot.color, title="Identity Crisis")
        em.add_field(name=f"{user},", value=logic)
        await ctx.send(embed=em)

    @commands.command(aliases=["rnd"])
    async def randomness(self, ctx):
        """Useless Paragraphs"""
        user = ctx.author.name
        logic = advchoice(pastas["rns"])
        em = discord.Embed(color=self.bot.color, title="O.o")
        paged = pagify(f"{logic}", delims=".", page_length=1000)
        for page in paged:
            page = page.strip(".").strip() + "."
            em.add_field(name=f"{user},", value=page)
        await ctx.send(embed=em)

    @commands.command(aliases=["htt"])
    async def heresthething(self, ctx):
        """So here's the thing Copypastas"""
        user = ctx.author.name
        logic = advchoice(pastas["arenot"])

        em = discord.Embed(color=self.bot.color, title="Wot?")

        paged = pagify(f"{logic}", delims=".", page_length=1000)
        for page in paged:
            page = page.strip(".").strip() + "."
            em.add_field(name=f"{user},", value=page)
        await ctx.send(embed=em)

    @commands.command(aliases=["hai"])
    async def hi(self, ctx):
        """Hi Copypastas"""
        user = ctx.author.name
        logic = advchoice(pastas["yccm"])
        em = discord.Embed(color=self.bot.color, title="Haiiiiii")

        paged = pagify(f"{logic}", delims=".", page_length=1000)
        for page in paged:
            page = page.strip(".").strip() + "."
            em.add_field(name=f"{user},", value=page)
        await ctx.send(embed=em)

    @commands.command(aliases=["wis"])
    async def wisdom(self, ctx):
        """Gives inspirational Quotes"""
        logic = advchoice(Get["wizz"])
        await ctx.send(content=f":purple_heart: Murr~ :purple_heart:\n**{logic}**")

    @commands.command(aliases=["friends"])
    async def friend(self, ctx):
        """Gives Friendship Quotes"""
        logic = advchoice(Get["friends"])
        await ctx.send(content=f":purple_heart: Murr~ :purple_heart:\n**{logic}**")

    @commands.command()
    async def fml(self, ctx):
        fml_msg = await ExGet.alexflipnote_api(self.bot, 'fml')
        await ctx.send(content=fml_msg['text'])

    @commands.command(aliases=["blurplify", "blurple"])
    async def blurplefy(self, ctx):
        user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://ourmainfra.me/api/v2/blurple?url={user.avatar_url_as(format='png')}",
                headers={"Authorization": os.environ["MAINFRAME_API_KEY"]},
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("blurplefy.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Blurple!")
                em.set_image(url="attachment://blurplefy.png")
                await ctx.send(file=discord.File("blurplefy.png"), embed=em)
            else:
                await ctx.send(f"{str(resp.status)}")

    @commands.command(aliases=["holloween"])
    async def halloweenify(self, ctx):
        user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://ourmainfra.me/api/v2/halloween?url={user.avatar_url_as(format='png')}",
                headers={"Authorization": os.environ["MAINFRAME_API_KEY"]},
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("blurplefy.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Spooky!")
                em.set_image(url="attachment://blurplefy.png")
                await ctx.send(file=discord.File("blurplefy.png"), embed=em)

    @commands.command()
    async def pinkify(self, ctx):
        user = ctx.author
        em = discord.Embed(color=self.bot.color)
        async with self.session.get(
                f"https://ourmainfra.me/api/v2/blurple/pink?url={user.avatar_url_as(format='png')}",
                headers={"Authorization": os.environ["MAINFRAME_API_KEY"]},
        ) as resp:
            if resp.status == 200:
                abandon = await resp.read()
                with open("blurplefy.png", "wb") as f:
                    f.write(abandon)
                    em.set_author(name="Pink!")
                em.set_image(url="attachment://blurplefy.png")
                await ctx.send(file=discord.File("blurplefy.png"), embed=em)
            else:
                await ctx.send(f"{str(resp.status)}")


def setup(bot):
    bot.add_cog(Fun(bot))
