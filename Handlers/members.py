from datetime import datetime

import discord
from discord.ext import commands

from Database.transactions import give_api_permissions, give_premium
from Formats.formats import avatar_check
from Functions.dehoist import auto_anti_hoist_zalgo
from Functions.logging import Logging
from Lines.custom_emotes import logging_emotes


def diff(li1, li2):
    return [i for i in li1 if i not in li2] + [i for i in li2 if i not in li1]


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not self.bot.is_ready():
            return
        try:
            if payload.guild_id:
                check = await self.bot.pool.fetchrow(
                    """
                    SELECT role_id 
                      FROM botsettings_reactroles
                     WHERE guild_id = $1 
                       AND channel_id = $2 
                       AND message_id = $3 
                       AND emoji_id = $4""",
                    payload.guild_id,
                    payload.channel_id,
                    payload.message_id,
                    payload.emoji.name,
                )
                if check:
                    guild = self.bot.get_guild(payload.guild_id)
                    member = guild.get_member(payload.user_id)
                    if not member.bot:
                        role = discord.utils.get(guild.roles, id=check[0])
                        if role in member.roles:
                            return await member.remove_roles(role, reason="Reaction Roles")
                        await member.add_roles(role, reason="Reaction Roles")
        except discord.Forbidden:
            return 
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not self.bot.is_ready():
            return
        try:
            if payload.guild_id:
                async with self.bot.pool.acquire() as db:
                    check = await db.fetchrow(
                        """
                        SELECT role_id 
                          FROM botsettings_reactroles
                         WHERE guild_id = $1 
                           AND channel_id = $2 
                           AND message_id = $3 
                           AND emoji_id = $4""",
                        payload.guild_id,
                        payload.channel_id,
                        payload.message_id,
                        payload.emoji.name,
                    )
                    if check:
                        guild = self.bot.get_guild(payload.guild_id)
                        member = guild.get_member(payload.user_id)
                        if member.bot:
                            return
                        role = discord.utils.get(guild.roles, id=check[0])
                        if role is None:
                            return
                        await member.remove_roles(role, reason="Reaction Roles")
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    ####################################################################################################################
    #                                   Member Updates
    ####################################################################################################################
    async def on_member_update(self, before, after):
        if self.bot.is_ready():
            try:
                await auto_anti_hoist_zalgo(self, after, before.guild)
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
                    ########################################
                    #       Member Logs
                    ########################################
                    if before.guild:
                        guild_data = await Logging.log_channel(self, "message_channel", before.guild)
                        channel = guild_data[0]
                        embed_enabled = guild_data[1]
                        if channel:
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
                                    await Logging.send_logs(channel, embed=embed, guild=before.guild)

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
                                    await Logging.send_logs(channel, embed=embed, guild=before.guild)
                            else:
                                if before.nick != after.nick:
                                    log_send = (
                                        f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their nickname to **{after.nick}**.\n"
                                        f"Their previous nickname was "
                                        f"``{f'{before.nick}' if before.nick is not None else 'was not configured'}``.")
                                    await Logging.send_logs(channel, message=log_send, guild=before.guild)

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
                                    await Logging.send_logs(channel, message=log_send, guild=before.guild)

            except Exception as e:
                self.bot.sentry.capture_exception(e)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if not self.bot.is_ready():
            return
        try:
            # Loops through bot guilds and acquires a guild object
            for guild in self.bot.guilds:
                # checks for member in guild
                member = guild.get_member(before.id)
                if member:
                    guild_data = await Logging.log_channel(self, "member_channel", guild)
                    channel = guild_data[0]
                    embed_enabled = guild_data[1]
                    if channel:
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
                                # embed.add_field(
                                #    name="Before",
                                #    value=f"``{avatar_check(before)}``",
                                #    inline=False,
                                # )
                                embed.add_field(
                                    name="New avatar URL:",
                                    value=f"``{avatar_check(after)}``",
                                    inline=False,
                                )
                                embed.set_image(url=avatar_check(after))
                                await Logging.send_logs(channel, embed=embed, guild=guild)

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
                                    await Logging.send_logs(channel, embed=embed, guild=guild)

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
                                    await Logging.send_logs(channel, embed=embed, guild=guild)
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
                                await Logging.send_logs(channel, embed=embed, guild=guild)
                        else:
                            if before.avatar_url != after.avatar_url:
                                log_send = (
                                    f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their avatar.\n"
                                    f"**New Avatar:** {after.avatar_url}\n"
                                    # f"**Old Avatar:** ``{before.avatar_url}``"
                                )
                                await Logging.send_logs(channel, message=log_send, guild=guild)
                            if before.name != after.name:
                                if before.discriminator != after.discriminator:
                                    log_send = (
                                        f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their name to **{after.name}#{after.discriminator}**"
                                    )
                                    await Logging.send_logs(channel, message=log_send, guild=guild)
                                else:
                                    log_send = (
                                        f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their name to **{after.name}#{after.discriminator}**")
                                    await Logging.send_logs(channel, message=log_send, guild=guild)
                            elif before.discriminator != after.discriminator:
                                log_send = (
                                    f"{logging_emotes['memberupdate']} **{before}**(``{before.id}``) has changed their discriminator.\n"
                                    f"**New Discriminator:** {after.discriminator}\n"
                                    f"**Old Discriminator:** ``{before.discriminator}``"
                                )
                                await Logging.send_logs(channel, message=log_send, guild=guild)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not self.bot.is_ready():
            return
        try:
            guild = member.guild
            if guild is not None:
                guild_data = await Logging.log_channel(self, "voice_channel", guild)
                log_channel = guild_data[0]
                embed_enabled = guild_data[1]
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


def setup(bot):
    bot.add_cog(Members(bot))
