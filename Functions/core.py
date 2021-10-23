from random import choice

import discord

from Checks.bot_checks import (
    can_send, can_embed, can_react,
    can_upload, can_delete, can_external_react)
from Formats.chat_markdown import bold
from Functions.randomization import advchoice
from Lines.valid_endpoints import Endpoints

sheri_colors = [
    0xFCBACB,
    0xFDABBF,
    0xFD9DB4,
    0xFE8EA8,
    0xFE7F9C,
    0xFFC0CB,
    0xDD96C4,
    0xE19AD3,
    0xF0AEED,
    0xF2B7F0,
    0xF6C9EE,
    0xF3B9E9,
    0xF1A8E4,
    0xEF6BB0,
    0xFF8899,
    0xFF7788
]


async def send_message(ctx, embed: discord.Embed = False, message: str = False, file: discord.File = False,
                       delete: int = False, custom_emoji: bool = False, delete_delay: int = False):
    errors = {
        "external emojis":
            "I require the permission ``External Emojis`` in order to send this response.",
        "embed links":
            "I require the permission ``Embed Links`` in order to send this response.",
        "attach files":
            "I require the permission ``Attach Files`` in order to send this response.",
        "send messages":
            f"I cannot send messages in {ctx.channel.mention}."
    }
    try:
        if isinstance(ctx.channel, discord.TextChannel):
            if can_send(ctx):
                if file and custom_emoji and embed and message:
                    if can_embed(ctx):
                        if can_upload(ctx):
                            if can_external_react(ctx):
                                return await ctx.send(content=message, file=file, embed=embed)
                            return await ctx.send(errors['external emojis'])
                        return await ctx.send(errors['attach files'])
                    return await ctx.send(errors['embed links'])

                if file and embed and message:
                    if can_embed(ctx):
                        if can_upload(ctx):
                            return await ctx.send(content=message, file=file, embed=embed)
                        return await ctx.send(errors['attach files'])
                    return await ctx.send(errors['embed links'])

                if file and embed:
                    if can_embed(ctx):
                        if can_upload(ctx):
                            return await ctx.send(file=file, embed=embed)
                        return await ctx.send(errors['attach files'])
                    return await ctx.send(errors['embed links'])

                if file and message:
                    if can_upload(ctx):
                        return await ctx.send(file=file, content=message)
                    return await ctx.send(errors['attach files'])

                if custom_emoji and embed and message:
                    if can_embed(ctx):
                        if can_external_react(ctx):
                            return await ctx.send(content=message, embed=embed)
                        return await ctx.send(errors['external emojis'])
                    return await ctx.send(errors['embed links'])

                if custom_emoji and embed and delete_delay:
                    if can_embed(ctx):
                        if can_external_react(ctx):
                            return await ctx.send(embed=embed, delete_after=delete_delay)
                        return await ctx.send(errors['external emojis'])
                    return await ctx.send(errors['embed links'])

                if message and delete_delay:
                    return await ctx.send(content=message, delete_after=delete_delay)

                if custom_emoji and embed:
                    if can_embed(ctx):
                        if can_external_react(ctx):
                            return await ctx.send(embed=embed)
                        return await ctx.send(errors['external emojis'])
                    return await ctx.send(errors['embed links'])

                if custom_emoji and message:
                    if can_external_react(ctx):
                        return await ctx.send(content=message)
                    return await ctx.send(errors['external emojis'])

                if embed and message:
                    if can_embed(ctx):
                        return await ctx.send(content=message, embed=embed)
                    return await ctx.send(errors['embed links'])

                if embed:
                    if can_embed(ctx):
                        return await ctx.send(embed=embed)
                    return await ctx.send(errors['embed links'])

                if message:
                    return await ctx.send(content=message)
            else:
                try:
                    if can_react(ctx):
                        await ctx.message.add_reaction("❌")
                    return await ctx.author.send(errors['send messages'])
                except discord.Forbidden:
                    return

        if isinstance(ctx.channel, discord.DMChannel):
            try:
                if file and custom_emoji and message and embed:
                    return await ctx.send(content=message, file=file, embed=embed)

                elif custom_emoji and embed and message:
                    return await ctx.send(content=message, embed=embed)

                elif embed and message:
                    return await ctx.send(content=message)

                elif embed:
                    return await ctx.send(embed=embed)

                elif message:
                    return await ctx.send(content=message)
            except discord.Forbidden:
                return
    except discord.NotFound:
        return


