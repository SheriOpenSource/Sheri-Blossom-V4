import re
from datetime import datetime

import discord
from discord.ext import commands

from Checks.bot_checks import can_send, can_embed, can_react
from Formats.formats import avatar_check, icon_check
from Functions import catching, away
from Functions.logging import Logging
from Lines.custom_emotes import logging_emotes


# noinspection PyCallByClass,PyCallByClass,PyCallByClass
class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.is_ready():
            try:
                # if not message.author.bot:
                # await add_user(self.bot.pool, message.author)
                self.bot.counter["messages_seen"] += 1
                if "@everyone" in message.content:
                    self.bot.counter["@everyones_seen"] += 1
                if "@here" in message.content:
                    self.bot.counter["@here_seen"] += 1
                ctx = await self.bot.get_context(message)
                if not isinstance(message.channel, discord.DMChannel):
                    await catching.initiate_catch(self, ctx)
                    await away.away_check(self.bot, ctx, message)
                    # await add_guild(self.bot.pool, message.guild)
                    # await Mod.auto_mod(self.bot, message)
            except Exception as e:
                self.bot.sentry.capture_exception(e)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        if not self.bot.is_ready():
            return
        guild = self.bot.get_guild(payload.guild_id)
        channel_bulked = self.bot.get_channel(payload.channel_id)
        try:
            if isinstance(channel_bulked, discord.TextChannel):
                guild_data = await Logging.log_channel(self, "message_channel", guild)
                channel = guild_data[0]
                embed_enabled = guild_data[1]
                if channel:
                    count = len(payload.message_ids)
                    # Is embed enabled?
                    if embed_enabled:

                        embed = discord.Embed(colour=self.bot.color).set_author(
                            name="Purge Detected", icon_url=icon_check(guild)
                        )
                        embed.timestamp = datetime.utcnow()
                        embed.description = (
                            f"{count} messages deleted in {channel_bulked.mention}"
                        )

                        await Logging.send_logs(channel, embed=embed, guild=guild)
                    else:
                        message = (
                            f"```Bulk Message Delete```"
                            f'{logging_emotes["messagedelete"]} {count} '
                            f'messages have been deleted from {channel_bulked.mention}.')
                        await Logging.send_logs(channel, message=message, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not self.bot.is_ready():
            return
        try:
            if message.author.bot:
                return
            guild_data = await Logging.log_channel(self, "message_channel", message.guild)
            channel = guild_data[0]
            embed_enabled = guild_data[1]
            if channel:
                # Edits the message splitting the extra and shortening it while adding ... to the end.
                raw_content = message.content
                content = (
                    (raw_content[:1000] + "...")
                    if len(raw_content) >= 1000
                    else raw_content
                )
                if embed_enabled:
                    embed = discord.Embed(colour=self.bot.color).set_author(
                        name=message.author,
                        icon_url=avatar_check(message.author),
                    )
                    if content != "":
                        embed.description = (
                            f"**Messaged Deleted in** {message.channel.mention}"
                        )
                        embed.add_field(
                            name="Message:", value=content, inline=False
                        )
                    embed.add_field(
                        name="Additional Information",
                        value=f"**Channel-ID:** {message.channel.id}\n**Message-ID:** {message.id}",
                        inline=False,
                    )
                    embed.timestamp = datetime.utcnow()
                    embed.set_footer(text=f"Author-ID: {message.author.id}")
                    await Logging.send_logs(channel, embed=embed, guild=message.guild)
                else:
                    cleaned_content = re.sub(r'@(everyone|here|[!&]?[0-9]{17,21})', '@\u200b\\1', content)
                    log_msg = (
                        f"```Message Deleted```"
                        f"{logging_emotes['messagedelete']} **{message.author}**'s message has been deleted in {message.channel.mention}.\n"
                        f"Their message was: {cleaned_content}")
                    await Logging.send_logs(channel, message=log_msg, guild=message.guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not self.bot.is_ready():
            return
        try:
            if before.author.bot:
                return
            if before.content == after.content:
                return
            if isinstance(before.channel, discord.TextChannel):
                guild_data = await Logging.log_channel(self, "message_channel", before.guild)
                channel = guild_data[0]
                embed_enabled = guild_data[1]
                if channel:
                    # Edits before content to split and add ... to the end.
                    raw_before_content = before.content
                    before_content = (
                        (raw_before_content[:1000] + "...")
                        if len(raw_before_content) >= 1000
                        else raw_before_content
                    )
                    # Edits after content to split and add ... to the end.
                    raw_after_content = after.content
                    after_content = (
                        (raw_after_content[:1000] + "...")
                        if len(raw_after_content) >= 1000
                        else raw_after_content
                    )

                    if embed_enabled:
                        embed = discord.Embed(colour=self.bot.color).set_author(
                            name=before.author.name,
                            icon_url=avatar_check(before.author),
                        )
                        embed.description = (
                            f"**Messaged edited in** {before.channel.mention} "
                            f"[Jump to Message]({after.jump_url})"
                        )
                        if before_content != "":
                            embed.add_field(
                                name="Before", value=before_content, inline=False
                            )
                        else:
                            embed.add_field(
                                name="Before", value="None", inline=False
                            )
                        if after_content != "":
                            embed.add_field(
                                name="After", value=after_content, inline=False
                            )
                        else:
                            embed.add_field(
                                name="After", value="None", inline=False
                            )
                        embed.add_field(
                            name="Additional Information",
                            value=f"**Channel-ID**: {before.channel.id}\n**Message-ID:** {before.id}",
                            inline=False,
                        )
                        embed.timestamp = datetime.utcnow()
                        embed.set_footer(text=f"Author-ID: {before.author.id}")
                        await Logging.send_logs(channel, embed=embed, guild=before.guild)
                    else:
                        cleaned_content_before = re.sub(r'@(everyone|here|[!&]?[0-9]{17,21})', '@\u200b\\1',
                                                        before_content)
                        cleaned_content_after = re.sub(r'@(everyone|here|[!&]?[0-9]{17,21})', '@\u200b\\1',
                                                       after_content)
                        message = (
                            f"```Message Edited```"
                            f"{logging_emotes['messageupdate']} **{before.author}** has updated their message in {before.channel.mention}.\n"
                            f"**Before:** {cleaned_content_before}\n\n"
                            f"**After:** {cleaned_content_after}"
                        )
                        await Logging.send_logs(channel, message=message, guild=before.guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)
        if not self.bot.is_ready() or after.author.bot:
            return
        # await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if self.bot.is_ready():
            self.bot.counter["commands_processed"] += 1
            self.bot.counter[ctx.command.qualified_name] += 1
            try:
                self.bot.log.info(
                    f"[Commands Manager] - [{ctx.guild.name}] - ({ctx.author}): {ctx.message.clean_content}"
                )
            except AttributeError:
                self.bot.log.info(
                    f"[Commands Manager] - Private message({ctx.author}): {ctx.message.clean_content}"
                )
            if ctx.command is None:
                return
            if isinstance(ctx.channel, discord.abc.GuildChannel):
                if not can_send(ctx) or not can_embed(ctx):
                    if can_react(ctx):
                        return await ctx.message.add_reaction("❌")
                    try:
                        return await ctx.author.send(
                            "Missing permissions to `send_messages` and/or `embed_links`!"
                        )
                    except discord.Forbidden:
                        return self.bot.log.error(
                            "Could not respond to command, all checks failed!"
                        )


def setup(bot):
    bot.add_cog(Messages(bot))
