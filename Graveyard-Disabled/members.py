from datetime import datetime

import discord
from discord.ext import commands

from Database.transactions import give_api_permissions, give_premium
from Formats.formats import avatar_check, icon_check
from Functions.logging import Logging
from Lines.custom_emotes import logging_emotes


def diff(li1, li2):
    return [i for i in li1 if i not in li2] + [i for i in li2 if i not in li1]


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if not self.bot.is_ready():
            return
        guild = before.guild
        try:
            channel, embed_enabled = await Logging.get_log_channel(self, "guild_channel", guild)
            if channel:
                embed = discord.Embed(colour=self.bot.color)
                embed.set_author(name=before.name, icon_url=avatar_check(self.bot.user))
                embed.timestamp = datetime.utcnow()
                embed.set_footer(text=f"Channel-ID: {before.id}")
                if embed_enabled:
                    if isinstance(before, discord.VoiceChannel):

                        if before.name != after.name:
                            embed.description = f"**Name Changed**"
                            embed.add_field(
                                name="Before", value=before.name, inline=True
                            )
                            embed.add_field(name="after", value=after.name, inline=True)
                            await Logging.send_logs(channel, embed=embed, guild=guild)

                        if before.bitrate != after.bitrate:
                            embed.description = "**Bitrate Changed**"
                            embed.add_field(
                                name="Before",
                                value=f"{before.bitrate}kbps",
                                inline=True,
                            )
                            embed.add_field(
                                name="after", value=f"{after.bitrate}kbps", inline=True
                            )
                            await Logging.send_logs(channel, embed=embed, guild=guild)

                        if before.user_limit != after.user_limit:
                            embed.description = "**User Limit Changed**"
                            embed.add_field(
                                name="Before", value=before.user_limit, inline=True
                            )
                            embed.add_field(
                                name="After", value=after.user_limit, inline=True
                            )
                            await Logging.send_logs(channel, embed=embed, guild=guild)

                    if isinstance(before, discord.TextChannel):

                        if before.name != after.name:
                            embed.description = f"**Name Changed**"
                            embed.add_field(
                                name="Before", value=before.name, inline=True
                            )
                            embed.add_field(name="after", value=after.name, inline=True)
                            await Logging.send_logs(channel, embed=embed, guild=guild)

                        if before.topic != after.topic:
                            embed.description = "**Topic Changed**"
                            embed.add_field(
                                name="Before",
                                value=before.topic if before.topic else "No topic set",
                                inline=False,
                            )
                            embed.add_field(
                                name="After",
                                value=after.topic if after.topic else "No topic set",
                                inline=False,
                            )
                            await Logging.send_logs(channel, embed=embed, guild=guild)

                        if before.slowmode_delay != after.slowmode_delay:
                            embed.description = "**Slowmode Changed**"
                            embed.add_field(
                                name="Before",
                                value=f"{before.slowmode_delay} "
                                      f"second{'' if before.slowmode_delay == 1 else 's'}",
                                inline=True,
                            )
                            embed.add_field(
                                name="After",
                                value=f"{after.slowmode_delay} "
                                      f"second{'' if after.slowmode_delay == 1 else 's'}",
                                inline=True,
                            )
                            await Logging.send_logs(channel, embed=embed, guild=guild)

                        if before.nsfw != after.nsfw:
                            embed.description = f"**NSFW Changed:** {after.nsfw}"
                            await Logging.send_logs(channel, embed=embed, guild=guild)
                else:

                    if isinstance(before, discord.VoiceChannel):

                        if before.name != after.name:
                            log_send = (f"{logging_emotes['channelupdate']} **{before.name}**"
                                        f" has been renamed to **{after.name}**.")
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.bitrate != after.bitrate:
                            log_send = (f"{logging_emotes['channelupdate']} **{before.name}** bitrate has been "
                                        f"changed to ``{before.bitrate}``. It was ``{after.bitrate}``")
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.user_limit != after.user_limit:
                            log_send = (
                                f"{logging_emotes['channelupdate']} **{before.name}** user limit has been changed to "
                                f"``{after.user_limit}``. It was ``{before.user_limit}``"
                            )
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                    if isinstance(before, discord.TextChannel):

                        if before.name != after.name:
                            log_send = f"**Name Changed:**\n**Before:** {before.name}\n**After:** {after.name}"
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.topic != after.topic:
                            log_send = (
                                f"**Topic Changed:**\n"
                                f"**Before:** {before.topic if before.topic else 'No topic set'}\n"
                                f"**After:** {after.topic if after.topic else 'No topic set'}"
                            )
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.slowmode_delay != after.slowmode_delay:
                            log_send = (
                                f"**Slowmode Changed:**\n"
                                f"**Before:** {before.slowmode_delay} "
                                f"second{'' if before.slowmode_delay == 1 else 's'}\n"
                                f"**After:** {after.slowmode_delay} "
                                f"second{'' if after.slowmode_delay == 1 else 's'}"
                            )
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.nsfw != after.nsfw:
                            log_send = f"**NSFW Changed:** {after.nsfw}"
                            await Logging.send_logs(channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if not self.bot.is_ready():
            return
        try:
            guild = channel.guild
            log_channel, embed_enabled = await Logging.get_log_channel(self, "guild_channel", guild)

            if log_channel:
                if embed_enabled:

                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=guild.name, icon_url=avatar_check(self.bot.user))
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Channel-ID: {channel.id}")
                    embed.description = f"**Channel Deleted:** {channel.name}"
                    await Logging.send_logs(log_channel, embed=embed, guild=guild)

                else:
                    log_send = (f"{logging_emotes['channeldelete']} **{channel.name}** was deleted with the id:"
                                f" ``{channel.id}``.")
                    await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if not self.bot.is_ready():
            return
        try:
            guild = channel.guild
            log_channel, embed_enabled = await Logging.get_log_channel(self, "guild_channel", guild)
            if log_channel:
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=guild.name, icon_url=avatar_check(self.bot.user))
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Channel-ID: {channel.id}")
                    embed.description = f"**Channel Created:** {channel.name}"
                    await Logging.send_logs(log_channel, embed=embed, guild=guild)
                else:
                    log_send = (f"{logging_emotes['channelcreate']} **{channel.name}** has been created with the id"
                                f" ``{channel.id}``.")
                    await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if not self.bot.is_ready():
            return
        try:
            guild = role.guild
            log_channel, embed_enabled = await Logging.get_log_channel(self, "guild_channel", guild)
            if log_channel:
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=guild.name, icon_url=avatar_check(self.bot.user))
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Role-ID: {role.id}")
                    embed.description = f"**Role Deleted:** {role.name}"
                    await Logging.send_logs(log_channel, embed=embed, guild=guild)
                else:
                    log_send = f"{logging_emotes['roleremove']} **{role.name}** was deleted with the id ``{role.id}``."
                    await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if not self.bot.is_ready():
            return
        try:
            guild = role.guild
            log_channel, embed_enabled = await Logging.get_log_channel(self, "guild_channel", guild)
            if log_channel:
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=guild.name, icon_url=avatar_check(self.bot.user))
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Role-ID: {role.id}")
                    embed.description = f"**Role Created:** {role.name}"
                    await Logging.send_logs(log_channel, embed=embed, guild=guild)
                else:
                    log_send = f"{logging_emotes['rolecreate']} **{role.name}** was created with the id ``{role.id}``."
                    await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if not self.bot.is_ready():
            return
        try:
            guild = before.guild
            log_channel, embed_enabled = await Logging.get_log_channel(self, "guild_channel", guild)
            if log_channel:
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=before.name, icon_url=avatar_check(self.bot.user))
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Role-ID: {before.id}")
                    if before.name != after.name:
                        embed.description = f"**Name Changed:**"
                        embed.add_field(name="Before", value=before.name, inline=False)
                        embed.add_field(name="After", value=after.name, inline=False)
                        await Logging.send_logs(log_channel, embed=embed, guild=guild)

                    if before.hoist != after.hoist:
                        embed.description = f"**Hoisted:** {after.hoist}"
                        await Logging.send_logs(log_channel, embed=embed, guild=guild)

                    if before.colour != after.colour:
                        embed.description = f"**Colour Changed**"
                        embed.add_field(name="Before", value=before.colour, inline=True)
                        embed.add_field(name="After", value=after.colour, inline=True)
                        await Logging.send_logs(log_channel, embed=embed, guild=guild)

                    if before.mentionable != after.mentionable:
                        embed.description = f"**Mentionable:** {after.mentionable}"
                        await Logging.send_logs(log_channel, embed=embed, guild=guild)

                    if before.permissions != after.permissions:
                        before_permission = set(before.permissions)
                        after_permission = set(after.permissions)
                        true = after_permission - before_permission
                        paginator = commands.Paginator(
                            prefix="", suffix="", max_size=1024
                        )
                        paginator.add_line(
                            f"**Permission{'' if len(true) == 1 else 's'} Changed**"
                        )
                        paginator.add_line("\u200b")
                        for x in true:
                            paginator.add_line(f"``{x[0]}`` = {x[1]}\r\n")

                        for page in paginator.pages:
                            embed.description = page
                        await Logging.send_logs(log_channel, embed=embed, guild=guild)
                else:
                    if before.name != after.name:
                        log_send = f"{logging_emotes['roleupdate']} **{before.name}** role has been changed to **{after.name}**."
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

                    if before.hoist != after.hoist:
                        if after.hoist:
                            log_send = (f"{logging_emotes['roleupdate']} **{before.name}** role has been hoisted."
                                        f" It was not hoisted.")
                        else:
                            log_send = (f"{logging_emotes['roleupdate']} **{before.name}**"
                                        f"hoisting has been disabled. It was hoisted.")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

                    if before.colour != after.colour:
                        log_send = (f"{logging_emotes['roleupdate']} **{before.name}** role color has been changed to"
                                    f" ``{after.colour}``. It was ``{before.colour}``.")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

                    if before.mentionable != after.mentionable:
                        if after.mentionable:
                            log_send = (f"{logging_emotes['roleupdate']} **{before.name}** has been made mentionable."
                                        f" It was not mentionable.")
                        else:
                            log_send = (f"{logging_emotes['roleupdate']} **{before.name}** "
                                        f"has been made not mentionable. It was mentionable")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        if not self.bot.is_ready():
            return
        log_channel, embed_enabled = await Logging.get_log_channel(self, "guild_channel", guild)
        try:
            if log_channel:
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=guild, icon_url=icon_check(guild))
                    embed.timestamp = datetime.utcnow()
                    if before != after:
                        before_emote = set(before)
                        after_emote = set(after)
                        added = after_emote - before_emote
                        removed = before_emote - after_emote
                        for add in added:
                            embed.description = f"**Emote Added:** {add}"
                        for remove in removed:
                            embed.description = f"**Emote Removed:** {remove}"
                        await Logging.send_logs(log_channel, embed=embed, guild=guild)
                    else:
                        if before != after:
                            before_emote = set(before)
                            after_emote = set(after)
                            added = after_emote - before_emote
                            removed = before_emote - after_emote
                            log_send = None
                            for add in added:
                                log_send = f"{logging_emotes['emotecreate']} The emoji {add} has been added to the server."
                            for remove in removed:
                                log_send = f"{logging_emotes['emotecreate']} The emoji {remove} has been removed from the server."
                            if log_send is None:
                                return
                            await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if not self.bot.is_ready():
            return
        try:
            guild = before.guild
            log_channel, embed_enabled = await Logging.get_log_channel(self, "guild_channel", guild)
            if log_channel:
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=after, icon_url=icon_check(after))
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Guild-ID: {before.id}")

                    if before.name != after.name:
                        embed.description = "**Name Changed**"
                        embed.add_field(name="Before", value=before.name, inline=False)
                        embed.add_field(name="After", value=after.name, inline=False)
                        await Logging.send_logs(log_channel, embed=embed, guild=guild)

                    if before.region != after.region:
                        embed.description = "**Region Changed**"
                        embed.add_field(
                            name="Before", value=before.region, inline=False
                        )
                        embed.add_field(name="After", value=after.region, inline=False)
                        await Logging.send_logs(log_channel, embed=embed, guild=guild)

                    if before.icon_url != after.icon_url:
                        embed.description = f"**Icon Changed"
                        if before.icon_url:
                            embed.add_field(
                                name="Before",
                                value=f"``{icon_check(before)}``",
                                inline=False,
                            )
                        if after.icon_url:
                            embed.add_field(
                                name="After",
                                value=f"``{icon_check(after)}``",
                                inline=False,
                            )
                            embed.set_image(url=icon_check(after))

                        await Logging.send_logs(log_channel, embed=embed, guild=guild)

                else:
                    if before.name != after.name:
                        log_send = (f"{logging_emotes['infoupdate']} **{before.guild.name}** "
                                    f"has been changed to ``{after.guild.name}``.")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

                    if before.region != after.region:
                        log_send = (f"{logging_emotes['infoupdate']} **{before.guild.name}** region has "
                                    f"been updated to ``{after.region}``. Was ``{before.region}``")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

                    if before.icon_url != after.icon_url:
                        log_send = (
                            f"{logging_emotes['infoupdate']} {before.guild.name} **Icon Changed:**\n**Before:** "
                            f"{before.icon_url if before.icon_url else 'None'}\n"
                            f"**After:** {after.icon_url if after.icon_url else 'None'}")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not self.bot.is_ready():
            return
        try:
            guild = member.guild
            log_channel, embed_enabled = await Logging.get_log_channel(self, "voice_channel", guild)
            if log_channel:
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=member, icon_url=avatar_check(member))
                    embed.timestamp = datetime.utcnow()
                    if before.channel != after.channel:
                        if before.channel is None:
                            embed.description = f"**Joined a Channel:** {after.channel}"
                            await Logging.send_logs(log_channel, embed=embed, guild=guild)
                        elif after.channel is None:
                            embed.description = f"**Left a Channel:** {before.channel}"
                            await Logging.send_logs(log_channel, embed=embed, guild=guild)
                        else:
                            embed.description = f"**Switched Channels**"
                            embed.add_field(
                                name="Before", value=before.channel, inline=True
                            )
                            embed.add_field(
                                name="After", value=after.channel, inline=True
                            )
                            await Logging.send_logs(log_channel, embed=embed, guild=guild)
                else:
                    if before.channel != after.channel:
                        if before.channel is None:
                            log_send = f"**{member.name}** Joined a channel: **{after.channel}**"
                            await Logging.send_logs(log_channel, message=log_send, guild=guild)
                        elif after.channel is None:
                            log_send = f"**{member.name}** Left a channel: **{before.channel}**"
                            await Logging.send_logs(log_channel, message=log_send, guild=guild)
                        else:
                            log_send = (
                                f"**{member.name}** Switched channels:\n"
                                f"Before: **{before.channel}**\n"
                                f"After: **{after.channel}**"
                            )
                            await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    async def on_user_update(self, before, after):
        if not self.bot.is_ready():
            return
        try:
            # Loops through bot guilds and acquires a guild object
            for guild in self.bot.guilds:
                # checks for member in guild
                member = guild.get_member(before.id)
                if member:
                    log_channel, embed_enabled = await Logging.get_log_channel(self, "member_channel", guild)
                    if log_channel:
                        if embed_enabled:
                            embed = discord.Embed(color=self.bot.color)
                            embed.set_author(
                                name=before, icon_url=avatar_check(before)
                            )
                            embed.timestamp = datetime.utcnow()
                            embed.set_footer(text=f"Member-ID: {before.id}")

                            if before.avatar_url != after.avatar_url:
                                embed.description = (
                                    f"{after.mention} **changed their avatar**"
                                )
                                embed.add_field(
                                    name="Before",
                                    value=f"``{avatar_check(before)}``",
                                    inline=False,
                                )
                                embed.add_field(
                                    name="After",
                                    value=f"``{avatar_check(after)}``",
                                    inline=False,
                                )
                                embed.set_image(url=avatar_check(after))
                                await Logging.send_logs(log_channel, embed=embed, guild=guild)

                            if before.name != after.name:
                                if before.discriminator != after.discriminator:
                                    embed.description = f"{after.mention} **changed their name#discrim**"
                                    embed.add_field(
                                        name="Before",
                                        value=f"{before.name}#{before.discriminator}",
                                        inline=False,
                                    )
                                    embed.add_field(
                                        name="After",
                                        value=f"{after.name}#{after.discriminator}",
                                        inline=False,
                                    )
                                    await Logging.send_logs(log_channel, embed=embed, guild=guild)

                                else:
                                    embed.description = (
                                        f"{after.mention} **changed their name**"
                                    )
                                    embed.add_field(
                                        name="Before",
                                        value=before.name,
                                        inline=False,
                                    )
                                    embed.add_field(
                                        name="After", value=after.name, inline=False
                                    )
                                    await Logging.send_logs(log_channel, embed=embed, guild=guild)
                            elif before.discriminator != after.discriminator:
                                embed.description = (
                                    f"{after.mention} **changed their discrim**"
                                )
                                embed.add_field(
                                    name="Before",
                                    value=before.discriminator,
                                    inline=False,
                                )
                                embed.add_field(
                                    name="After",
                                    value=after.discriminator,
                                    inline=False,
                                )
                                await Logging.send_logs(log_channel, embed=embed, guild=guild)
                        else:
                            if before.avatar_url != after.avatar_url:
                                log_send = (
                                    f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their avatar.\n"
                                    f"**New Avatar:** {after.avatar_url}\n"
                                    f"**Old Avatar:** ``{before.avatar_url}``"
                                )
                                await Logging.send_logs(log_channel, message=log_send, guild=guild)
                            if before.name != after.name:
                                if before.discriminator != after.discriminator:
                                    log_send = (
                                        f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their name to **{after.name}#{after.discriminator}**"
                                    )
                                    await Logging.send_logs(log_channel, message=log_send, guild=guild)
                                else:
                                    log_send = (
                                        f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their name to **{after.name}#{after.discriminator}**")
                                    await Logging.send_logs(log_channel, message=log_send, guild=guild)
                            elif before.discriminator != after.discriminator:
                                log_send = (
                                    f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their discriminator.\n"
                                    f"**New Discriminator:** {after.discriminator}\n"
                                    f"**Old Discriminator:** ``{before.discriminator}``"
                                )
                                await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # noinspection PyCallByClass
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not self.bot.is_ready():
            return
        try:
            async with self.bot.pool.acquire() as db:
                # Automonus Premuim adding
                role_diff = diff(before.roles, after.roles)
                if role_diff:
                    if after.guild.id == 346892627108560901:
                        api_key_role = after.guild.get_role(590306580667564055)
                        premium_tier_1 = after.guild.get_role(418539980403638282)
                        premium_tier_2 = after.guild.get_role(459143362080145408)
                        if (
                                api_key_role in after.roles
                                and api_key_role not in before.roles
                        ):
                            await give_api_permissions(db, after, True)
                        elif (
                                api_key_role in before.roles
                                and api_key_role not in after.roles
                        ):
                            await give_api_permissions(db, after, False)
                        if (
                                premium_tier_1 in after.roles
                                and premium_tier_1 not in before.roles
                        ) or (
                                premium_tier_2 in after.roles
                                and premium_tier_2 not in before.roles
                        ):
                            await give_premium(db, after, True)
                        elif (
                                premium_tier_1 in before.roles
                                and premium_tier_1 not in after.roles
                        ) or (
                                premium_tier_2 in before.roles
                                and premium_tier_2 not in after.roles
                        ):
                            await give_premium(db, after, False)
                guild = before.guild
                log_channel, embed_enabled = await Logging.get_log_channel(self, "member_channel", guild)
                if log_channel:
                    if embed_enabled:
                        embed = discord.Embed(colour=self.bot.color)
                        embed.set_author(name=before, icon_url=avatar_check(before))
                        embed.timestamp = datetime.utcnow()
                        embed.set_footer(text=f"Member-ID: {before.id}")
                        if before.nick != after.nick:
                            embed.description = (
                                f"{after.mention} **changed their nickname**"
                            )
                            embed.add_field(
                                name="Before", value=before.nick, inline=False
                            )
                            embed.add_field(
                                name="After", value=after.nick, inline=False
                            )
                            await Logging.send_logs(log_channel, embed=embed, guild=guild)
                        if before.roles != after.roles:
                            before_roles = set(before.roles)
                            after_roles = set(after.roles)
                            added = after_roles - before_roles
                            removed = before_roles - after_roles
                            for add in added:
                                embed.description = f"**Role added:** {add.name}"
                            for remove in removed:
                                embed.description = (
                                    f"**Role removed:** {remove.name}"
                                )
                            await Logging.send_logs(log_channel, embed=embed, guild=guild)

                        else:
                            if before.nick != after.nick:
                                log_send = (
                                    f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their nickname to **{after.nick}**.\n"
                                    f"Their previous nickname was "
                                    f"``{f'{before.nick}' if before.nick is not None else 'was not configured'}``.")
                                await Logging.send_logs(log_channel, message=log_send, guild=guild)
                            if before.roles != after.roles:
                                before_roles = set(before.roles)
                                after_roles = set(after.roles)
                                added = after_roles - before_roles
                                removed = before_roles - after_roles
                                for add in added:
                                    log_send = (
                                        f"{logging_emotes['memberupdate']} **{add.name}** was added to **{before}**(``{before.id}``)."
                                    )
                                for remove in removed:
                                    log_send = (
                                        f"{logging_emotes['memberupdate']} **{remove.name}** was removed from **{before}**(``{before.id}``)."
                                    )
                                await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id is None:
            return
        async with self.bot.pool.acquire() as db:
            check = await db.fetchrow(
                """
                SELECT role_id 
                  FROM botsettings_react_roles
                 WHERE guild_id = $1 
                   AND channel_id = $2 
                   AND message_id = $3 
                   AND emoji_id = $4""",
                payload.guild_id,
                payload.channel_id,
                payload.message_id,
                payload.emoji.name,
            )
            if check is None:
                return
            if check:
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                if member.bot:
                    return
                role = discord.utils.get(guild.roles, id=check[0])
                if role is None:
                    return
                if role in member.roles:
                    return await member.remove_roles(role, reason="Reaction Roles")
                await member.add_roles(role, reason="Reaction Roles")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.guild_id is None:
            return
        async with self.bot.pool.acquire() as db:
            check = await db.fetchrow(
                """
                SELECT role_id 
                  FROM botsettings_react_roles
                 WHERE guild_id = $1 
                   AND channel_id = $2 
                   AND message_id = $3 
                   AND emoji_id = $4""",
                payload.guild_id,
                payload.channel_id,
                payload.message_id,
                payload.emoji.name,
            )
            if check is None:
                return
            if check:
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                if member.bot:
                    return
                role = discord.utils.get(guild.roles, id=check[0])
                if role is None:
                    return
                await member.remove_roles(role, reason="Reaction Roles")


def setup(bot):
    bot.add_cog(Members(bot))
