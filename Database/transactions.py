from datetime import datetime, timezone

banned_words = [
    "nigger",
    "n1gger",
    "n1ggers",
    "niggers",
    "faggot",
    "faggots",
    "fagit",
    "fagits",
    "faggit",
    "faggits",
    "fag",
    "fags",
    "furfag",
    "furfags",
]


async def add_user(db, user):
    try:
        await db.execute(
            """INSERT INTO botsettings_user
                         (id, away, away_message, premium, premium_count, foxes, foxesall, bunnies, bunniesall,
                         wolves, wolvesall, coins, boxes, keys, treats, presents, marry, xp, xp_last_added,
                         animal_catch_dm, api_access, cats, catsall, developer, vip, owner,
                          keyshards, keyshardsall, lustshardsall, lustshards, support, gender, orientation)
                         VALUES ($1, False, '', False, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '{}', 0, $2,
                          False, False, 0, 0, False, False, False, 0,0,0,0, 'f', 'Female', 'Straight')
                         ON CONFLICT DO NOTHING""",
            user.id,
            datetime.now(timezone.utc),
        )
        print(f"[Database] - Added {user.name}({user.id}) to the user database.")
    except Exception as e:
        print(f"[Database] - Error adding user {user.name}({user.id}):\n{e}")


async def bulk_add_users(pool, users):
    async with pool.acquire() as db:
        result = await db.copy_records_to_table("users", records=users, columns=["id"])
        return result


async def add_guild(db, guild):
    try:
        await db.execute(
            """INSERT INTO botsettings_guild
                         (id, owner_id, prefixes, premium, premium_owner_id, logs_embed, logs_enabled, registration_enabled,
                         autoroles, autoroles_enabled, botautorole_enabled, welcome_message,
                         leave_message, welcome_leave_embed, welcome_leave_color, welcome_background,
                         welcome_type, catching_channels, catching_enabled, no_xp_channels, no_xp_roles,
                         levels_announce, levels_message, newcomer_time_limit, automod_enabled, global_automod,
                         banned_words, trigger_words, persistent_roles_enabled, selfroles, global_automod_action,
                         welcome_leave_enabled, registration_nsfw, dehoist, anti_zalgo, social_embeds, registration_channel_lock,
                          registration_intro_enabled, registration_intro_message, registration_cleanup_toggle)
                         VALUES ($1, $2, '{}', 'f', null, 't', 'f', 'f', '{}', 'f', 'f', '', '', 't', 16761035, 1, 2, '{}',
                         'f', '{}', '{}', 'f', 'Congrats on leveling up **{name}**! You are now level **{level}**',
                         120, 'f', 't', $3, $4, 'f', '{}', 'warn', 'f', 't', 'f', 'f', 't', 'f', 'f', 
                         'Everyone, {mention} has just registered to the server, Give them a warm welcome.', 'f')
                         ON CONFLICT DO NOTHING""",
            guild.id,
            guild.owner.id,
            banned_words,
            banned_words,
        )
        print(f"[Database] - Added {guild.name}({guild.id}) to the guild database.")
    except Exception as e:
        print(f"[Database] - Error adding guild {guild.name} ({guild.id}):\n{e}")


async def add_guild_level(pool, guild, user):
    async with pool.acquire() as db:
        await add_guild(db, guild)
        await db.execute(
            """INSERT INTO botsettings_guildlevel
                         (guild_id, member_id, xp) VALUES ($1, $2, 0)
                         ON CONFLICT DO NOTHING""",
            guild.id,
            user.id,
        )


async def invite_tracker(db, invite):
    await db.execute(
        "UPDATE botsettings_invite SET uses=$1 WHERE code=$2", invite.uses, invite.code
    )


async def give_api_permissions(db, user, new_value):
    await db.execute(
        """UPDATE botsettings_user SET api_access=$1 WHERE id=$2""", new_value, user.id
    )


async def give_premium(db, user, new_value):
    await db.execute(
        """UPDATE botsettings_user SET premium=$1 WHERE id=$2""", new_value, user.id
    )


async def update_persistent_roles(db, member):
    try:
        await db.execute(
            """INSERT INTO botsettings_guildroles (roles, guild_id, member_id) VALUES ($1, $2, $3)
                         ON CONFLICT (guild_id, member_id) DO UPDATE SET roles=excluded.roles""",
            [role.id for role in member.roles],
            member.guild.id,
            member.id,
        )
    except:
        try:
            await add_user(db, member)
            await add_guild(db, member.guild)
            await update_persistent_roles(db, member)
        except:
            pass
