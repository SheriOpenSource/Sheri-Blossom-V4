import discord
from discord.ext import commands

from Formats.formats import RoleID


class react_roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def reactrole(
            self,
            ctx,
            channel: discord.TextChannel,
            message_id: int,
            emoji: str,
            *,
            role: RoleID,
    ):
        if "<a" in emoji:
            r = emoji.replace("<a", "").replace(">", "")
            r = r.replace(":", "").replace(":", "")
            emoji_name = "".join("" if c.isdigit() else c for c in r)
        elif "<" in emoji:
            r = emoji.replace("<", "").replace(">", "")
            r = r.replace(":", "").replace(":", "")
            emoji_name = "".join("" if c.isdigit() else c for c in r)
        else:
            emoji_name = emoji.replace(":", "").replace(":", "")
            # if "<" in emoji:
            # emoji_name = emoji.replace("<", "").replace(">", "")
            # else:
            # emoji_name = emoji.replace(":", "")
        try:
            channel = ctx.guild.get_channel(channel.id)
            message = await channel.fetch_message(message_id)
            await message.add_reaction(emoji)
        except discord.NotFound:
            return await ctx.send(
                "Are you sure that the message ID is a indeed a message ID? Please double check and try again.\n"
                "See https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID- if you are unsure how to get a message ID."
            )
        except discord.HTTPException:
            return await ctx.send(
                "It seems that I do not have access to this emoji, or this emoji doesn't exist."
            )

        async with ctx.bot.pool.acquire() as db:
            check_combo = await db.fetchrow(
                "SELECT * FROM botsettings_react_roles WHERE guild_id = $1 AND channel_id = $2 AND message_id = $3 AND role_id = $4 AND emoji_id = $5",
                ctx.guild.id,
                channel.id,
                message_id,
                role,
                emoji_name,
            )
            rx = discord.utils.get(ctx.guild.roles, id=role)
            if check_combo:
                await db.execute(
                    "DELETE FROM botsettings_react_roles WHERE guild_id = $1 AND channel_id = $2 AND message_id = $3 AND role_id = $4 AND emoji_id = $5",
                    ctx.guild.id,
                    channel.id,
                    message_id,
                    role,
                    emoji_name,
                )
                return await ctx.send(
                    f"I have successfully removed **{rx.name}** and {emoji} for reaction roles on the message ``{message_id}``."
                )
            else:
                await db.execute(
                    "INSERT INTO botsettings_react_roles (guild_id, channel_id, message_id, role_id, emoji_id) VALUES ($1, $2, $3, $4, $5)",
                    ctx.guild.id,
                    channel.id,
                    message_id,
                    role,
                    emoji_name,
                )
                await ctx.send(
                    f"Done, successfully set **{rx.name}** and {emoji} as reaction roles on the message ``{message_id}``."
                )

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
    bot.add_cog(react_roles(bot))
