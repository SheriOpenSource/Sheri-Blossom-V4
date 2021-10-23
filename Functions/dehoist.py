import discord

hoist_characters = [
    "!",
    "?",
    "[",
    "]",
    "*",
    ".",
    ",",
    "(",
    ")",
    "{",
    "}",
    "-",
    "+",
    "=",
    '"',
    "'",
    "`",
    "~",
    "<",
    ">",
    "/",
    "&",
    "^",
    "%",
    "#",
    "$",
    "@",
    ":",
    ";",
    "_",
    "\\",
]

zalgo_characters = [
    u"\u030d",
    u"\u030e",
    u"\u0304",
    u"\u0305",
    u"\u033f",
    u"\u0311",
    u"\u0306",
    u"\u0310",
    u"\u0352",
    u"\u0357",
    u"\u0351",
    u"\u0307",
    u"\u0308",
    u"\u030a",
    u"\u0342",
    u"\u0343",
    u"\u0344",
    u"\u034a",
    u"\u034b",
    u"\u034c",
    u"\u0303",
    u"\u0302",
    u"\u030c",
    u"\u0350",
    u"\u0300",
    u"\u030b",
    u"\u030f",
    u"\u0312",
    u"\u0313",
    u"\u0314",
    u"\u033d",
    u"\u0309",
    u"\u0363",
    u"\u0364",
    u"\u0365",
    u"\u0366",
    u"\u0367",
    u"\u0368",
    u"\u0369",
    u"\u036a",
    u"\u036b",
    u"\u036c",
    u"\u036d",
    u"\u036e",
    u"\u036f",
    u"\u033e",
    u"\u035b",
    u"\u0346",
    u"\u031a",
    u"\u0315",
    u"\u031b",
    u"\u0340",
    u"\u0341",
    u"\u0358",
    u"\u0321",
    u"\u0322",
    u"\u0327",
    u"\u0328",
    u"\u0334",
    u"\u0335",
    u"\u0336",
    u"\u034f",
    u"\u035d",
    u"\u035e",
    u"\u035f",
    u"\u0360",
    u"\u0362",
    u"\u0338",
    u"\u0337",
    u"\u0361",
    u"\u0489",
    u"\u0316",
    u"\u0317",
    u"\u0318",
    u"\u0319",
    u"\u031c",
    u"\u031d",
    u"\u031e",
    u"\u031f",
    u"\u0320",
    u"\u0324",
    u"\u0325",
    u"\u0326",
    u"\u0329",
    u"\u032a",
    u"\u032b",
    u"\u032c",
    u"\u032d",
    u"\u032e",
    u"\u032f",
    u"\u0330",
    u"\u0331",
    u"\u0332",
    u"\u0333",
    u"\u0339",
    u"\u033a",
    u"\u033b",
    u"\u033c",
    u"\u0345",
    u"\u0347",
    u"\u0348",
    u"\u0349",
    u"\u034d",
    u"\u034e",
    u"\u0353",
    u"\u0354",
    u"\u0355",
    u"\u0356",
    u"\u0359",
    u"\u035a",
    u"\u0323",
]


async def dehoist(self, member, guildID):
    async with self.bot.pool.acquire() as db:
        guild_info = await db.fetchrow(
            "SELECT * FROM botsettings_guild WHERE id=$1", member.guild.id
        )

    if not guild_info:
        return

    if guild_info["dehoist"]:
        start_index = 0
        nick = list(member.display_name)
        for character in nick:
            if character in hoist_characters:
                start_index += 1
            else:
                break
        if start_index > 0:
            await member.edit(nick=member.display_name[start_index:], reason="Dehoist")

    if guild_info["anti_zalgo"]:
        new_nick = ""
        nick = list(member.display_name)
        for character in nick:
            if character not in zalgo_characters:
                new_nick += character
        if new_nick != member.display_name:
            await member.edit(nick=new_nick, reason="Anti Zalgo")


async def auto_anti_hoist_zalgo(self, member: discord.Member, guild: discord.Guild):
    guild_info = await self.bot.pool.fetchrow(
        "SELECT dehoist, anti_zalgo FROM botsettings_guild WHERE id=$1",
        guild.id
    )

    if guild_info["dehoist"]:
        start_index = 0
        nick = list(member.display_name)
        for character in nick:
            if character in hoist_characters:
                start_index += 1
            else:
                break
        if start_index > 0:
            try:
                await member.edit(nick=member.display_name[start_index:],
                                  reason="[Auto Dehoist] - Nickname contained common hoisting characters.")
            except discord.Forbidden:
                return

    if guild_info["anti_zalgo"]:
        new_nick = ""
        nick = list(member.display_name)
        for character in nick:
            if character not in zalgo_characters:
                new_nick += character
        if new_nick != member.display_name:
            try:
                await member.edit(nick=new_nick,
                                  reason="[Auto Anti Zalgo] - Nickname contained Zalgo characters.")
            except discord.Forbidden:
                return
