import discord

from Checks.bot_checks import can_send, can_embed, can_external_react
from Lines.custom_emotes import logging_emotes


class Logging:
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def send_logs(channel, guild, message: str = None, embed: discord.Embed = None):

        if embed:
            if can_send(guild=guild, channel=channel):
                if can_embed(guild=guild, channel=channel):
                    try:
                        return await channel.send(embed=embed)
                    except (discord.Forbidden, discord.HTTPException):
                        return

            if can_send(guild=guild, channel=channel):
                return await channel.send("I cannot embed links here, please fix this issue.")
            try:

                await guild.owner.send(f"My permissions are messed up in {channel.mention}. "
                                       f"You have embed logs enabled and I cannot send messages in that channel.")
            except discord.Forbidden:
                return

        if message:
            if can_send(guild=guild, channel=channel):
                if can_external_react(guild=guild, channel=channel):
                    return await channel.send(content=message)

            # Attempt to notify the owner of the discord that the permissions are broken
            try:
                await guild.owner.send(f"My permissions are messed up in {channel.mention}. "
                                       f"You have non embed logs enabled and I cannot send messages/use external emojis in that channel.")

            except discord.Forbidden:
                return

    async def get_log_channel(self, channeltype, guild):
        try:
            async with self.bot.pool.acquire() as db:
                logging_config = await db.fetchrow(
                    f"SELECT {channeltype}, logs_enabled, default_channel, logs_embed FROM botsettings_guild WHERE id=$1",
                    guild.id)

                if logging_config['logs_enabled']:
                    if logging_config[f'{channeltype}']:
                        channel = guild.get_channel(logging_config[f'{channeltype}'])
                        if channel:
                            return channel, logging_config['logs_embed']
                        return False, False
                    elif logging_config['default_channel']:
                        channel = guild.get_channel(logging_config[f'default_channel'])
                        if channel:
                            return channel, logging_config['logs_embed']
                        return False, False
                return False, False
        except TypeError:
            return

    async def log_channel(self, channeltype, guild):
        try:
            database = await self.bot.pool.fetchrow(
                f"SELECT {channeltype}, logs_enabled, default_channel, logs_embed FROM botsettings_guild WHERE id=$1",
                guild.id)
            # check to see if logs are enabled
            if database['logs_enabled']:
                # Check to see if the channel is configured if not default to the default channel
                if database[f'{channeltype}']:
                    channel = guild.get_channel(database[f'{channeltype}'])
                    # Check to make sure the channel is not returning NONE
                    if channel is not None:
                        return [channel, database['logs_embed']]
                    # oh comon, why did you have to delete it?
                    elif database['default_channel']:
                        channel = guild.get_channel(database['default_channel'])
                        if channel is not None:
                            return [channel, database['logs_embed']]
                elif database['default_channel']:
                    channel = guild.get_channel(database['default_channel'])
                    if channel is not None:
                        return [channel, database['logs_embed']]
            return [False, False]
        except (TypeError, AttributeError):
            return [False, False]

    async def member_ban_log(self, ctx, member, reason):
        database = await Logging.log_channel(self, 'moderation_channel', ctx.guild)
        channel, embed_enabled = database[0], database[1]
        if channel:
            if embed_enabled:
                embed = discord.Embed(
                    title=f"{logging_emotes['bancreated']} {member} has been banned",
                    color=self.bot.danger_color,
                    timestamp=ctx.message.created_at,
                    description=f"**Reason for ban:** {reason}\n"
                                f"**User ID:** ``{member.id}``\n"
                                f"**Responsible Moderator: {ctx.author}({ctx.author.id})**"
                )
                await Logging.send_logs(channel, ctx.guild, embed=embed)

            else:
                log_message = (f"```Member Banned```"
                               f"{logging_emotes['bancreated']} **{member}**(``{member.id}``) has been banned by "
                               f"**{ctx.author}** (``{ctx.author.id}``) "
                               f"for the reason {reason}.")
                await Logging.send_logs(channel, ctx.guild, message=log_message)

    async def member_kick_log(self, ctx, member, reason):
        database = await Logging.log_channel(self, 'moderation_channel', ctx.guild)
        channel, embed_enabled = database[0], database[1]
        if channel:
            if embed_enabled:
                embed = discord.Embed(
                    title=f"👢 {member} has been kicked",
                    color=self.bot.danger_color,
                    timestamp=ctx.message.created_at,
                    description=f"**Reason for kick:** {reason}\n"
                                f"**User ID:** ``{member.id}``\n"
                                f"**Responsible Moderator: {ctx.author} ({ctx.author.id})**"
                )
                await Logging.send_logs(channel, ctx.guild, embed=embed)

            else:
                log_message = ("```Member Kicked```"
                               f"👢 **{member}**(``{member.id}``) has been kicked by **{ctx.author}** (``{ctx.author.id}``) "
                               f"for the reason {reason}.")
                await Logging.send_logs(channel, ctx.guild, message=log_message)

