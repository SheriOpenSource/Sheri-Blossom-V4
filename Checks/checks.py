import discord
from discord.ext import commands

'''notes to all developers under no circumstances are we to hard code'''

async def is_owner(ctx: commands.context):
    are_owner = await ctx.pool.fetchval("SELECT owner FROM botsettings_user WHERE id=$1",
                                        ctx.author.id)
    if are_owner:
        return True
    else:
        await ctx.send("You're not my master!")
        return False


async def is_dev(ctx: commands.context):
    permissions = await ctx.pool.fetchrow("SELECT owner, developer FROM botsettings_user WHERE id=$1",
                                          ctx.author.id)
    if permissions['owner']:
        return True
    elif permissions['developer']:
        return True
    else:
        await ctx.send("You're not one of my developers!")
        return False


def is_staff_check(self, ctx):
    yiff_yiff = self.bot.home
    if ctx.message.author not in yiff_yiff.members:
        return False
    return 484003210739318785 in [
        r.id
        for r in [x for x in yiff_yiff.members if x.id == ctx.message.author.id][
            0
        ].roles
    ]


def is_staff():
    return commands.check(is_staff_check)


async def donor_check(ctx: commands.Context):
    cmd = ctx.command.name
    async with ctx.bot.pool.acquire() as db:
        donor_status = await db.fetchval(
            """SELECT premium FROM botsettings_user WHERE id=$1""", ctx.author.id
        )
        if donor_status:
            return True
        else:
            await ctx.send(
                f"{cmd} is a donor command. If you want to become a donor and help keep me online, "
                f"visit <https://sheri.bot/>. <:SheriLove:592375692956663808>"
            )


async def premium_guild_check(ctx: commands.Context):
    async with ctx.bot.pool.acquire() as db:
        premium = await db.fetchval(
            "SELECT premium FROM botsettings_guild WHERE id=$1", ctx.guild.id
        )
        if premium:
            return True
        if not premium:
            await ctx.send(
                "I'm sorry, Your server does not have premium.\n"
                "You can't use the auto poster on this server until you have premium for this server.\n"
                "<https://patreon.sheri.bot> | <https://invite.sheri.bot/>"
            )


async def premium_level_2(ctx: commands.Context):
    cmd = ctx.command.name
    if ctx.author in ctx.bot.home.members:
        role = discord.utils.get(ctx.bot.home.roles, id=459143362080145408)
        nitro = discord.utils.get(ctx.bot.home.roles, id=585529512008089602)
        if ctx.author in role.members or ctx.author in nitro.members:
            return True
        else:
            await ctx.send(
                f"You are currently not a $10 dollar donor, or a nitro booster in {ctx.bot.home.name}"
            )
    else:
        await ctx.send(f"You need to be in sheri's hangout to use this {cmd}!")


def check_permissions(ctx, perms):
    if is_owner(ctx):
        return True
    elif not perms:
        return False
    ch = ctx.message.channel
    author = ctx.message.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())


def role_or_permissions(ctx, check, **perms):
    if check_permissions(ctx, perms):
        return True
    ch = ctx.message.channel
    if isinstance(ch, discord.abc.PrivateChannel):
        return False
    if check:
        return True


def mod_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(
            ctx,
            ctx.message.author.permissions_in(ctx.message.channel).manage_roles,
            **perms,
        )

    return commands.check(predicate)


def admin_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(
            ctx,
            ctx.message.author.permissions_in(ctx.message.channel).manage_guild,
            **perms,
        )

    return commands.check(predicate)


def guild_owner_or_permissions(**perms):
    def predicate(ctx):
        guild = ctx.message.guild
        if not guild:
            return False

        if ctx.message.author.id == guild.owner.id:
            return True

        return check_permissions(ctx, perms)

    return commands.check(predicate)


def guild_owner():
    return guild_owner_or_permissions()


def admin():
    return admin_or_permissions()


def mod():
    return mod_or_permissions()
