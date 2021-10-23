import ujson
import discord

# Roles needed for the register system to function
roles = [
    "Male",
    "Female",
    "Agender",
    "Genderfluid",
    "Transgender",
    "Non-binary",
    "Agender",
    "Asexual",
    "Bisexual",
    "Gay",
    "Lesbian",
    "Pansexual",
    "Straight",
    "Aromantic",
    "Taken",
    "Single",
    "Mention",
    "No Mention",
    "18+",
    "Underage",
    "Registered",
    "Dominant",
    "Submissive",
    "Switch",
    "DMs NOT Allowed",
    "DMs Allowed",
    "Ask to DM",
    "Seeking for partner",
    "Not seeking for partner",
    "NSFW",
]
nsfw_roles = [
    "Dominant",
    "Submissive",
    "Switch",
    "Asexual",
    "Bisexual",
    "Gay",
    "Lesbian",
    "Pansexual",
    "Straight",
    "Aromantic",
    "NSFW",
]

sfw_roles = [
    "Male",
    "Female",
    "Agender",
    "Genderfluid",
    "Transgender",
    "Non-binary",
    "Registered",
    "DMs NOT Allowed",
    "DMs Allowed",
    "Ask to DM",
    "Taken",
    "Single",
    "Seeking for partner",
    "Not seeking for partner",
    "Mention",
    "No Mention",
    "18+",
    "Underage"
]

nsfw_sfw_roles = nsfw_roles + sfw_roles


async def load_registration_roles(ctx):
    guild_data = await ctx.pool.fetchrow(
        'select registration_roles from botsettings_guild where id=$1',
        ctx.guild.id)
    if guild_data['registration_roles'] == {} or guild_data['registration_roles'] is None:
        return False
    reg_roles = {}
    for rolename, roleid in ujson.loads(guild_data['registration_roles']).items():
        guild_role = ctx.guild.get_role(roleid)
        if guild_role is None:
            return False
        reg_roles[rolename] = guild_role
    return reg_roles


async def add_registration_roles(ctx):
    guild_data = await ctx.pool.fetchrow(
        f"select registration_nsfw from botsettings_guild where id={ctx.guild.id}")
    role_dict = dict()
    guild_roles = ctx.guild.roles
    if guild_data['registration_nsfw']:
        roles = nsfw_sfw_roles
    else:
        roles = sfw_roles
    for role in roles:
        for guild_role in guild_roles:
            if guild_role.name == role:
                role_dict[role] = guild_role.id
    await ctx.pool.execute(f"update botsettings_guild set registration_roles=$1, registration_roles_setup=$3 where id=$2",
                           ujson.dumps(role_dict), ctx.guild.id, True)


async def registration_output(ctx):
    reg_output = await ctx.pool.fetchval('select registration_output from botsettings_guild where id=$1',
                                         ctx.guild.id)
    try:
        channel = ctx.guild.get_channel(reg_output)
        if channel is None:
            await ctx.send("The channel you selected for registration output is non existent")
            return None
        else:
            return channel
    except discord.NotFound:
        await ctx.send("The channel you selected for registration output is non existent")
        return None
