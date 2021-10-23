from dataclasses import dataclass

import discord

from Functions import errors
from Functions.ctx import CustomContext


@dataclass
class Prefixes:
    ctx: CustomContext
    prefix: str = None

    @staticmethod
    async def get(bot, message):
        # Get default prefixes
        prefixes = [bot.user.mention + " ", "fur", "sheri, "]

        # If we're in a guild, add the guilds custom prefixes
        if isinstance(message.channel, discord.TextChannel):
            guild = message.guild
            data = await bot.pool.fetchval("SELECT prefixes FROM botsettings_guild WHERE id=$1", guild.id)
            if data:
                prefixes.extend(data)

            # Nicks are different mentions
            if guild.get_member(bot.user.id).nick:
                prefixes.append(guild.me.mention + " ")

        # Now that we have the list, let's try to see if it's in the message, if not we just return the entire list
        for prefix in prefixes:
            if message.content.lower().startswith(prefix):
                return message.content[:len(prefix)]
        return prefixes

    async def list(self):
        ctx = self.ctx
        bot = ctx.bot
        # Get default prefixes
        prefixes = [bot.user.mention + " ", "fur", "sheri, "]

        # If we're in a guild, add the guilds custom prefixes
        if isinstance(ctx.channel, discord.TextChannel):
            prefixes.extend(await ctx.pool.fetchval("SELECT prefixes FROM botsettings_guild WHERE id=$1", ctx.guild.id))

        # Make a string out of the list and return it
        return ", ".join(prefixes)

    async def add(self):
        ctx, prefix = self.ctx, self.prefix
        # If the prefix is more than 10 characters we don't want it
        if len(prefix) > 10:
            raise errors.PrefixTooLong

        # Get the current prefixes and make sure it's not 10 in length
        current_prefixes = \
            (await ctx.pool.fetch("SELECT prefixes FROM botsettings_guild WHERE id=$1", ctx.guild.id))[0][0]
        if len(current_prefixes) == 10:
            raise errors.TooManyPrefixes

        # Get the default prefixes and make sure the prefix isn't in those
        default_prefixes = ["fur", "sheri, "]
        if prefix.lower() in current_prefixes or prefix in default_prefixes:
            raise errors.DuplicatePrefix

        # Add the prefix
        await ctx.pool.execute(
            "UPDATE botsettings_guild SET prefixes=array_append(prefixes, $1) WHERE id=$2",
            prefix.lower(),
            ctx.guild.id
        )

    async def remove(self):
        ctx, prefix = self.ctx, self.prefix
        # Get the current prefixes and make sure it's in them
        prefixes = await ctx.pool.fetchval("SELECT prefixes FROM botsettings_guild WHERE id=$1", ctx.guild.id)
        if prefix.lower() not in prefixes:
            raise errors.PrefixNotFound

        # Remove the prefix
        await ctx.pool.execute(
            "UPDATE botsettings_guild SET prefixes=array_remove(prefixes, $1) WHERE id=$2",
            prefix.lower(),
            ctx.guild.id
        )
