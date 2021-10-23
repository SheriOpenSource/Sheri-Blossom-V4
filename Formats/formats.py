import datetime
import io
from datetime import datetime, timedelta

import colorthief
import discord
import emoji
from discord.ext import commands

# https://www.webpagefx.com/tools/emoji-cheat-sheet/
from Checks.bot_checks import can_send, can_embed


# from utils.checks.bot_checks import can_send, can_embed


def get_icon():
    file = open("Logo/banner.txt", encoding="utf8")
    return file.read()


# What

bad_argument_text = (
    "Uh oh, I can't find that role in here, are you sure you spelled it right?\n"
    "Remember that capitalization matters, coolrolename isn't the same to me as CoolRoleName!"
)


def get_emoji_by_name(name: str):
    return emoji.emojize(name, True)


def pagify(text, delims=["\n"], shorten_by=8, page_length=1900):
    if not delims:
        delims = ["\n"]

    in_text = text
    page_length -= shorten_by
    while len(in_text) > page_length:
        closest_delim = max([in_text.rfind(d, 0, page_length) for d in delims])
        closest_delim = closest_delim if closest_delim != -1 else page_length
        to_send = in_text[:closest_delim]
        yield to_send
        in_text = in_text[closest_delim:]
    yield in_text


def escape(text: str):
    text = text.replace("@everyone", "@\u200beveryone")
    text = text.replace("@here", "@\u200bhere")
    return text


async def embed(
        ctx: commands.Context, text: str, color: discord.Color = discord.Color.purple()
):
    if not can_send(ctx):
        return
    if not can_embed(ctx):
        await ctx.channel.send(
            f"{get_emoji_by_name(':x:')} **error** You must give this bot embed permissions"
        )
    em = discord.Embed(description=text, color=color)
    await ctx.send(embed=em)


async def same_person(ctx, user):
    if ctx.author.id == user.id:
        return True
    else:
        return False


async def em(self, desc, channel):
    """Shows the invite."""
    try:
        em = discord.Embed(description=desc, color=0xFFC0CB)
        await channel.send(embed=em)
    except:
        await channel.send(
            "\U0000274c **error** You must give this bot embed permissions"
        )


async def current_time():
    time = datetime.datetime.now()
    fmt = "[ %I:%M:%S ] %B, %d %Y"
    return time.strftime(fmt)


async def get_dominant_color(bot, url):
    """dominant color of img"""
    async with bot.session.get(url) as resp:
        image = await resp.read()
    with io.BytesIO(image) as f:
        try:
            color = colorthief.ColorThief(f).get_color(quality=10)
        except:
            return discord.Color.default()
    return discord.Color.from_rgb(*color)


async def nopingpatch(ha):
    troll = (
        ha.replace("@everyone", "pinger")
            .replace("@here", "pinger")
            .replace("everyone", "pinger")
            .replace("here", "pinger")
    )
    return troll


class RoleID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            r = await commands.RoleConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(bad_argument_text) from None
                # raise commands.BadArgument(f"{argument} is not a valid role or role ID.") from None
        else:
            can_execute = (
                    ctx.author.id == ctx.bot.owner_id
                    or ctx.author == ctx.guild.owner
                    or ctx.author.top_role.position > r.position
            )

            if not can_execute:
                raise commands.BadArgument(
                    "You cannot do this action due to role hierarchy."
                )
            return r.id


class RoleID_member(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            r = await commands.RoleConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(bad_argument_text) from None
        else:
            return r.id


def avatar_check(user):
    if user.avatar_url:
        if user.is_avatar_animated():
            return user.avatar_url_as(format="gif")
        else:
            return user.avatar_url_as(format="png")
    else:
        return "https://imgur.com/gPl45Y4.png"


def icon_check(guild):
    default = "https://imgur.com/gPl45Y4.png"
    if guild is None:
        return default
    elif guild.icon_url:
        if guild.is_icon_animated():
            return guild.icon_url_as(format="gif")
        else:
            return guild.icon_url_as(format="png")
    else:
        return default


def build_message(
        message: str,
        author: discord.Member = None,
        user: discord.Member = None,
        guild: discord.Guild = None,
        level: int = None,
):
    if not message:
        return None
    if author:
        message = message.replace("{AUTHOR_MENTION}", author.mention)
        message = message.replace("{AUTHOR_NAME}", author.name)
    if user:
        message = message.replace("{USER_MENTION}", user.mention)
        message = message.replace("{USER_NAME}", user.name)
    if guild:
        message = message.replace("{GUILD_NAME}", guild.name)
        message = message.replace("{GUILD_COUNT_ALL}", str(len(guild.members)))
        message = message.replace(
            "{GUILD_COUNT_USERS}", str(len([i for i in guild.members if not i.bot]))
        )
        message = message.replace(
            "{GUILD_COUNT_BOTS}", str(len([i for i in guild.members if i.bot]))
        )
    if level:
        message = message.replace("{LEVEL}", str(level))
    return message


async def build_embed(
        bot,
        information: dict,
        guild: discord.Guild,
        author: discord.Member,
        user: discord.Member = None,
):
    title = information.pop("title", None)
    descr = information.pop("descr", None)
    img = information.pop("img", None)
    thumbnail = information.pop("thumbnail", None)
    author_icon = information.pop("author_icon", None)
    author_name = information.pop("author_name", None)
    author_url = information.pop("author_url", None)
    content = information.pop("content", None)
    footer_text = information.pop("footer_text", None)
    footer_icon = information.pop("footer_icon", None)
    color = bot.color
    em = discord.Embed(color=color)
    if title:
        em.title = build_message(message=title, author=author, user=user, guild=guild)
    if descr:
        em.description = build_message(
            message=descr, author=author, user=user, guild=guild
        )
    if author_name:
        author_name = build_message(message=author_name, author=author, guild=guild)
        if author_url:
            if author_icon:
                em.set_author(name=author_name, url=author_url, icon_url=author_icon)
            else:
                em.set_author(name=author_name, url=author_url)
        elif author_icon:
            em.set_author(name=author_name, icon_url=author_icon)
            if author_url:
                em.set_author(name=author_name, url=author_url, icon_url=author_icon)
        else:
            em.set_author(name=author_name)
    if img:
        em.set_image(url=img)
    if thumbnail:
        em.set_thumbnail(url=thumbnail)
    if footer_text or footer_icon:
        if footer_icon:
            em.set_footer(text=footer_text, icon_url=footer_icon)
        else:
            em.set_footer(text=footer_text)
    for key, value in information.items():
        em.add_field(name=key, value=value, inline=True)
    if content:
        content = build_message(message=content, author=author, user=user, guild=guild)
    return content, em


def format_retry_after(retry_after):
    time = timedelta(seconds=int(round(retry_after, 0)))
    hours, remainder = divmod(int(time.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    if days:
        fmt = (
            f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
        )
    elif hours:
        fmt = f"{hours} hours, {minutes} minutes, and {seconds} seconds"
    elif minutes:
        fmt = f"{minutes} minutes and {seconds} seconds"
    else:
        fmt = f"{seconds} seconds"
    return "You can try again in " + fmt