def make_embed(color, title: str = None, description: str = None, author: str = None, author_icon: str = None,
               author_link: str = None, footer_text: str = None, footer_icon: str = None,
               thumbnail: str = None, image: str = None,
               ):
    """" THE ULTIMATE EFFORT IN REDUCING CODE DUPLICATION"""
    if color and title and description and author and author_icon and author_link and footer_text and footer_icon and \
            thumbnail:
        embed = discord.Embed(color=color, title=title, description=description)
        embed.set_author(name=author, url=author_link, icon_url=author_icon)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        embed.set_thumbnail(url=thumbnail)
        return embed

    if color and title and description and author and author_icon and author_link and footer_text and footer_text \
            and footer_icon and thumbnail and image:
        embed = discord.Embed(color=color, title=title, description=description)
        embed.set_author(name=author, url=author_link, icon_url=author_icon)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        embed.set_image(url=image)
        embed.set_thumbnail(url=thumbnail)
        return embed

    if color and title and author and author_icon and author_link and footer_text and footer_icon and thumbnail:
        embed = discord.Embed(color=color, title=title)
        embed.set_author(name=author, url=author_link, icon_url=author_icon)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        embed.set_thumbnail(url=thumbnail)
        return embed

    if color and title and author and author_icon and author_link and footer_text and footer_icon and image:
        embed = discord.Embed(color=color, title=title)
        embed.set_author(name=author, url=author_link, icon_url=author_icon)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        embed.set_image(url=image)
        return embed

    if color and title and author and author_icon and author_link and footer_text and footer_icon:
        embed = discord.Embed(color=color, title=title)
        embed.set_author(name=author, url=author_link, icon_url=author_icon)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        return embed

    if color and title and author and author_icon and footer_text and footer_icon:
        embed = discord.Embed(color=color, title=title)
        embed.set_author(name=author, icon_url=author_icon)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        return embed

    if color and title and author and footer_text and footer_icon:
        embed = discord.Embed(color=color, title=title)
        embed.set_author(name=author)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        return embed

    if color and title and footer_icon and footer_text:
        embed = discord.Embed(color=color, title=title, )
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        return embed

    if color and title and footer_icon:
        embed = discord.Embed(color=color, title=title)
        embed.set_footer(icon_url=footer_icon)
        return embed

    if color and title:
        embed = discord.Embed(color=color, title=title)
        return embed

    if color and description:
        embed = discord.Embed(color=color, description=description)
        return embed

    if color and author:
        embed = discord.Embed(color=color)
        embed.set_author(name=author)
        return embed

    if color and title and description and footer_text and footer_icon and thumbnail:
        embed = discord.Embed(color=color, title=title, description=description)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        embed.set_thumbnail(url=thumbnail)
        return embed

    if color and title and description and footer_text and footer_icon and image:
        embed = discord.Embed(color=color, title=title, description=description)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        embed.set_image(url=image)
        return embed

    if color and title and description and footer_text and footer_icon:
        embed = discord.Embed(color=color, title=title, description=description)
        embed.set_footer(icon_url=footer_icon, text=footer_text)
        return embed

    if color and title and description and footer_text:
        embed = discord.Embed(color=color, title=title, description=description)
        embed.set_footer(text=footer_text)
        return embed

    if color and title and description and footer_icon:
        embed = discord.Embed(color=color, title=title, description=description)
        embed.set_footer(icon_url=footer_icon)
        return embed


