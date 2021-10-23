from datetime import datetime, timezone

from Database.transactions import add_user, add_guild_level


def _get_level_xp(n):
    return 5 * (n ** 2) + 50 * n + 100


def _get_level_from_xp(xp):
    remaining_xp = int(xp)
    level = 0
    while remaining_xp >= _get_level_xp(level):
        remaining_xp -= _get_level_xp(level)
        level += 1
    return level


async def banned_role_or_channel(ctx, db):
    record = await db.fetchrow(
        "SELECT no_xp_roles, no_xp_channels FROM botsettings_guild WHERE id=$1",
        ctx.guild.id,
    )
    is_banned = False
    for role in ctx.author.roles:
        if role.id in record["no_xp_roles"]:
            is_banned = True
    if ctx.channel.id in record["no_xp_channels"]:
        is_banned = True
    return is_banned


async def get_member_info(self, db, member):
    guild_xp = await db.fetchval(
        "SELECT xp FROM botsettings_guildlevel WHERE guild_id=$1 AND member_id=$2",
        member.guild.id,
        member.id,
    )
    if guild_xp is None:
        await add_guild_level(self.bot.pool, member.guild, member)
        guild_xp = 0
    member_xp = await db.fetchval(
        "SELECT xp FROM botsettings_user WHERE id=$1", member.id
    )
    guild_level = self._get_level_from_xp(guild_xp)
    global_level = self._get_level_from_xp(member_xp)
    x = 0
    for y in range(0, global_level):
        x += self._get_level_xp(y)
    remaining_global_xp = member_xp - x
    x = 0
    for y in range(0, guild_level):
        x += self._get_level_xp(y)
    remaining_guild_xp = guild_xp - x
    global_level_xp = self._get_level_xp(global_level)
    guild_level_xp = self._get_level_xp(guild_level)

    return {
        "guild_xp": guild_xp,
        "guild_level": guild_level,
        "remaining_guild_xp": remaining_guild_xp,
        "guild_level_xp": guild_level_xp,
        "global_xp": member_xp,
        "global_level": global_level,
        "remaining_global_xp": remaining_global_xp,
        "global_level_xp": global_level_xp,
    }


async def get_redis_user_info(self, message):
    async with self.bot.redis_pool.get() as r:
        last_added = await r.execute("get", f"{message.author.id}_xp_last_added")
        if last_added:
            last_added = datetime.fromisoformat(last_added.decode("utf-8"))
            guild_xp = await r.execute(
                "get", f"{message.guild.id}{message.author.id}_xp"
            )
            if not guild_xp:
                guild_xp = 0
                await r.execute(
                    "set", f"{message.guild.id}{message.author.id}_xp", 0
                )
            global_xp = await r.execute("get", f"{message.author.id}_xp")
            if not global_xp:
                global_xp = 0
                await r.execute("set", f"{message.author.id}_xp", 0)
            return {
                "xp_last_added": last_added,
                "guild_xp": int(guild_xp),
                "global_xp": int(global_xp),
            }
        else:
            return False


async def get_pg_user_info(self, message):
    async with self.bot.pool.acquire() as db:
        user_info = await db.fetchrow(
            """SELECT xp_last_added, xp FROM botsettings_user WHERE id=$1""",
            message.author.id,
        )
        if user_info is None:
            await add_user(self.bot.pool, message.author)
            last_added = datetime.now(timezone.utc)
            return {"xp_last_added": last_added, "guild_xp": 0, "global_xp": 0}
        else:
            guild_xp = await db.fetchval(
                """SELECT xp FROM botsettings_guildlevel
                                         WHERE member_id=$1 AND guild_id=$2""",
                message.author.id,
                message.guild.id,
            )
            if guild_xp is None:
                await add_guild_level(self.bot.pool, message.guild, message.author)
                guild_xp = 0
            async with self.bot.redis_pool.get() as r:
                await r.execute(
                    "set",
                    f"{message.author.id}_xp_last_added",
                    user_info["xp_last_added"].isoformat(),
                )
                await r.execute(
                    "set", f"{message.guild.id}{message.author.id}_xp", guild_xp
                )
                await r.execute("set", f"{message.author.id}_xp", user_info["xp"])
            return {
                "xp_last_added": user_info["xp_last_added"],
                "guild_xp": guild_xp,
                "global_xp": user_info["xp"],
            }


async def update_xp(self, message, user_info, add_xp):
    async with self.bot.pool.acquire() as db:
        await db.execute(
            "UPDATE botsettings_user SET xp=$1, xp_last_added=$2 WHERE id=$3",
            user_info["global_xp"] + add_xp,
            datetime.now(timezone.utc),
            message.author.id,
        )
        await db.execute(
            "UPDATE botsettings_guildlevel SET xp=$1 WHERE guild_id=$2 AND member_id=$3",
            user_info["guild_xp"] + add_xp,
            message.guild.id,
            message.author.id,
        )
    async with self.bot.redis_pool.get() as r:
        await r.execute(
            "set",
            f"{message.guild.id}{message.author.id}_xp",
            user_info["guild_xp"] + add_xp,
        )
        await r.execute(
            "set", f"{message.author.id}_xp", user_info["global_xp"] + add_xp
        )
        await r.execute(
            "set",
            f"{message.author.id}_xp_last_added",
            datetime.now(timezone.utc).isoformat(),
        )
