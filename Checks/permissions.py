import discord

from discord.ext import commands

owners = [
    173237945149423619,  # Kanin
    139800365393510400,  # Waspy,
    248294452307689473,  # Tails
    252362165456076800,  # Kyle <3
    83006253919375360,  # Atoro
    493308716427509761,  # Talvi
    106511913222955008,  # Alphy
    443276440168038401,  # Kano
    406707961214402568,  # spacey
]


async def check_permissions(ctx, perms, *, check=all):
    if ctx.author.id in owners:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(
        getattr(resolved, name, None) == value for name, value in perms.items()
    )


def has_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)

    return commands.check(pred)


def can_send(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).send_messages
    )


def can_read(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).read_messages
    )


def manage_webhooks(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).manage_webhooks
    )


def can_delete(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).manage_messages
    )


def can_kick(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).kick_members
    )


def can_ban(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).ban_members
    )


def can_nick(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).manage_nicknames
    )


def can_administrator(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).administrator
    )


def can_roles(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).manage_roles
    )


def can_embed(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).embed_links
    )


def can_manage(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).manage_messages
    )


def can_upload(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).attach_files
    )


def can_react(ctx):
    return (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.channel.permissions_for(ctx.guild.me).add_reactions
    )


def is_nsfw(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.is_nsfw()