async def do_removal(ctx, limit, predicate, *, before=None, after=None, message=True):
    try:
        deleted = None
        if limit > 2000:
            return await ctx.send(
                f"Too many messages to search given ({limit}/2000)", delete_after=10
            )

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            if can_delete(ctx):
                deleted = await ctx.channel.purge(
                    limit=limit, before=before, after=after, check=predicate
                )
        except discord.Forbidden:
            if can_send(ctx):
                return await ctx.send("I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await ctx.send(f"Error: {e} (try a smaller search?)")

        deleted = len(deleted)
        if message is True:
            await ctx.send(
                f'Eaten {deleted} message{"" if deleted == 1 else "s"}. ' ":yum:",
                delete_after=10,
            )
    except (discord.Forbidden, discord.NotFound):
        pass


async def commands_help(ctx, commands, main):
    cmd_list = ""
    for command in commands:
        comm = ctx.bot.get_command(command)
        cmd_list += f"fur**{comm} {comm.signature}** {comm.help}\n"
    embed = discord.Embed(color=ctx.color, title=f"{main}'s Sub Commands", description=cmd_list)
    if can_embed(ctx):
        await ctx.send(embed=embed)
    else:
        if can_send(ctx):
            await ctx.send(cmd_list)


async def get_command_stats(ctx, commands):
    data = await ctx.pool.fetch(
        f"SELECT command, usage_count FROM botsettings_commandcount WHERE command in {commands} ORDER BY usage_count DESC")
    output = ""
    for command in data:
        output += "{}: ``{:,}``\n".format(bold(command['command']), command['usage_count'])
    return output


async def get_general_stats(ctx, commands):
    data = await ctx.pool.fetch(
        f"SELECT command, usage_count FROM botsettings_commandcount WHERE command in {commands}")
    stats = ""
    for command in data:
        if command['command'] == "messages_seen":
            stats += f"<:message:451852158137008128> Messages Seen: ``{command['usage_count']:,}``\n"
        elif command['command'] == "guild_join":
            stats += f"<:sheriwave:457367018342187008> Guilds Joined: ``{command['usage_count']:,}``\n"
        elif command['command'] == "guild_leave":
            stats += f"<:error:451845273124208652> Guilds Left: ``{command['usage_count']:,}``\n"
        elif command['command'] == "@everyones_seen":
            stats += f"<a:error:474000184263573544> @everyones seen: ``{command['usage_count']:,}``\n"
        elif command['command'] == "@here_seen":
            stats += f"<a:error:474000184263573544> @heres seen: ``{command['usage_count']:,}``\n"
        elif command['command'] == "commands_processed":
            stats += f"<:Count:451852157860184074> Commands processed ``{command['usage_count']:,}``\n"
        else:
            stats += f"{command['command']} {command['usage_count']}"
    return stats


# NOT READY TO USE YET
async def sheri_random_response(ctx, nsfw):
    nsfw_responses = ["Yes? Yiff Yiff~", "W-What do you want? I'm doing something naughty right now.",
                      "Yes I'm here UwU", "What do you want naughty fur?"]

    sfw_responses = ["Yes?", "Hmmmmm.....", "Like using me? Consider trying out my fun commands :)"]

    if nsfw:
        await send_message(ctx, message=choice(nsfw_responses))
    else:
        return choice(sfw_responses)


async def endpoint_checker(ctx, endpoint):
    endpoint_results = Endpoints.check_endpoint(endpoint, ctx.channel.is_nsfw())
    results = endpoint_results[0]
    if results is False:
        if endpoint_results[1] == "unknown":
            valid_endpoints = Endpoints.list_endpoints(True, True)
            embed = discord.Embed(color=ctx.color,
                                  description=endpoint_results[2])
            embed.add_field(name="**SFW ENDPOINTS**", value=valid_endpoints[0], inline=False)
            if ctx.channel.is_nsfw():
                embed.add_field(name="**NSFW ENDPOINTS**", value=valid_endpoints[1], inline=True)
            await ctx.send(f"The endpoint {endpoint} is invalid, see below..", embed=embed)
            return False
        if endpoint_results[1] == "error":
            valid_endpoints = Endpoints.list_endpoints(True, False)
            embed = discord.Embed(color=ctx.color,
                                  description=endpoint_results[2])
            embed.add_field(name="**SFW ENDPOINTS**", value=valid_endpoints, inline=False)
            await ctx.send(f"This endpoint can't be used in a sfw environment...", embed=embed)
            return False
    if results:
        return True


def embed_color():
    return advchoice(sheri_colors)
