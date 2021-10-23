import discord
from discord.ext import commands

from API.API import base_url, headers


async def send_message(ctx, embed: discord.Embed = False, message: str = False, file: discord.File = False,
                       delete: int = False):
    if isinstance(ctx.channel, discord.TextChannel):
        if can_send(ctx):
            if embed and file:
                if can_embed(ctx) and can_upload(ctx):
                    return await ctx.send(embed=embed, file=file)
                return await ctx.send("I require the permissions embed links and attach files"
                                      " in order to send this response.")
            elif message and file:
                if can_upload(ctx):
                    return await ctx.send(content=message, file=file)
                return await ctx.send("I require the permissions attach files"
                                      " in order to send this response.")
            elif message and embed:
                if can_embed(ctx):
                    return await ctx.send(content=message, embed=embed)
                return await ctx.send("I require the permission embed links in order to send this response.")
            elif embed:
                if can_embed(ctx):
                    return await ctx.send(embed=embed)
                return await ctx.send("I require the permission embed links in order to send this response.")
            elif message:
                return await ctx.send(content=message)
            elif file:
                if can_upload(ctx):
                    return await ctx.send(file=file)
        try:
            if can_react(ctx):
                await ctx.message.add_reaction("❌")
            return await ctx.author.send(f"I cannot send messages in {ctx.channel.mention}.")
        except discord.Forbidden:
            return
    if isinstance(ctx.channel, discord.DMChannel):
        try:
            if embed and file:
                return await ctx.send(embed=embed, file=file)
            elif message and file:
                return await ctx.send(content=message, file=file)
            elif message and embed:
                return await ctx.send(content=message, embed=embed)
            elif embed:
                return await ctx.send(embed=embed)
            elif message:
                return await ctx.send(content=message)
            elif file:
                return await ctx.send(file=file)
        except discord.Forbidden:
            return


def check_hierarchy(ctx: commands.Context, role: discord.Role):
    return ctx.guild.me.top_role.position > role.position


def can_manage_user(
        ctx: commands.Context = None,
        user: discord.user = None,
        guild: discord.Guild = None,

):
    if ctx:
        if user.id == ctx.guild.owner.id:
            return False
        elif ctx.guild.me.top_role > user.top_role:
            return True
    if guild:
        if user.id == guild.owner.id:
            return False
        elif guild.me.top_role > user.top_role:
            return True


async def check_nsfw(ctx: commands.Context):
    if isinstance(ctx.channel, discord.DMChannel):
        return True
    if ctx.channel.is_nsfw():
        return True
    cmd = ctx.command.name
    if cmd == "pussy":
        if can_embed(ctx):
            async with ctx.bot.session.get(
                    base_url + "cat", headers=headers,
            ) as resp:
                if resp.status == 200:
                    json = await resp.json()
                else:
                    json = {"url": "https://sheri.bot/media/service-unavaliable.png"}

            embed = discord.Embed(color=discord.Colour.orange(), title=f"fur{cmd} is a NSFW command.",
                                  description=f"NSFW commands are not allowed in "
                                              "this channel because the channel is not marked for NSFW.\n"
                                              f"If this not intended, please run ``'furnsfw'``\n"
                                              f"Here is a pussy for you though :)")
            embed.set_image(url=json['url'])
            embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1")
            await send_message(ctx, embed=embed)
            return False
    else:
        if can_embed(ctx):
            message = f"<a:bug:474000184901369856> | **``fur{cmd}``is a NSFW COMMAND**| <a:bug:474000184901369856>"
            embed = discord.Embed(color=discord.Color.orange(),
                                  description="NSFW commands are not allowed in "
                                              "this channel because the channel is not marked for NSFW.\n"
                                              "If this not intended, please run ``furnsfw``")
            embed.set_footer(text=f"Powered by: furhost.net")
            await send_message(ctx, message=message, embed=embed)
        else:
            message = (f"<a:bug:474000184901369856> | **``fur{cmd}`` is a NSFW COMMAND** | <a:bug:474000184901369856>\n"
                       "NSFW commands are not allowed in this channel because the channel is not marked for NSFW.\n"
                       "If this not intended, please run ``furnsfw``")
            await send_message(ctx, message=message)
        return False


def can_send(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).send_messages
    if guild and channel:
        try:
            return guild.me.permissions_in(channel).send_messages

        except AttributeError:
            return False


def can_react(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).add_reactions
    if guild and channel:
        return guild.me.permissions_in(channel).add_reactions


def can_embed(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).embed_links
    if guild and channel:
        return guild.me.permissions_in(channel).embed_links


def can_manage_channel(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).manage_channels
    if guild and channel:
        return guild.me.permissions_in(channel).manage_channels


def can_external_react(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None,
):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).external_emojis
    if guild and channel:
        return guild.me.permissions_in(channel).external_emojis


def can_delete(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).manage_messages
    if guild and channel:
        return guild.me.permissions_in(channel).manage_messages


def can_kick(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).kick_members
    if guild and channel:
        return guild.me.permissions_in(channel).kick_members


def can_create_webhook(
        ctx: commands.Context = None,
        guild: discord.Guild = None,
        channel: discord.TextChannel = None):
    if ctx:
        if channel is None:
            channel = ctx.channel
        if not ctx.guild:
            return False
        return ctx.guild.me.permissions_in(channel).manage_webhooks
    if guild and channel:
        return guild.me.permissions_in(channel).manage_webhooks


def can_upload(ctx: commands.Context, channel: discord.TextChannel = None):
    if not channel:
        channel = ctx.channel
    if not ctx.guild:
        return False
    return ctx.guild.me.permissions_in(channel).attach_files


def can_edit_role(ctx: commands.Context, role: discord.Role):
    if not ctx.guild:
        return False
    return ctx.guild.me.permissions_in(ctx.channel).manage_roles and check_hierarchy(
        ctx, role
    )
