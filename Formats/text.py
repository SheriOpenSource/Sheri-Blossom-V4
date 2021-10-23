from random import choice

from Formats.chat_markdown import bold
from Lines.misc_functions import get


async def parse_level_vars(member, level, text):
    try:
        text = text.format(
            member=str(member),
            name=member.name,
            displayname=member.display_name,
            mention=member.mention,
            guild=member.guild,
            level=level,
        )
        return text
    except (KeyError, ValueError):
        return f"There was an error with the level function. Ensure that you have correctly entered your variables. " + \
        "Variables must be entered only in lowercase and enclosed in **`{curly brackets}`**. " + \
        f"Examples of these variables can be found by clicking the **`?`** on the **`Levels`** tab in your guild settings, " + \
        f"in the **`Level-Up Message`** box.\n" + \
        f"Please feel free to visit our support server for further assistance if problems persist."


async def parse_welcome_vars(text, member, guild):
    try:
        text = text.format(
            name=str(member),
            mention=member.mention,
            member=member,
            random_join=choice(get["welcomes"]["Join"]).format(bold(member.name)),
            random_leave=choice(get["welcomes"]["Leave"]).format(bold(member.name)),
            guild=guild.name,
            displayname=member.display_name,
            guild_count_all=str(guild.member_count),
            guild_count_users=str(
                len([member for member in guild.members if not member.bot])
            ),
            guild_count_bots=str(
                len([member for member in guild.members if member.bot])
            ),
        )
        return text
    except (KeyError, ValueError):
        return f"There was an error with the welcome function. Ensure that you have correctly entered your variables. " + \
        "Variables must be entered only in lowercase and enclosed in **`{curly brackets}`**. " + \
        f"Examples of these variables can be found by clicking the **`message guide`** link on the **`General`** tab in your guild settings, " + \
        f"under the **`Welcome Message`** and **`Leave Message`** boxes.\n" + \
        f"Please feel free to visit our support server for further assistance if problems persist."
