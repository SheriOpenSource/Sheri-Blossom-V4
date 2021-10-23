import asyncio

import discord

from Checks.bot_checks import send_message
from Formats.formats import avatar_check
from Lines.custom_emotes import get as emote
from API.API import Retrieval as Get


async def send_dm(self, ctx, nsfw, endpoint, member: discord.Member):
    if member.bot:
        return await ctx.send(
            "Oops, it appears this command was ran on a bot in which case it cannot be used. "
            "Please try again with a user instead of a bot, thank you."
        )

    options = ["yes", "no"]
    send_embed = discord.Embed(
        color=ctx.bot.color,
        description=f"{ctx.author.mention} is trying to send you an image.",
    )

    send_embed.set_thumbnail(url=avatar_check(ctx.author))
    send_embed.set_author(
        name=f"Endpoint: {endpoint}", icon_url=avatar_check(self.bot.user)
    )

    send_embed.set_footer(
        text="Sheri is proudly powered by: https://furhost.net | Bot Version: v4.3"
    )

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

    msg = await send_message(ctx, embed=discord.Embed(color=ctx.color, title="DM Image Sender",
                                                      description="<a:ooh:473963385269125130> Attempting to send"
                                                                  f" {endpoint} to {member.mention}... Please wait"))
    try:
        response = await ctx.bot.wait_for("message", timeout=120, check=check)
    except asyncio.TimeoutError:
        await msg.delete()
        embed = discord.Embed(color=ctx.color, title="DM Image Sender",
                              description=f"{member} is not there or they are ignoring me."
                                          f" <:shrug:572486049243332618>")
        await ctx.send(embed=embed)
        return await member.send(
            f"You didn't respond in time to receive the image from {ctx.author}."
        )

    if response.content.lower() not in options:
        try:
            await member.send("You need to tell me yes or no.")
            await msg.delete()
        except discord.Forbidden:
            return await ctx.send(
                "I think they have me blocked or are not accepting DMs"
            )

    if response.content.lower() == "yes":
        try:
            await msg.delete()
        except discord.Forbidden:
            pass

        embed = discord.Embed(color=ctx.color, title="DM Image Sender",
                              description=f"``{member.display_name}`` has accepted the image and your image "
                                          f"has been delivered successfully").set_thumbnail(
            url="https://cdn.discordapp.com/emojis/563783885230702622.png?v=1")
        await ctx.send(f"Good job {ctx.author.mention}", embed=embed)
        await build_dm_image(self, ctx, endpoint, member)
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

        embed = discord.Embed(color=ctx.color, title="DM Image Sender",
                              description=f"``{member.display_name}`` rejected your beautiful image :(") \
            .set_thumbnail(url="https://cdn.discordapp.com/emojis/685118828283166746.png?v=1")
        await ctx.send(ctx.author.mention, embed=embed)


async def build_dm_image(self, ctx, endpoint, member: discord.Member):
    image = await Get.main_api(self.bot, endpoint)
    embed = discord.Embed(title=f"{ctx.author} sent you this image!",
                          color=self.bot.color,
                          description=f"No image? **[Click Here]({image['url']})**\n"
                                      f"Something wrong with the image? [report it here]({image['report_url']})",
                          )

    embed.set_image(url=image["url"])
    try:
        await member.send(embed=embed)

    except discord.Forbidden:
        await ctx.send(
            "It appears that they have their dms disabled or have blocked me :("
        )
