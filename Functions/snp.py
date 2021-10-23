import discord

from Checks.bot_checks import can_embed, can_send
from Functions.reactions import upvote_downvote_reactions


async def manage_mention(guild, role, mention):
    role_to_edit = discord.utils.get(guild.roles, id=role)
    try:
        try:
            if mention:
                await role_to_edit.edit(mentionable=True, reason="Smash or Pass")
                return role_to_edit.mention
            else:
                await role_to_edit.edit(mentionable=False, reason="Smash or Pass")
        except TypeError:
            pass
    except discord.Forbidden:
        message = "Permission error on role EDIT"
        return message


async def send_smash_n_pass(role_enabled: bool, role: discord.Role, guild, channel, embed):
    if channel.is_nsfw():
        if can_send(guild=guild, channel=channel) and can_embed(
                guild=guild, channel=channel
        ):
            if role_enabled:
                mention = await manage_mention(
                    guild, role, mention=True
                )
                if mention == "DELETED":
                    return await channel.send(
                        "There was an error posting the next smash n pass.\n"
                        "The error is geared to a nonexistent role!\n"
                        "Please reset and readd the role. "
                        "I will continue to attempt to post the smash n pass without pings now."
                    )
                message = await channel.send(
                    embed=embed,
                    content=f"{mention}\n"
                            "The next smash or pass will be in 12 hours.",
                )
                await upvote_downvote_reactions(channel, message)
                await manage_mention(
                    guild, role, mention=False
                )
            else:
                message = await channel.send(embed=embed)
                await upvote_downvote_reactions(channel, message)
