import asyncio

import discord
# from dateutil.relativedelta import relativedelta
from discord.ext import commands

from Formats.formats import avatar_check
from Lines.custom_emotes import get as emote
from API.API import Retrieval as Get
from Checks.bot_checks import check_nsfw


class Dm_sending(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def authorize_nsfw_sending(ctx, member):
        await ctx.send(
            "Hang on there fluffbutt! I have to check to make sure they are above age!"
        )
        await member.send(
            f"{ctx.author.display_name} is wanting to send you some nsfw images, but due to some circumstances,"
            f" i need to verify that you are above age to receive the explict content"
        )

        def check(m):
            return isinstance(m.channel, discord.DMChannel) and m.author == member

        try:
            response = await ctx.bot.wait_for("message", timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.send(
                f"I think they are ignoring me or not even there. I tried {ctx.author.name}!"
            )
            return await member.send(
                "Times up! You will need to wait for another opportunity"
            )

        # bd_datetime = datetime.datetime.strptime(response.content, "%m/%d/%Y")
        # delta = relativedelta(datetime.datetime.now(), bd_datetime)
        # await ctx.send(f"They are {delta.years} years old")

    async def send_dm(self, ctx, nsfw, endpoint, member: discord.Member):
        if member.bot:
            return await ctx.send(
                "Oops, it appears this command was ran on a bot in which case it cannot be used. "
                "Please try again with a user instead of a bot, thank you."
            )

        options = ["yes", "no"]
        send_embed = discord.Embed(
            color=self.bot.color,
            description=f"{ctx.author.mention} is trying to send you an image.",
        )
        send_embed.set_thumbnail(url=avatar_check(ctx.author))
        send_embed.set_author(
            name=f"Endpoint: {endpoint}", icon_url=avatar_check(self.bot.user)
        )
        send_embed.set_footer(
            text="Sheri is proudly powered by: https://furhost.net | Bot Version: v4.1b"
        )
        msg = await ctx.send(f"{emote['sheri emotes']['Paws']} Please wait...")
        if nsfw:
            send_embed.add_field(
                name="Image is NSFW",
                value="Do you accept the image?\n"
                      "Valid responses are: ``Yes``, ``No``",
            )
            try:
                await member.send(embed=send_embed)
            except discord.Forbidden:
                return await ctx.send(
                    "I think they have me blocked or are not accepting DMs"
                )
        else:
            send_embed.add_field(
                name="Image is SFW",
                value="Do you accept the image?\n"
                      "Valid responses are: ``Yes``, ``No``",
            )
            try:
                await member.send(embed=send_embed)
            except discord.Forbidden:
                return await ctx.send(
                    "I think they have me blocked or are not accepting DMs"
                )

        def check(m):
            return isinstance(m.channel, discord.DMChannel) and m.author == member

        try:
            response = await ctx.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(
                f"I think they are ignoring me or not even there. I tried {ctx.author.name}!"
            )
            return await member.send(
                "You didn't respond in time therefore, you will not receive the image."
            )
        if response.content.lower() not in options:
            try:
                await member.send("You need to tell me yes or no.")
            except discord.Forbidden:
                return await ctx.send(
                    "I think they have me blocked or are not accepting DMs"
                )
        if response.content.lower() == "yes":
            await msg.delete()
            await ctx.send(f"Good job {ctx.author.mention}!")
            await self.build_dm_image(ctx, endpoint, member)
        if response.content.lower() == "no":
            await msg.delete()
            try:
                await member.send(
                    f"Alright, Thank you! Informing {ctx.author.name} now."
                )
            except discord.Forbidden:
                return await ctx.send(
                    "I think they have me blocked or are not accepting DMs"
                )
            await ctx.send(
                content=f"I'm sorry, I tried to deliver {endpoint}, unfortunately they rejected it."
            )

    async def build_dm_image(self, ctx, endpoint, member: discord.Member):
        image = await Get.main_api(self.bot, endpoint)
        embed = discord.Embed(
            color=self.bot.color,
            description=f"No image? **[Click Here]({image['url']})**",
        )
        embed.set_image(url=image["url"])
        embed.set_author(name=ctx.author, icon_url=avatar_check(ctx.author))
        try:
            await member.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(
                "It appears that they have their dms disabled or have blocked me :("
            )

    ####################################################################################################################
    #                                           NSFW
    ####################################################################################################################

    @commands.cooldown(4, 10, type=commands.BucketType.user)
    @commands.group(name="nsend")
    @commands.check(check_nsfw)
    async def n_send(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=self.bot.color)
            embed.add_field(
                name="Commands",
                value="nsend yiff [@user]\nnsend solo [@user]\n"
                      "nsend gay [@user]\nnsend lesbian [@user]\n"
                      "nsend futa [@user]\nnsend femboy [@user]\n",
            )
            await ctx.send(embed=embed)

    @n_send.command(name="gif")
    @commands.check(check_nsfw)
    async def n_send_gif(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        await self.send_dm(ctx, True, "gif", member)

    @n_send.command(name="yiff")
    @commands.check(check_nsfw)
    async def n_send_yiff(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        await self.send_dm(ctx, True, "yiff", member)

    @n_send.command(name="gay")
    @commands.check(check_nsfw)
    async def n_send_gay(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        await self.send_dm(ctx, True, "gay", member)

    @n_send.command(name="lesbian")
    @commands.check(check_nsfw)
    async def n_send_lesbian(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        await self.send_dm(ctx, True, "lesbian", member)

    @n_send.command(name="dick")
    @commands.check(check_nsfw)
    async def n_send_dick(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        await self.send_dm(ctx, True, "dick", member)

    @n_send.command(name="femboy")
    @commands.check(check_nsfw)
    async def n_send_femboy(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        await self.send_dm(ctx, True, "nfemboy", member)

    @n_send.command(name="futa")
    @commands.check(check_nsfw)
    async def n_send_futa(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        await self.send_dm(ctx, True, "nfuta", member)


def setup(bot):
    bot.add_cog(Dm_sending(bot))
