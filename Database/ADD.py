from dataclasses import dataclass

from Functions.ctx import CustomContext

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


@dataclass
class Guild:
    ctx: CustomContext

    @staticmethod
    async def add_guild(ctx, guild):
        try:
            await ctx.pool.execute(
                """INSERT INTO botsettings_guild
                             (id, owner_id, prefixes, premium, premium_owner_id, logs_embed, logs_enabled,
                             registration_enabled, autoroles, autoroles_enabled, botautorole_enabled, welcome_message,
                             leave_message, welcome_leave_embed, welcome_leave_color, welcome_background,
                             welcome_type, catching_channels, catching_enabled, no_xp_channels, no_xp_roles,
                             levels_announce, levels_message, newcomer_time_limit, automod_enabled, global_automod,
                             banned_words, trigger_words, persistent_roles_enabled, selfroles, global_automod_action,
                             welcome_leave_enabled, registration_nsfw, dehoist, anti_zalgo, registration_channel_lock)
                             VALUES ($1, $2, '{}', 'f', null, 't', 'f', 'f', '{}', 'f', 'f', '', '', 't', 16761035,
                             1, 2, '{}', 'f', '{}', '{}', 'f',
                             'Congrats on leveling up **{name}**!\nYou are now level **{level}**', 120, 'f', 't', $3,
                             $4, 'f', '{}', 'warn', 'f', 't', 'f', 'f', 't')
                             ON CONFLICT DO NOTHING""",
                guild.id,
                guild.owner.id,
                banned_words,
                banned_words,
            )
            ctx.log.INFO(f"[Database Manager]: Added {guild.name} owned by {guild.owner} to the database.")
        except Exception as e:
            ctx.sentry.capture_exception(e)
