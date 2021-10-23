from datetime import datetime

import discord
from discord.ext import commands

from Formats.formats import avatar_check, icon_check
from Functions.logging import Logging
from Lines.custom_emotes import logging_emotes


# noinspection PyCallByClass
class Guildevents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ####################################################################################################################
    #                               Guild Channel Log Events
    ####################################################################################################################

    # Guild EMBEDS rewrite = Not Started
    # Guild Messages rewrite = Not Started
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        try:
            guild = before.guild
            guild_data = await Logging.log_channel(self, "guild_channel", before.guild)
            channel = guild_data[0]
            embed_enabled = guild_data[1]
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
                            log_send = (f"```Voice Channel Updated```"
                                        f"{logging_emotes['channelupdate']} **{before.name}**"
                                        f" has been renamed to **{after.name}**.")
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.bitrate != after.bitrate:
                            log_send = (f"Voice Channel Updated```"
                                        f"{logging_emotes['channelupdate']} **{before.name}** bitrate has been "
                                        f"changed to ``{before.bitrate}``. It was ``{after.bitrate}``")
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.user_limit != after.user_limit:
                            log_send = (f"```Voice Channel Updated```"
                                        f"{logging_emotes['channelupdate']} **{before.name}** user limit has been changed to "
                                        f"``{after.user_limit}``. It was ``{before.user_limit}``"
                            )
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                    if isinstance(before, discord.TextChannel):

                        if before.name != after.name:
                            log_send = (
                                f"```Text Channel Updated```"
                                f"**Name Changed:**\n**Before:** {before.name}\n**After:** {after.name}"
                            )
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.topic != after.topic:
                            log_send = (
                                f"```Text Channel Updated```"
                                f"**Topic Changed:**\n"
                                f"**Before:** {before.topic if before.topic else 'No topic set'}\n"
                                f"**After:** {after.topic if after.topic else 'No topic set'}"
                            )
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.slowmode_delay != after.slowmode_delay:
                            log_send = (
                                f"```Text Channel Updated```"
                                f"**Slowmode Changed:**\n"
                                f"**Before:** {before.slowmode_delay} "
                                f"second{'' if before.slowmode_delay == 1 else 's'}\n"
                                f"**After:** {after.slowmode_delay} "
                                f"second{'' if after.slowmode_delay == 1 else 's'}"
                            )
                            await Logging.send_logs(channel, message=log_send, guild=guild)

                        if before.nsfw != after.nsfw:
                            log_send = (
                                f"```Text Channel Updated```"
                                f"**NSFW Status Changed:** {after.nsfw}"
                            )
                            await Logging.send_logs(channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # Guild EMBEDS rewrite = Not Started
    # Guild Messages rewrite = Finished
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        try:
            guild = channel.guild
            guild_data = await Logging.log_channel(self, "guild_channel", channel.guild)
            log_channel = guild_data[0]
            embed_enabled = guild_data[1]
            if log_channel:
                if embed_enabled:

                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=guild.name, icon_url=avatar_check(self.bot.user))
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Channel-ID: {channel.id}")
                    embed.description = f"**Channel Deleted:** {channel.name}"
                    await Logging.send_logs(log_channel, embed=embed, guild=channel.guild)

                else:
                    log_send = (f"```Channel Deleted```"
                                f"{logging_emotes['channeldelete']} **{channel.name}** was deleted with the id:"
                                f" ``{channel.id}``.")
                    await Logging.send_logs(log_channel, message=log_send, guild=channel.guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # Guild EMBEDS rewrite = Not Started
    # Guild Messages rewrite = Finished
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if not self.bot.is_ready():
            return
        try:
            guild = channel.guild
            guild_data = await Logging.log_channel(self, "guild_channel", channel.guild)
            log_channel = guild_data[0]
            embed_enabled = guild_data[1]
            if log_channel:
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=guild.name, icon_url=avatar_check(self.bot.user))
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Channel-ID: {channel.id}")
                    embed.description = f"**Channel Created:** {channel.name}"
                    await Logging.send_logs(log_channel, embed=embed, guild=channel.guild)
                else:
                    log_send = (f"```Channel Created```"
                                f"{logging_emotes['channelcreate']} **{channel.name}** has been created with the id"
                                f" ``{channel.id}``.")
                    await Logging.send_logs(log_channel, message=log_send, guild=channel.guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    ####################################################################################################################
    #                               Guild Channel Role Events
    ####################################################################################################################

    # Guild EMBEDS rewrite = Not Started
    # Guild Messages rewrite = Finished
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        try:
            guild = role.guild
            guild_data = await Logging.log_channel(self, "guild_channel", guild)
            log_channel = guild_data[0]
            embed_enabled = guild_data[1]
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

    # Guild EMBEDS rewrite = Not Started
    # Guild Messages rewrite = Finished
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        try:
            guild = role.guild
            guild_data = await Logging.log_channel(self, "guild_channel", guild)
            log_channel = guild_data[0]
            embed_enabled = guild_data[1]
            if log_channel:
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color)
                    embed.set_author(name=guild.name, icon_url=avatar_check(self.bot.user))
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Role-ID: {role.id}")
                    embed.description = f"**Role Created:** {role.name}"
                    await Logging.send_logs(log_channel, embed=embed, guild=guild)
                else:
                    log_send = (
                        f"```Role Created```"
                        f"{logging_emotes['rolecreate']} **{role.name}** was created with the id ``{role.id}``."
                        )
                    await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except TypeError:
            return
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    # Guild EMBEDS rewrite = Not Started
    # Guild Messages rewrite = Finished
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        try:
            guild = before.guild
            guild_data = await Logging.log_channel(self, "guild_channel", before.guild)
            log_channel = guild_data[0]
            embed_enabled = guild_data[1]
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
                        log_send = (f"```Role Updated```"
                                    f"{logging_emotes['roleupdate']} **{before.name}** role has been changed to **{after.name}**.")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

                    if before.hoist != after.hoist:
                        if after.hoist:
                            log_send = (f"{logging_emotes['roleupdate']} **{before.name}** role has been hoisted. "
                                        f"Members with this role will now display separately in the member list.")
                        else:
                            log_send = (f"```Role Updated```"
                                        f"{logging_emotes['roleupdate']} **{before.name}** "
                                        f"role hoisting has been disabled. This role will no longer display its members separately in the member list.")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

                    if before.colour != after.colour:
                        log_send = (f"```Role Updated```"
                                    f"{logging_emotes['roleupdate']} **{before.name}** role color has been changed to"
                                    f" ``{after.colour}``. It was ``{before.colour}``.")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

                    if before.mentionable != after.mentionable:
                        if after.mentionable:
                            log_send = (f"```Role Updated```"
                                        f"{logging_emotes['roleupdate']} **{before.name}** has been made mentionable. "
                                        f"Members are now able to mention this role.")
                        else:
                            log_send = (f"```Role Updated```"
                                        f"{logging_emotes['roleupdate']} **{before.name}** "
                                        f"has been made not mentionable. It was mentionable")
                        await Logging.send_logs(log_channel, message=log_send, guild=guild)

        except Exception as e:
            self.bot.sentry.capture_exception(e)

    ####################################################################################################################
    #                                  Guild emoji updates
    ####################################################################################################################
    # Guild EMBEDS rewrite = Not Started
    # Guild Messages rewrite = Finished
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        guild_data = await Logging.log_channel(self, "guild_channel", guild)
        log_channel = guild_data[0]
        embed_enabled = guild_data[1]
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
                                log_send = (f"```Emoji Added```"
                                            f"{logging_emotes['emotecreate']} The emoji {add} has been added to the server.")
                            for remove in removed:
                                log_send = (f"```Emoji Removed```"
                                            f"{logging_emotes['emotecreate']} The emoji {remove} has been removed from the server.")
                            if log_send is None:
                                return
                            await Logging.send_logs(log_channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    async def on_member_ban(self, guild, member):
        channel = self.bot.get_channel(651774871763812392)
        await channel.send()

    async def on_member_unban(self, guild, member):
        channel = self.bot.get_channel(651774871763812392)
        await channel.send(str(member))


def setup(bot):
    bot.add_cog(Guildevents(bot))
