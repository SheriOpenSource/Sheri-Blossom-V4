import re
from datetime import datetime, timedelta
from random import choice

import discord
import pytz
from discord.ext import commands, tasks
from sentry_sdk import capture_exception

from API.API import Retrieval as Get
from Checks.bot_checks import (
    check_hierarchy,
    can_embed,
    can_send,
    can_react,
    can_manage_user,
    can_external_react,
    can_delete)
from Checks.permissions import can_ban
from Formats.formats import avatar_check
from Functions.core import do_removal, send_message
from Functions.logging import Logging
from Lines.misc_functions import get as get_list


# TODO Add Channel Lock <- Elaborate? Lock how? Lock what?


# noinspection PyCallByClass
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_temp.start()

    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def warn(self, ctx, member: discord.Member = None, *, reason="None given"):
        if member is None:
            msg = (
                "**Description:** Warn a member\n"
                "**Cooldown:** 3 seconds\n"
                f"**Usage:** **fur**warn [member] [reason]\n"
                f"**Example:** **fur**warn @{ctx.guild.owner.name} shiposting old memes"
            )
            embed = discord.Embed(
                color=self.bot.info_color,
                title=f"Command: **fur**warn",
                description=msg,
            )
            return await ctx.send(embed=embed)
        if member == self.bot.user:
            return await ctx.send("LOL! You can't make me warn myself.")
        elif member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(
                f"Unable to warn {member}. They're higher than my highest role."
            )
        else:
            await ctx.message.delete()
            async with self.bot.pool.acquire() as db:
                await db.execute(
                    """INSERT INTO botsettings_infraction
                                 (type, reason, guild_id, member_id, member_id_only, moderator_id, incident_date) VALUES
                                 ($1, $2, $3, $4, $5, $6, $7)""",
                    "warning",
                    reason,
                    ctx.guild.id,
                    member.id,
                    member.id,
                    ctx.author.id,
                    datetime.utcnow(),
                )
                warning_count = await db.fetchval(
                    """SELECT count(*) FROM botsettings_infraction
                                                  WHERE member_id=$1 AND type='warning'""",
                    member.id,
                )
                guild_info = await db.fetchrow(
                    "SELECT moderation_channel, logs_embed, logs_enabled FROM botsettings_guild WHERE id=$1",
                    ctx.guild.id,
                )
                if guild_info["logs_enabled"]:
                    embed = discord.Embed(
                        title=f":warning: {member.display_name} was warned :warning:",
                        color=self.bot.warning_color,
                        timestamp=ctx.message.created_at,
                    )
                    embed.set_footer(
                        text=f"New action by {ctx.author.display_name}",
                        icon_url=avatar_check(ctx.author),
                    )
                    embed.add_field(name="User", value=str(member), inline=True)
                    embed.add_field(
                        name="Display Name", value=member.display_name, inline=True
                    )
                    embed.add_field(
                        name="Moderator", value=ctx.author.display_name, inline=True
                    )
                    embed.add_field(
                        name="Total Warnings", value=warning_count, inline=True
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    embed.set_thumbnail(url=avatar_check(member))
                    if guild_info["logs_embed"]:
                        try:
                            await self.bot.get_channel(
                                guild_info["moderation_channel"]
                            ).send(embed=embed)
                        except AttributeError:
                            await ctx.send("You have Log Embed Enabled for moderation, but no channel was specified!")
                        finally:
                            pass
                    else:
                        try:
                            await self.bot.get_channel(
                                guild_info["moderation_channel"]
                            ).send(
                                f"{ctx.author.mention} warned {member.mention}\n"
                                f"Reason: {reason}\n"
                                f"Total warnings: {warning_count}"
                            )
                        except AttributeError:
                            await send_message(ctx, message="You have Logs Enabled for moderation, but no channel was specified!")
                        finally:
                            pass
                await send_message(
                    ctx, message=f"_{member.mention} has been warned!_", delete_delay=10
                )
                try:
                    await member.send(
                        f"You have received a warning in {ctx.message.guild.name}\n"
                        f"Warning: {reason}\n"
                        f"You now have {warning_count} warnings."
                    )
                except discord.HTTPException:
                    pass

    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def clearwarn(self, ctx, member: discord.Member = None):
        if member is None:
            msg = (
                "**Description:** Clears warnings from a member\n"
                "**Cooldown:** 3 seconds\n"
                f"**Usage:** **fur**clearwarn [member]\n"
                f"**Example:** **fur**clearwarn @{ctx.guild.owner.name}"
            )
            embed = discord.Embed(
                color=self.bot.info_color,
                title=f"Command: **fur**clearwarn",
                description=msg,
            )
            return await ctx.send(embed=embed)
        await ctx.message.delete()
        async with self.bot.pool.acquire() as db:
            warn_count = await db.fetchval(
                """SELECT count(*) FROM botsettings_infraction WHERE
                                            member_id=$1 AND guild_id=$2""",
                member.id,
                ctx.guild.id,
            )
            await db.execute(
                "DELETE FROM botsettings_infraction WHERE member_id=$1 AND guild_id=$2",
                member.id,
                ctx.guild.id,
            )
            await ctx.send(
                f"Removed {warn_count if warn_count else '0'} warnings from "
                f"{member.mention} in {ctx.guild.name}.",
                delete_after=5,
            )
            guild_info = await db.fetchrow(
                "SELECT moderation_channel, logs_embed, logs_enabled FROM botsettings_guild WHERE id=$1",
                ctx.guild.id,
            )
            if guild_info["logs_enabled"]:
                embed = discord.Embed(
                    title=f":white_check_mark: Cleared warnings from "
                          f"{member.display_name} :white_check_mark:",
                    color=self.bot.success_color,
                    timestamp=ctx.message.created_at,
                )
                embed.set_footer(
                    text=f"New action by {ctx.author.display_name}",
                    icon_url=avatar_check(ctx.author),
                )
                embed.add_field(name="User", value=str(member), inline=True)
                embed.add_field(
                    name="Display Name", value=member.display_name, inline=True
                )
                embed.add_field(
                    name="Moderator", value=ctx.author.display_name, inline=True
                )
                embed.set_thumbnail(url=member.avatar_url)
                if guild_info["logs_embed"]:
                    await self.bot.get_channel(guild_info["moderation_channel"]).send(
                        embed=embed
                    )
                else:
                    await self.bot.get_channel(guild_info["moderation_channel"]).send(
                        f"```Warnings Cleared```"
                        f":white_check_mark: {ctx.author.mention} has removed all warnings from {member.mention} in "
                        f"{ctx.guild.name}"
                    )

    @commands.guild_only()
    @commands.command(name="tempmute")
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def tempmute(self, ctx, member: discord.Member = None, time=None, *, reason="None given"):
        if member is None:
            msg = (
                "**Description:** Temporarily mute a member\n"
                "**Cooldown:** 3 seconds\n"
                f"**Example:** furtempmute @{ctx.guild.owner.name} 30m spamming"
            )
            embed = discord.Embed(
                color=self.bot.info_color,
                title=f"Command: tempmute",
                description=msg,
            )
            return await ctx.send(embed=embed)
        if member == self.bot.user:
            return await ctx.send("Nice try, asshole")
        elif member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("Couldn't mute member, they're a higher role than me")
        else:
            if time[-1] == "s":
                undo_time = datetime.utcnow() + timedelta(seconds=int(time[:-1]))
            elif time[-1] == "m":
                undo_time = datetime.utcnow() + timedelta(minutes=int(time[:-1]))
            elif time[-1] == "h":
                undo_time = datetime.utcnow() + timedelta(hours=int(time[:-1]))
            elif time[-1] == "d":
                undo_time = datetime.utcnow() + timedelta(days=int(time[:-1]))
            else:
                return await ctx.send("Please use a valid time format, like '30m'")
            await ctx.message.delete()
            async with self.bot.pool.acquire() as db:
                mute_role_id = await db.fetchval(
                    "SELECT mute_role FROM botsettings_guild WHERE id=$1", ctx.guild.id
                )
                if not mute_role_id:
                    return await ctx.send(
                        f"There no mute role set up for {ctx.guild.name}!\n"
                        "Go to https://sheri.bot to add one first"
                    )
                mute_role = ctx.guild.get_role(mute_role_id)
                try:
                    await member.add_roles(mute_role, atomic=True)
                    await ctx.send(
                        f":mute: {str(member)} has been muted", delete_after=10
                    )
                    await db.execute(
                        """INSERT INTO botsettings_infraction 
                        (type, reason, guild_id, member_id, member_id_only, moderator_id, incident_date) VALUES
                        ($1, $2, $3, $4, $5, $6, $7)""",
                        "mute",
                        reason,
                        ctx.guild.id,
                        member.id,
                        member.id,
                        ctx.author.id,
                        datetime.utcnow(),
                    )
                    await db.execute(
                        """INSERT INTO botsettings_temppunishment
                                     (type, punishment_end, guild_id, member_id) VALUES
                                     ($1, $2, $3, $4)""",
                        "mute",
                        undo_time,
                        ctx.guild.id,
                        member.id,
                    )
                    guild_info = await db.fetchrow(
                        "SELECT moderation_channel, logs_embed, logs_enabled FROM botsettings_guild WHERE id=$1",
                        ctx.guild.id,
                    )
                    if guild_info["logs_enabled"]:
                        embed = discord.Embed(
                            title=f":mute: {member.display_name} Muted :mute:",
                            color=self.bot.warning_color,
                            timestamp=ctx.message.created_at,
                        )
                        embed.set_footer(
                            text=f"New action by {ctx.author.display_name}",
                            icon_url=avatar_check(ctx.author),
                        )
                        embed.add_field(name="User", value=str(member), inline=True)
                        embed.add_field(
                            name="Display Name", value=member.display_name, inline=True
                        )
                        embed.add_field(
                            name="Moderator", value=ctx.author.display_name, inline=True
                        )
                        embed.add_field(name="Length", value=time, inline=True)
                        embed.add_field(name="Reason", value=reason, inline=False)
                        embed.set_thumbnail(url=avatar_check(member))
                        if guild_info["logs_embed"]:
                            await self.bot.get_channel(
                                guild_info["moderation_channel"]
                            ).send(embed=embed)
                        else:
                            await self.bot.get_channel(
                                guild_info["moderation_channel"]
                            ).send(
                                f"```Member Temporarily Muted```"
                                f":mute: {ctx.author.mention} has temp muted {member.mention} for {time}\n"
                                f"Reason: {reason}"
                            )
                except discord.Forbidden as e:
                    await ctx.send(f"I'm not allowed to do that!'\n{str(e)}")
                except discord.HTTPException as e:
                    await ctx.send(f"Error when trying to add mute role:\n{e}")
                    self.bot.sentry.capture_exception(e)
                try:
                    await member.send(
                        f"You were temporarily muted in {ctx.message.guild.name}\nReason: {reason}\nLength: {time}"
                    )
                except discord.HTTPException:
                    pass

    @commands.guild_only()
    @commands.command(name="mute")
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def mute(self, ctx, member: discord.Member = None, *, reason="None given"):
        if member is None:
            msg = (
                "**Description:** Mute a member\n"
                "**Cooldown:** 3 seconds\n"
                f"**Example:** furmute perm @{ctx.guild.owner.name} spamming"
            )
            embed = discord.Embed(
                color=self.bot.info_color,
                title=f"Command: mute",
                description=msg,
            )
            return await ctx.send(embed=embed)
        if member == self.bot.user:
            return await ctx.send("Nice try, asshole")
        elif member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("Couldn't mute member, they're a higher role than me")
        else:
            await ctx.message.delete()
            async with self.bot.pool.acquire() as db:
                mute_role_id = await db.fetchval(
                    "SELECT mute_role FROM botsettings_guild WHERE id=$1", ctx.guild.id
                )
                if not mute_role_id:
                    return await ctx.send(
                        f"There no mute role set up for {ctx.guild.name}!\n"
                        "Go to https://sheri.bot to add one first"
                    )
                mute_role = ctx.guild.get_role(mute_role_id)
                try:
                    await member.add_roles(mute_role, atomic=True)
                    await db.execute(
                        """INSERT INTO botsettings_infraction 
                        (type, reason, guild_id, member_id, member_id_only, moderator_id, incident_date) VALUES 
                        ($1, $2, $3, $4, $5, $6, $7)""",
                        "mute",
                        reason,
                        ctx.guild.id,
                        member.id,
                        member.id,
                        ctx.author.id,
                        datetime.utcnow(),
                    )
                    guild_info = await db.fetchrow(
                        "SELECT moderation_channel, logs_embed, logs_enabled FROM botsettings_guild WHERE id=$1",
                        ctx.guild.id,
                    )
                    if guild_info["logs_enabled"]:
                        embed = discord.Embed(
                            title=f":mute: {member.display_name} Muted :mute:",
                            color=self.bot.warning_color,
                            timestamp=ctx.message.created_at,
                        )
                        embed.set_footer(
                            text=f"New action by {ctx.author.display_name}",
                            icon_url=avatar_check(ctx.author),
                        )
                        embed.add_field(name="User", value=str(member), inline=True)
                        embed.add_field(
                            name="Display Name", value=member.display_name, inline=True
                        )
                        embed.add_field(
                            name="Moderator", value=ctx.author.display_name, inline=True
                        )
                        embed.add_field(name="Reason", value=reason, inline=False)
                        embed.set_thumbnail(url=avatar_check(member))
                        if guild_info["logs_embed"]:
                            await self.bot.get_channel(
                                guild_info["moderation_channel"]
                            ).send(embed=embed)
                        else:
                            await self.bot.get_channel(
                                guild_info["moderation_channel"]
                            ).send(
                                f"```Member Muted```"
                                f":mute: {ctx.author.mention} has muted "
                                f"{member.mention}\nReason: {reason}"
                            )
                    await ctx.send(
                        f":mute: _{member.mention} has been muted!_", delete_after=10
                    )
                    try:
                        await member.send(
                            f"You were muted in {ctx.message.guild.name}\nReason: {reason}"
                        )
                    except discord.HTTPException:
                        pass
                except discord.Forbidden as e:
                    await ctx.send(f"I'm not allowed to do that!'\n{str(e)}")
                except discord.HTTPException as e:
                    await ctx.send(f"Error when trying to add mute role:\n{e}")
                    self.bot.sentry.capture_exception(e)

    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def unmute(self, ctx, member: discord.Member = None):
        if member is None:
            msg = (
                "**Description:** Unmute a member\n"
                "**Cooldown:** 3 seconds\n"
                f"**Usage:** **fur**unmute [member]\n"
                f"**Example:** **fur**unmute @{ctx.guild.owner.name}"
            )
            embed = discord.Embed(
                color=self.bot.info_color,
                title=f"Command: **fur**unmute",
                description=msg,
            )
            return await ctx.send(embed=embed)
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(
                "Couldn't unmute member, they're a higher role than me"
            )
        else:
            await ctx.message.delete()
            async with self.bot.pool.acquire() as db:
                mute_role_id = await db.fetchval(
                    "SELECT mute_role FROM botsettings_guild WHERE id=$1", ctx.guild.id
                )
                if not mute_role_id:
                    return await ctx.send(
                        f"There no mute role set up for {ctx.guild.name}!\n"
                        "Go to https://sheri.bot to add one first"
                    )
                mute_role = ctx.guild.get_role(mute_role_id)
                try:
                    await member.remove_roles(mute_role, atomic=True)
                    await ctx.send(
                        f":loud_sound: {str(member)} is no longer muted",
                        delete_after=10,
                    )
                    guild_info = await db.fetchrow(
                        "SELECT moderation_channel, logs_embed, logs_enabled FROM botsettings_guild WHERE id=$1",
                        ctx.guild.id,
                    )
                    if guild_info["logs_enabled"]:
                        embed = discord.Embed(
                            title=f":loud_sound: {member.display_name} Unmuted :loud_sound:",
                            color=self.bot.success_color,
                            timestamp=ctx.message.created_at,
                        )
                        embed.set_footer(
                            text=f"New action by {ctx.author.display_name}",
                            icon_url=avatar_check(ctx.author),
                        )
                        embed.add_field(name="User", value=str(member), inline=True)
                        embed.add_field(
                            name="Display Name", value=member.display_name, inline=True
                        )
                        embed.add_field(
                            name="Moderator", value=ctx.author.display_name, inline=True
                        )
                        embed.set_thumbnail(url=avatar_check(member))
                        if guild_info["logs_embed"]:
                            await self.bot.get_channel(
                                guild_info["moderation_channel"]
                            ).send(embed=embed)
                        else:
                            await self.bot.get_channel(
                                guild_info["moderation_channel"]
                            ).send(
                                f"```Member Unmuted```"
                                f":loud_sound: {ctx.author.mention} unmuted {member.mention}"
                            )
                except discord.Forbidden as e:
                    await ctx.send(f"I'm not allowed to do that!'\n{str(e)}")
                except discord.HTTPException as e:
                    await ctx.send(f"Error when trying to remove mute role:\n{e}")
                    self.bot.sentry.capture_exception(e)
                try:
                    await member.send(f"You are no longer muted in {ctx.guild.name}")
                except discord.HTTPException:
                    pass

    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def kick(self, ctx, member: discord.Member = None, *, reason="None given"):

        if member is None:
            msg = (
                "**Description:** Kick a member\n"
                "**Cooldown:** 3 seconds\n"
                f"**Usage:** **fur**kick [member] [reason]\n"
                f"**Example:** **fur**kick @{ctx.guild.owner.name} shiposting old memes"
            )
            embed = discord.Embed(
                color=self.bot.info_color,
                title=f"Command: **fur**kick",
                description=msg,
            )
            return await ctx.send(embed=embed)
        if member == self.bot.user:
            return await ctx.send("LOL! You can't make me kick myself.")
        elif member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(
                f"I could not kick {member} because their role is higher than mine."
            )
        elif member == ctx.author:
            return await ctx.send(f"LOL! You can't kick yourself, {ctx.author.mention}.")
        else:
            await self.bot.pool.execute(
                """INSERT INTO botsettings_infraction
                   (type, reason, guild_id, member_id, member_id_only, moderator_id, incident_date) VALUES
                   ($1, $2, $3, $4, $5, $6, $7)""",
                "kick",
                reason,
                ctx.guild.id,
                member.id,
                member.id,
                ctx.author.id,
                datetime.utcnow(),
            )
            try:
                await member.send(
                    f"You were kicked from {ctx.guild.name}.\n```{reason}```"
                )
            except discord.HTTPException:
                pass
            if ctx.channel.permissions_for(ctx.guild.me).kick_members:
                if can_manage_user(ctx, member):
                    if ctx.author == member.id:
                        return await ctx.send(
                            "You can't kick yourself. What are you even thinking?"
                        )
                    await member.kick(reason=f'[{ctx.author}] kicked with reason: ' + reason)
                    # noinspection PyCallByClass
                    await Logging.member_kick_log(self, ctx, member, reason)
                else:
                    await ctx.send(
                        "It appears that I can't manage this user, You will have to kick them "
                        "yourselves or put my role higher than theirs. :)")
            else:
                await ctx.send("It seems that I can't kick members!")
        if can_embed(ctx):
            if can_delete(ctx):
                await ctx.message.delete()
            embed = discord.Embed(color=self.bot.color)
            embed.add_field(
                name="Member Kicked",
                value=f"Member: {member}\n" f"Reason: {reason}",
                inline=False,
            )
            kick_image = await Get.main_api(self.bot, "kick")
            embed.set_image(url=kick_image["url"])
            await ctx.send(embed=embed)
        elif can_send(ctx):
            if can_delete(ctx):
                await ctx.message.delete()
            await ctx.send(f"_{member.name} has been kicked!_", delete_after=10)
        elif can_react(ctx):
            if can_external_react(ctx):
                await ctx.message.add_reaction(":mhm:391714717539762176")
            else:
                await ctx.message.add_reaction("✔")

    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def ban(self, ctx, member =None, *, reason="None given"):
        real_member = None
        if member is None:
            msg = (
                "**Description:** Ban a member\n"
                "**Cooldown:** 3 seconds\n"
                f"**Usage:** **fur**ban [member] [reason]\n"
                f"**Example:** **fur**ban @{ctx.guild.owner.name} shiposting old memes"
            )
            embed = discord.Embed(
                color=self.bot.info_color, title=f"Command: **fur**ban", description=msg
            )
            return await ctx.send(embed=embed)
        else:
            if not member.isdigit():
                member = await commands.MemberConverter().convert(ctx, member)
                real_member = True
                if member == ctx.author:
                    return await ctx.send("You can't ban yourself!")
                if member == self.bot.user:
                    return await ctx.send("Nice try, asshole")
                if member.top_role >= ctx.guild.me.top_role:
                    return await ctx.send(
                        "Couldn't ban member, they're a higher role than me"
                    )
                if can_ban(ctx):
                    if can_manage_user(ctx, member):
                        try:
                            await member.send(
                                f"You were banned from {ctx.guild.name} for the reason: {reason}"
                            )
                        except discord.HTTPException:
                            pass
                        await ctx.guild.ban(member, reason=f'[{ctx.author}] banned with reason: ' + reason)
                    else:
                        await ctx.send(content="Looks like I can't ban the member because I can't manage the user.")
                else:
                    await ctx.send(
                        content=f"I can't ban {member} because I do not have the required permissions to do so."
                    )
            elif member.isdigit():
                try:
                    member = await self.bot.fetch_user(member)
                except discord.NotFound:
                    return await send_message(ctx, message="User not found, did you put the right ID?")

                real_member = False
                server_member = False
                if member == ctx.author:
                    return await ctx.send("You can't ban yourself!")
                if member == self.bot.user:
                    return await ctx.send("Nice try, asshole")
                if member.id in ctx.guild.members:
                    server_member = True
                    if member.top_role >= ctx.guild.me.top_role:
                        return await ctx.send(
                            "Couldn't ban member, they're a higher role than me"
                        )
                try:
                    await member.send(
                        f"You were banned from {ctx.guild.name} for the reason: {reason}"
                    )
                except discord.HTTPException:
                    pass
                if can_ban(ctx):
                    if server_member:
                        if can_manage_user(ctx, member):
                            await ctx.guild.ban(member, reason=reason)
                    await ctx.guild.ban(member, reason=reason)
                else:
                    await ctx.send(
                        content=f"I can't ban {member} because I do not have the required permissions to do so."
                    )
            else:
                return await ctx.send(f"Couldn't find ``{member}``, try that again")

        await self.bot.pool.execute(
            """INSERT INTO botsettings_infraction
                         (type, reason, guild_id, member_id, member_id_only, moderator_id, incident_date) VALUES
                         ($1, $2, $3, $4, $5, $6, $7)""",
            "ban",
            reason,
            ctx.guild.id,
            member.id if real_member else None,
            member.id,
            ctx.author.id,
            datetime.utcnow(),
        )

        await Logging.member_ban_log(self, ctx, member, reason)

        if can_embed(ctx) and can_send(ctx):
            if can_delete(ctx):
                await ctx.message.delete()
            embed = discord.Embed(color=self.bot.color)
            embed.add_field(
                name="Member Banned",
                value=f"Member: {member}\n" f"Reason: {reason}")
            ban_image = await Get.main_api(self.bot, "ban")
            embed.set_image(url=ban_image["url"])
            await ctx.send(embed=embed)
        elif can_send(ctx):
            if can_delete:
                await ctx.message.delete()
            await ctx.send(
                f":no_entry_sign: ***{member.display_name if real_member else member} "
                "has been banned!***"
            )
        elif can_react(ctx):
            if can_external_react(ctx):
                await ctx.message.add_reaction(":mhm:391714717539762176")
            else:
                await ctx.message.add_reaction("✔")

    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def tempban(self, ctx, member = None, time=None, *, reason="None given"):
        if member is None:
            msg = (
                "**Description:** Temporarily ban a member\n"
                "**Cooldown:** 3 seconds\n"
                f"**Usage:** **fur**tempban [member] [time] [reason]\n"
                f"**Example:** **fur**tempban @{ctx.guild.owner.name} 30m shiposting old memes"
            )
            embed = discord.Embed(
                color=self.bot.info_color,
                title=f"Command: **fur**tempban",
                description=msg,
            )
            return await ctx.send(embed=embed)

        #elif member.top_role >= ctx.guild.me.top_role:
        #    return await ctx.send("Couldn't ban member, they're a higher role than me")
        else:
            if time[-1] == "s":
                undo_time = datetime.utcnow() + timedelta(seconds=int(time[:-1]))
            elif time[-1] == "m":
                undo_time = datetime.utcnow() + timedelta(minutes=int(time[:-1]))
            elif time[-1] == "h":
                undo_time = datetime.utcnow() + timedelta(hours=int(time[:-1]))
            elif time[-1] == "d":
                undo_time = datetime.utcnow() + timedelta(days=int(time[:-1]))
            else:
                return await ctx.send("Please use a valid time format, like '30m'")
            try:
                member = await commands.MemberConverter().convert(ctx, member)
                if member.top_role >= ctx.guild.me.top_role:
                    return await ctx.send(
                        "Couldn't ban member, they're a higher role than me"
                    )
                if member == self.bot.user:
                    return await ctx.send("Nice try, asshole")
            except:
                if member.isdigit():
                    member = await ctx.guild.get_member(member)
                    if not member:
                        return await ctx.send(
                            "You can't temporarily punish people not in this guild!",
                            delete_after=10,
                        )
                else:
                    return await ctx.send("Couldn't find that member, try that again")
            await ctx.message.delete()
            async with self.bot.pool.acquire() as db:
                await db.execute(
                    """INSERT INTO botsettings_infraction
                                 (type, reason, guild_id, member_id, member_id_only, moderator_id, incident_date) VALUES
                                 ($1, $2, $3, $4, $5, $6, $7)""",
                    "ban",
                    reason,
                    ctx.guild.id,
                    member.id,
                    member.id,
                    ctx.author.id,
                    datetime.utcnow(),
                )
                await db.execute(
                    """INSERT INTO botsettings_temppunishment
                                 (type, punishment_end, guild_id, member_id) VALUES
                                 ($1, $2, $3, $4)""",
                    "ban",
                    undo_time,
                    ctx.guild.id,
                    member.id,
                )
                guild_info = await db.fetchrow(
                    "SELECT moderation_channel, logs_embed, logs_enabled FROM botsettings_guild WHERE id=$1",
                    ctx.guild.id,
                )
                if guild_info["logs_enabled"]:
                    if guild_info["logs_embed"]:
                        image = await Get.main_api(self.bot, "ban")
                        embed = discord.Embed(
                            title=f":no_entry_sign: {member.display_name} "
                                  "Banned :no_entry_sign:",
                            color=self.bot.danger_color,
                            timestamp=ctx.message.created_at,
                        )
                        embed.set_footer(text=f"User ID: {member.id}")
                        embed.add_field(name="User", value=member.mention, inline=True)
                        embed.add_field(
                            name="Moderator", value=ctx.author.mention, inline=True
                        )
                        embed.add_field(name="Reason", value=reason, inline=True)
                        embed.add_field(name="Length", value=time, inline=True)
                        embed.set_thumbnail(url=avatar_check(member))
                        embed.set_image(url=image["url"])
                        await self.bot.get_channel(
                            guild_info["moderation_channel"]
                        ).send(embed=embed)
                    else:
                        await self.bot.get_channel(
                            guild_info["moderation_channel"]
                        ).send(
                            f"```Member Temporarily Banned```"
                            f":no_entry_sign: {ctx.author.mention} has temp banned "
                            f"{member.mention} for {time}\n"
                            f"Reason: {reason}"
                        )
                    await ctx.send(
                        f":no_entry_sign: ***{member.display_name} "
                        "has been banned!***"
                    )
                    try:
                        await member.send(
                            f"You were temporarily banned from {ctx.guild.name}\n"
                            f"Reason: {reason}\n"
                            f"Time: {time}"
                        )
                    except discord.HTTPException:
                        pass
                    await ctx.guild.ban(member, reason=reason)

    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def unban(self, ctx, user=None, *, reason="None given"):

        if user is None:
            msg = (
                "**Description:** Unban a member\n"
                "**Cooldown:** 3 seconds\n"
                f"**Usage:** **fur**unban [member] [reason]\n"
                f"**Example:** **fur**unban @{ctx.guild.owner.name} I guess your "
                "shitposting wasn't THAT bad"
            )
            embed = discord.Embed(
                color=self.bot.info_color,
                title=f"Command: **fur**warn",
                description=msg,
            )
            return await ctx.send(embed=embed)

        try:
            int(user)
        except ValueError:
            return await ctx.send("I need the ID of the user only.")
        
        banned = await self.bot.fetch_user(user)
        await ctx.message.delete()
        try:
            await ctx.guild.unban(banned, reason=reason)
        except discord.HTTPException:
            return await ctx.send(
                f"Can't unban {banned.name} since they're not banned here!"
            )
        except Exception as e:
            self.bot.sentry.capture_exception(e)
            return await ctx.send(f"Error: {str(e)}")
        async with self.bot.pool.acquire() as db:
            in_database = await db.fetchval(
                "SELECT EXISTS(SELECT * FROM botsettings_user WHERE id=$1)", banned.id
            )
            await db.execute(
                """INSERT INTO botsettings_infraction
                             (type, reason, guild_id, member_id, member_id_only, moderator_id, incident_date) VALUES
                             ($1, $2, $3, $4, $5, $6, $7)""",
                "unban",
                reason,
                ctx.guild.id,
                banned.id if in_database else None,
                banned.id,
                ctx.author.id,
                datetime.utcnow(),
            )
            guild_info = await db.fetchrow(
                "SELECT moderation_channel, logs_embed, logs_enabled FROM botsettings_guild WHERE id=$1",
                ctx.guild.id,
            )
            if guild_info["logs_enabled"]:
                if guild_info["logs_embed"]:
                    embed = discord.Embed(
                        title="User Unbanned",
                        color=self.bot.success_color,
                        timestamp=ctx.message.created_at,
                    )
                    embed.set_footer(
                        text=f"New action by {ctx.author.display_name}",
                        icon_url=avatar_check(ctx.author),
                    )
                    embed.add_field(name="User", value=str(banned), inline=True)
                    embed.add_field(
                        name="Moderator", value=ctx.author.mention, inline=True
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    embed.set_thumbnail(url=avatar_check(banned))
                    await self.bot.get_channel(guild_info["moderation_channel"]).send(
                        embed=embed
                    )
                else:
                    await self.bot.get_channel(guild_info["moderation_channel"]).send(
                        f"```Member Unbanned```"
                        f":white_check_mark: {ctx.author.mention} has unbanned {banned}\nReason: {reason}"
                    )
                await ctx.send(f":white_check_mark: ***{banned} has been unbanned!***")

    @commands.guild_only()
    @commands.command(aliases=["warnings", "warnlist", "listwarn", "punishments"])
    @commands.has_permissions(kick_members=True)
    async def shitlist(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        if member is None:
            async with self.bot.pool.acquire() as db:
                members = {}
                actions = await db.fetch(
                    "SELECT member_id from botsettings_infraction WHERE guild_id=$1",
                    ctx.guild.id,
                )
                for m in actions:
                    if m not in members:
                        members[m] = 1
                    else:
                        members[m] += 1
                desc = ""
                for m, n in members.items():
                    user = discord.utils.get(ctx.guild.members, id=m[0])
                    if not user:
                        continue
                    desc = desc + f"{user.name} - {n} Entries\n"
            embed = discord.Embed(
                title="Shitlist", color=self.bot.danger_color, description=desc
            )
            return await ctx.send(embed=embed)
        else:
            async with self.bot.pool.acquire() as db:
                actions = await db.fetch(
                    """SELECT type, incident_date, reason FROM botsettings_infraction
                                   WHERE member_id=$1 AND guild_id=$2""",
                    member.id,
                    ctx.guild.id,
                )
                incidents = ""
                for row in actions:
                    incidents += f"{row['type'].title()} - {row['incident_date']} - {row['reason']}\n"
                embed = discord.Embed(
                    color=self.bot.danger_color,
                    title=f"{member.display_name}'s shitlist",
                    description=incidents,
                )
                embed.set_thumbnail(url=avatar_check(member))
                await ctx.send(embed=embed)

    @commands.command(aliases=["ar"], no_pm=True)
    @commands.has_permissions(manage_roles=True)
    async def add_role(self, ctx, role: discord.Role, user: discord.Member = None):
        """Adds a role to a user, defaults to author. Role name must be in quotes if there are spaces."""
        author = ctx.author
        channel = ctx.channel
        guild = ctx.guild
        if not user:
            user = author
        #   role = self._role_from_string(guild, rolename)
        if not role:
            await ctx.send("<:error:391715668598325248> That role cannot be found.")
            return
        if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
            await ctx.send("<:error:391715668598325248> I don't have manage_roles.")
            return
        if not check_hierarchy(ctx, role):
            await ctx.send(
                "Sorry, Can't add you to a role that is higher than yourself."
            )
        try:
            await user.add_roles(
                role,
                reason="Role added via command ran by {}".format(ctx.message.author),
            )
            app = discord.Embed(color=self.bot.color)
            app.set_author(name="Sheri", icon_url=self.bot.user.avatar_url)
            app.set_footer(text="Murrrr", icon_url=guild.icon_url)
            app.add_field(
                name="Role Added to {}".format(user.name),
                value="Role: **{}**".format(role.name),
            )
            app.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=app)
        except discord.Forbidden:
            await ctx.send("<:error:391715668598325248> Some kind of error!")

    @commands.command(aliases=["rr"], no_pm=True)
    @commands.has_permissions(manage_roles=True)
    async def remove_role(self, ctx, role: discord.Role, user: discord.Member = None):
        "Removes a role to a user, defaults to author. Role name must be in quotes if there are spaces."
        guild = ctx.guild
        author = ctx.author
        # role = self._role_from_string(guild, rolename)
        if role is None:
            await ctx.send("<:error:391715668598325248> Role not found.")
            return
        if user is None:
            user = author
        if role in user.roles:
            try:
                em = discord.Embed(color=discord.Colour.purple())
                em.set_author(name=self.bot.user.name, icon_url=author.avatar_url)
                em.add_field(
                    name="Removed Role from {}".format(user.name),
                    value="Role: **{}**".format(role.name),
                )
                em.set_footer(text="Whimpers", icon_url=guild.icon_url)
                em.set_thumbnail(url=user.avatar_url)
                await user.remove_roles(
                    role,
                    reason="Role removed via command ran by {}".format(
                        ctx.message.author
                    ),
                )
                await ctx.send(embed=em)
            except discord.Forbidden:
                await ctx.send(
                    "<:error:391715668598325248> I don't have the proper permissions!"
                )
        else:
            await ctx.send("<:error:391715668598325248> User does not have that role.")

    @commands.group(aliases=["er"], no_pm=True)
    @commands.has_permissions(manage_roles=True)
    async def editrole(self, ctx):
        if ctx.invoked_subcommand is None:
            e = discord.Embed(color=self.bot.color)
            e.add_field(
                name="Commands",
                value="fur**er color**: Edit a role's color\n"
                      "Usage: `furer color Members fdabbf`\n"
                      "fur**er name**: Edits a role's name\n"
                      "Usage: `furer name Members Floofbutts`",
            )
            await ctx.send(embed=e)

    @editrole.command(aliases=["colour", "c"])
    @commands.has_permissions(manage_roles=True)
    async def color(self, ctx, role: discord.Role, value: discord.Colour):
        """"Edits a role's color"""
        try:
            await role.edit(
                color=value,
                reason="Command 'editrole' ran by {}".format(ctx.message.author),
            )
            await ctx.send("Done. <:fwrok:446318910711529473>")
        except discord.Forbidden:
            await ctx.send(
                "<:error:391715668598325248> I can't change the color of that role because you or I don't have the "
                "`Manage Nicknames` permission or it's too high up for me to reach. Halp!"
            )
        except Exception as e:
            print(e)
            await ctx.send("<:error:391715668598325248> Something went wrong.")

    @editrole.command(aliases=["n"], name="name")
    @commands.has_permissions(manage_roles=True)
    async def edit_role_name(self, ctx, role: discord.Role, *, name: str):
        """Edits a role's name"""
        if name == "":
            await ctx.send("<:error:391715668598325248> Name cannot be empty.")
            return
        try:
            await role.edit(name=name)
            await ctx.send("<:mhm:391714717539762176> Done!")
        except discord.Forbidden:
            await ctx.send(
                "<:error:391715668598325248> I can't rename that role because you or I don't have the `Manage Nicknames` "
                "permission or it's too high up for me to reach. Halp!"
            )
        except Exception as e:
            print(e)
            await ctx.send("<:error:391715668598325248> Something went wrong.")

    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def setnick(self, ctx, user: discord.Member, *, nickname=""):
        """Changes a members nickname. Leaving empty will remove it."""
        await ctx.message.delete()
        nickname = nickname.strip()
        cl = "changed"
        if nickname == "":
            nickname = None
            cl = "cleared"
        try:
            await user.edit(
                nick=nickname, reason=f"Command 'setnick' ran by {ctx.message.author}"
            )
            await ctx.send(
                f"<:mhm:391714717539762176> I have {cl} {user.name}'s nickname!",
                delete_after=5,
            )
        except discord.Forbidden:
            await ctx.send(
                "<:error:391715668598325248> Error updating nickname. Please ensure both of us have the `Manage Nicknames` "
                "permission, and that I have a role high enough to be able to edit the nickname of the target member."
            )

    #####################################
    #     Anti-Raid Auto-Moderation     #
    #####################################

    async def get_automod_status(self, guild):
        """ checks Redis and the database for the current status of automod """
        async with self.bot.redis_pool.get() as r:
            exists = await r.execute("exists", f"{guild}-automod-enabled")
            if not exists:
                async with self.bot.pool.acquire() as db:
                    automod_enabled = await db.fetchval(
                        """SELECT automod_enabled FROM botsettings_guild WHERE id=$1""",
                        guild,
                    )
                await r.execute(
                    "setex",
                    f"{guild}-automod-enabled",
                    60 * 60,
                    1 if automod_enabled else 0,
                )
                return automod_enabled
            automod_enabled = await r.execute("get", f"{guild}-automod-enabled")

            if not automod_enabled:
                return None
            return int(automod_enabled)

    @staticmethod
    async def get_banned_words(message, r, db):
        """ Checks the Redis cache for banned words, populates cache from DB if cache empty. Returns array. """
        banned_words = await r.execute(
            "lrange", f"{message.guild.id}_banned_words", 0, 999
        )
        if not banned_words:
            banned_words = await db.fetchval(
                """SELECT banned_words FROM botsettings_guild
                                             WHERE id=$1""",
                message.guild.id,
            )

            if None in banned_words:
                banned_words.remove(None) #HOW?

            if not banned_words:
                return []
            await r.execute("lpush", f"{message.guild.id}_banned_words", *banned_words)
            await r.execute("expire", f"{message.guild.id}_banned_words", 60 * 60)
        try:
            banned_words = [word.decode("utf-8") for word in banned_words]
        except AttributeError:
            pass
        return banned_words

    @staticmethod
    async def get_trigger_words(message, r, db):
        """ Checks the Redis cache for trigger words, populates cache from DB if cache empty. Returns array. """
        trigger_words = await r.execute(
            "lrange", f"{message.guild.id}_trigger_words", 0, 999
        )
        if not trigger_words:
            trigger_words = await db.fetchval(
                """SELECT trigger_words FROM botsettings_guild
                                              WHERE id=$1""",
                message.guild.id,
            )
            if not trigger_words:
                return []
            await r.execute(
                "lpush", f"{message.guild.id}_trigger_words", *trigger_words
            )
            await r.execute("expire", f"{message.guild.id}_trigger_words", 60 * 60)
        try:
            trigger_words = [word.decode("utf-8") for word in trigger_words]
        except AttributeError:
            pass
        return trigger_words

    @staticmethod
    async def get_newcomer_timeout(message, r, db):
        """ Checks the Redis cache for the newcomer timeout, populates cache from DB if cache empty. Returns int. """
        newcomer_time_limit = await r.execute(
            "get", f"{message.guild.id}_newcomer_time_limit"
        )
        if not newcomer_time_limit:
            newcomer_time_limit = await db.fetchval(
                """SELECT newcomer_time_limit FROM botsettings_guild
                                                    WHERE id=$1""",
                message.guild.id,
            )
            await r.execute(
                "set", f"{message.guild.id}_newcomer_time_limit", newcomer_time_limit
            )
            await r.execute(
                "expire", f"{message.guild.id}_newcomer_time_limit", 60 * 60
            )
        return int(newcomer_time_limit)

    @staticmethod
    async def check_for_spam(message):
        """ Checks the last 5 seconds of chat, if user has sent more than 3 messages, delete and notify """
        m_count = 0
        async for m in message.channel.history(
                after=(datetime.utcnow() + timedelta(seconds=-5))
        ):
            if m.author == message.author:
                m_count += 1
        if m_count > 3:
            try:
                await message.delete()
            except discord.NotFound:
                pass
            except discord.Forbidden:
                return

            await message.channel.send(
                f"**Automod**: No spamming, {message.author.mention}", delete_after=5
            )

    @staticmethod
    async def handle_trigger_words(message, db, trigger_words):
        """ Checks message for trigger words, deletes and adds infraction for each found """
        if trigger_words:
            for word in message.content.lower().split():
                if word in trigger_words:
                    try:
                        await message.delete()
                    except discord.NotFound:
                        pass
                    await db.execute(
                        """INSERT INTO botsettings_infraction
                                     (type, reason, guild_id, member_id, member_id_only, incident_date)
                                     VALUES ($1, $2, $3, $4, $4, $5)""",
                        "automod",
                        "Automod language filter",
                        message.guild.id,
                        message.author.id,
                        datetime.utcnow(),
                    )
                    count = await db.fetchval(
                        """SELECT count(*) FROM botsettings_infraction WHERE
                                              member_id=$1 AND guild_id=$2""",
                        message.author.id,
                        message.guild.id,
                    )
                    if count > 5:
                        await message.guild.ban(
                            message.author, reason="Automod anti-raid protection"
                        )
                    else:
                        await message.author.send(
                            f"**Automod violation #{count}:**\n"
                            f"Common raid language detected: {word}\n"
                            "Note that repeated violations as a new member "
                            "will automatically result in a ban"
                        )

    @staticmethod
    async def check_for_uppercase(message):
        """ Checks the message for all uppercase spam """
        num_upper = 0
        num_total = len(message.content.replace(" ", ""))

        for letter in list(message.content):
            if letter.isupper():
                num_upper += 1

        if num_upper >= num_total / 2 and num_total > 7:
            try:
                await message.delete()
            except discord.NotFound:
                pass
            await message.channel.send("**Automod**: No yelling >:[", delete_after=5)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def updateautomod(self, ctx):
        """ Automod only updates once per hour, this skips the wait and updates immediately """
        async with self.bot.redis_pool.get() as r:
            async with self.bot.pool.acquire() as db:
                automod_enabled = await db.fetchval(
                    """SELECT automod_enabled FROM botsettings_guild WHERE id=$1""",
                    ctx.guild.id,
                )
            await r.execute(
                "setex",
                f"{ctx.guild.id}-automod-enabled",
                60 * 60,
                1 if automod_enabled else 0,
            )
        return await ctx.send(
            f"Automod updated, it is currently {'enabled' if automod_enabled else 'disabled'}"
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        """ Performs automod check on every message, only inside guilds """''
        if not message.guild:
            return
        try:
            if message.author != self.bot.user and message.author.bot is not True:
                automod_enabled = await self.get_automod_status(message.guild.id)
                if not automod_enabled:
                    return
                async with self.bot.redis_pool.get() as r:
                    async with self.bot.pool.acquire() as db:
                        banned_words = await self.get_banned_words(message, r, db)
                        for word in message.content.lower().split():
                            if word in banned_words:
                                try:
                                    await message.delete()
                                except discord.NotFound:
                                    return
                        newcomer_time_limit = await self.get_newcomer_timeout(
                            message, r, db
                        )
                        try:
                            if message.author.joined_at + timedelta(minutes=-newcomer_time_limit) > datetime.utcnow():
                                await self.check_for_spam(message)
                                trigger_words = await self.get_trigger_words(
                                    message, r, db
                                )
                                await self.handle_trigger_words(
                                    message, db, trigger_words
                                )
                                await self.check_for_uppercase(message)
                        except AttributeError:
                            pass
        except Exception as e:
            capture_exception(e)

    ##############################
    #     Temp Commands Loop     #
    ##############################

    @tasks.loop(minutes=1)
    async def check_temp(self):
        try:
            async with self.bot.pool.acquire() as db:
                rows = await db.fetch(
                    """SELECT id, member_id, guild_id, type, punishment_end
                                      FROM botsettings_temppunishment"""
                )
                for row in rows:
                    try:
                        if row["punishment_end"].replace(tzinfo=pytz.utc) <= datetime.now(
                                pytz.utc
                        ):
                            guild = self.bot.get_guild(row["guild_id"])
                            member = guild.get_member(int(row["member_id"]))
                            if not member:
                                member_left = await self.bot.fetch_user(
                                    int(row["member_id"])
                                )
                            mod_channel_id = await db.fetchval(
                                """SELECT moderation_channel FROM botsettings_guild
                                                               WHERE id=$1""",
                                row["guild_id"],
                            )
                            mod_channel = (
                                self.bot.get_channel(mod_channel_id)
                                if mod_channel_id
                                else None
                            )
                            logs_enabled = await db.fetchval(
                                "SELECT logs_enabled FROM botsettings_guild WHERE id=$1",
                                row["guild_id"],
                            )
                            logs_embed = await db.fetchval(
                                "SELECT logs_embed FROM botsettings_guild WHERE id=$1",
                                row["guild_id"],
                            )
                            if row["type"] == "mute":
                                if member:
                                    mute_role_id = await db.fetchval(
                                        "SELECT mute_role FROM botsettings_guild WHERE id=$1",
                                        row["guild_id"],
                                    )
                                    mute_role = discord.utils.get(
                                        guild.roles, id=mute_role_id
                                    )
                                    try:
                                        await member.remove_roles(
                                            mute_role, reason="Temp time up", atomic=True
                                        )
                                    except discord.Forbidden:
                                        pass
                                await db.execute(
                                    "DELETE FROM botsettings_temppunishment WHERE ID=$1",
                                    row["id"],
                                )
                                if logs_enabled:
                                    if logs_embed:
                                        if not member:
                                            member = member_left
                                        embed = discord.Embed(
                                            title=f":loud_sound: {member.display_name} "
                                                  "Unmuted :loud_sound:",
                                            color=self.bot.success_color,
                                            timestamp=datetime.utcnow(),
                                        )
                                        embed.set_footer(text="Temp Punishment Over")
                                        embed.add_field(
                                            name="User", value=str(member), inline=True
                                        )
                                        embed.add_field(
                                            name="Display Name",
                                            value=member.display_name,
                                            inline=True,
                                        )
                                        embed.set_thumbnail(url=avatar_check(member))
                                        await mod_channel.send(embed=embed)
                                    else:
                                        await mod_channel.send(
                                            f":loud_sound: {member.mention} is no longer muted, "
                                            "their temp punishment is over"
                                        )
                                try:
                                    await member.send(
                                        f"You are no longer muted in {self.bot.get_guild(row['guild_id']).name}"
                                    )
                                except discord.HTTPException:
                                    pass
                            elif row["type"] == "ban":
                                if not member:
                                    member = member_left
                                    await self.bot.get_guild(row["guild_id"]).unban(
                                        member, reason="Temp punishment over"
                                    )
                                else:
                                    await self.bot.get_guild(row["guild_id"]).unban(
                                        member, reason="Temp punishment over"
                                    )

                                await db.execute(
                                    "DELETE FROM botsettings_temppunishment WHERE ID=$1",
                                    row["id"],
                                )
                                if logs_enabled:
                                    if logs_embed:
                                        embed = discord.Embed(
                                            title="User Unbanned",
                                            color=self.bot.success_color,
                                            timestamp=datetime.utcnow(),
                                        )
                                        embed.set_footer(text="Temp Punishment Over")
                                        embed.add_field(
                                            name="User", value=str(member), inline=True
                                        )
                                        embed.set_thumbnail(url=avatar_check(member))
                                        await mod_channel.send(embed=embed)
                                    else:
                                        await mod_channel.send(
                                            f"{member} is no longer banned, "
                                            "their temp punishment is over")
                    except discord.Forbidden:
                        return

        except Exception as e:
            capture_exception(e)

    @check_temp.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()

    #####################################
    #       Cleanup Command
    #####################################
    # Source: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/mod.py

    @commands.group(name="eat", aliases=["purge"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def cleanup(self, ctx):
        """ Removes messages from the current server. """
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=self.bot.color,
                title="Commands",
                description="**fureat all [1-100]** - Deletes up to 100 messages.\n"
                            "⚠️ **WARNING:** Using `fureat all` with no numerical value will delete a very large number of messages and will severely rate limit Sheri "
                            "on your server for approximately 3 minutes. Please only exclude numerical values if you wish to deep clean a channel.\n"
                            "**fureat embeds [1-100]** - Deletes up to 100 embedded messages.\n"
                            "**fureat files [1-100]** - Deletes up to 100 messages that contain files.\n"
                            "**fureat bots [1-100]** - Deletes up to 100 messages that are made by bots.\n"
                            "**fureat user @user [1-100]** - Deletes up to 100 messages that are made by the user.\n"
                            "**fureat emoji [1-100]** - Deletes up to 100 messages that contain emojis\n"
                            "**fureat reactions [1-100]** - Deletes reactions from messages.\n"
                            "**fureat contains contents [1-100]** - Deletes the messages that contains the content.",
            )
            await send_message(ctx, embed=embed)
        else:
            if can_delete(ctx):
                try:
                    await ctx.message.delete()
                except discord.errors.NotFound:
                    pass
            else:
                return await send_message(ctx, message="I need to be able to delete messages.")

    @cleanup.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await do_removal(ctx, search, lambda e: len(e.embeds))

    @cleanup.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await do_removal(ctx, search, lambda e: len(e.attachments))

    @cleanup.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await do_removal(
            ctx, search, lambda e: len(e.embeds) or len(e.attachments)
        )

    @cleanup.command(name="all")
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await do_removal(ctx, search, lambda e: True)

    @cleanup.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await do_removal(ctx, search, lambda e: e.author == member)

    @cleanup.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send("The substring length must be at least 3 characters.")
        else:
            await do_removal(ctx, 100, lambda e: substr in e.content)

    @cleanup.command(name="messages")
    async def _messages(self, ctx, search=100):
        """ Removes all messages without attachments """
        await do_removal(ctx, search, lambda e: len(e.attachments) == 0)

    @cleanup.command(name="bots")
    async def _bots(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return m.author.bot or (prefix and m.content.startswith(prefix))

        await do_removal(ctx, search, predicate)

    @cleanup.command(name="emoji")
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r"<:(\w+):(\d+)>")

        def predicate(m):
            return custom_emoji.search(m.content)

        await do_removal(ctx, search, predicate)

    @cleanup.command(name="reactions")
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""
        message = choice(get_list["eats"])
        if search > 2000:
            return await ctx.send(f"Too many messages to eat ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(
            f"{message}\nEaten {total_reactions} reactions.", delete_after=10
        )


def setup(bot):
    bot.add_cog(Moderation(bot))
