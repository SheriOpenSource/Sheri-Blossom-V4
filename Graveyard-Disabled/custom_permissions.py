import discord
from discord.ext import commands

owners = [
    173237945149423619,  # Kanin
    139800365393510400,  # Waspy,
    248294452307689473,  # Tails
    252362165456076800,  # Kyle <3
    83006253919375360,   # Atoro
    493308716427509761,  # Talvi
    106511913222955008,  # Alphy
    443276440168038401,  # Kano,
    209219778206760961,  # Jazzy
    158292798368382976,  # DeviousKR
    406707961214402568   # Spacey Da Dragon
]
owners = set(owners)


def is_owner_check(ctx):
    return ctx.author.id in owners


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


# TODO check role/db
def is_donor_check(ctx):
    return False


def is_donor():
    return commands.check(is_donor_check)


def check_permissions(ctx, perms):
    if ctx.author.id in owners:
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
            **perms
        )

    return commands.check(predicate)


def admin_or_permissions(**perms):
    def predicate(ctx):
        return role_or_permissions(
            ctx,
            ctx.message.author.permissions_in(ctx.message.channel).manage_guild,
            **perms
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


def dev():
    return is_owner_check()
