import asyncio
import datetime

import discord
from dateutil.relativedelta import relativedelta
from discord.ext import commands
from Functions.registration import *
from Checks.bot_checks import can_embed, can_manage_user, can_delete
from Formats.formats import avatar_check, pagify
from Lines.custom_emotes import CustomEmotes as Get_emote

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
    "Agender",
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


class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def permission_check(ctx):
        if not can_manage_user(ctx, ctx.author) and not ctx.guild.owner:
            await ctx.send(
                "I can not manage your roles, therefore I can not grant you any roles when you register, Please fix this and retry again!"
            )
            return False
        else:
            return True

    @staticmethod
    async def registered_check(ctx):
        registered_role = discord.utils.get(ctx.guild.roles, name="Registered")
        if registered_role in ctx.author.roles:
            await ctx.send(
                "It looks like you've already registered on this server! You cannot register twice!\n"
                "If you need to reregister you can ``furunregister``!"
            )
            return False
        else:
            return True, registered_role

    async def reg_data(self, ctx):
        async with ctx.bot.pool.acquire() as db:
            register_db = await db.fetchrow(
                """SELECT registration_output, registration_enabled FROM botsettings_guild WHERE id=$1""",
                ctx.guild.id,
            )
            if register_db["registration_output"]:
                channel = int(register_db["registration_output"])
                return register_db["registration_enabled"], channel
            else:
                await ctx.send(
                    "It appears that the registration channel has not been set."
                    " Please see https://sheri.bot/settings to set this."
                )
                return False

    async def reg_channel_check(self, ctx, channel):
        discord_text_channel = self.bot.get_channel(int(channel))
        if not discord_text_channel:
            await ctx.send(
                "I cannot see/send messages in the channel set on the dashboard. Are you sure it exists?"
            )
            return False
        else:
            return True

    @staticmethod
    async def reg_role_checks(ctx, roles):
        total_roles = len(roles)
        invalid_role_count = 0
        invalid_roles = ""
        for role_name in roles:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                invalid_roles += f"{role_name}\n"
                invalid_role_count += 1

        # Role Message
        invalid_roles_beginning = (
            f"There are {total_roles} roles needed for the "
            f"registration to work and {invalid_role_count} roles are non-existant.\n"
            f"The roles that are missing are:\n"
        )
        invalid_roles_end = (
            "You can fix these automatically with the command ``regroles``"
        )
        invalid_role_build = invalid_roles_beginning + invalid_roles + invalid_roles_end
        if invalid_role_count == 0:
            return True
        else:
            await ctx.send(invalid_role_build)
            return False



    @commands.guild_only()
    @commands.command(name="register")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def register(self, ctx):
        # Added so the PM sentry error can shutdapucup
        try:
            if not ctx.guild:
                return await ctx.author.send("Registration must be done in a server!")

            config = await ctx.pool.fetchrow(
                "SELECT registration_output, registration_channel,  registration_enabled, registration_channel_lock,"
                " registration_cleanup_toggle,"
                " registration_nsfw FROM botsettings_guild WHERE id=$1", ctx.guild.id)
            # Variables to carry at the end
            correct_channel = None
            output = None
            channel = None
            sexual_questions = None
            explict_content = None
            information = ""
            give_roles = []
            registered = await self.registered_check(ctx)
            if config['registration_enabled'] is False:
                return await ctx.send("registration is currently not enabled on this server.")

            # Output Channel Check/Collection
            if config['registration_output']:
                output = ctx.guild.get_channel(config['registration_output'])
                if output is None:
                    return await ctx.send(
                        "It appears that I cannot use the current channel that has been set for the registration output. "
                        "Permissions?? Does it even exist???")
            else:
                return await ctx.send("It appears that someone has not configured registration system at all, "
                                      "please visit https://sheri.bot/ to configure the registration system.")

            # Reg Channel Lock Check/Collection
            if config['registration_channel_lock']:
                if config['registration_channel']:
                    channel = ctx.guild.get_channel(config['registration_channel'])
                    if channel is None:
                        return await ctx.send(
                            "It appears that the register channel set in the database cannot be used.")
                else:
                    return await ctx.send(
                        "Someone didn't configure the channel for the channel lock in registration, Please see "
                        "https://sheri.bot/settings to configure it.")
                if channel.id == ctx.channel.id:
                    correct_channel = True
                else:
                    correct_channel = False
                if not correct_channel:
                    return await ctx.send(
                        f"**{ctx.author.name}**, You are only allowed to register in {channel.mention}.")

            # Role checks w/ NSFW
            if config['registration_nsfw']:
                if not await self.reg_role_checks(ctx, nsfw_sfw_roles):
                    return

            # Role checks w/o NSFW
            if not config['registration_nsfw']:
                if not await self.reg_role_checks(ctx, sfw_roles):
                    return

            # Permission Checker
            if not can_manage_user(ctx, ctx.author) and not ctx.guild.owner:
                return await ctx.send(
                    "I cannot manage your roles, therefore I cannot grant you any roles when you register, Please notfify "
                    "a server admin "
                    "and retry again!")

            # Begin the registration embed
            registered_embed = discord.Embed(color=self.bot.color,
                                             title=f"{ctx.author.display_name}'s Registration",
                                             description=f"Discord User ID: {ctx.author.id}")
            if registered:
                if config['registration_cleanup_toggle']:
                    try:
                        await ctx.send(
                            f"Please make sure your direct messages are open **{ctx.author.name}** as I will "
                            f"direct message you to collect your info.\n"
                            f"Do **NOT** lie, as this can get you __banned__ or __penalized__.", delete_after=15)
                        if can_delete(ctx):
                            await ctx.message.delete()
                    except discord.NotFound:
                        pass
                else:
                    await ctx.send(f"Please make sure your direct messages are open **{ctx.author.name}** as I will "
                                   f"direct message you to collect your info.\n"
                                   f"Do **NOT** lie, as this can get you __banned__ or __penalized__.")

                # Dm Check
                def check(m):
                    return (
                            isinstance(m.channel, discord.DMChannel)
                            and m.author == ctx.author
                    )

                try:
                    await ctx.author.send(
                        "__**What gender do you identify as?**__\n"
                        "The following responses are valid for this question:"
                        "```fix\n"
                        "Male | Female | Genderfluid | Agender | Non-Binary | Transgender | Transgender Male | Transgender Female,"
                        "```")
                except discord.Forbidden:
                    return await ctx.send(
                        f"It appears that I cannot DM you due to your privacy settings, {ctx.author.mention}!\n"
                        "Please update your privacy settings. You can revert "
                        "your settings once registration is complete. "
                    )
                # Gender Question
                while True:
                    try:
                        response = await ctx.bot.wait_for(
                            "message", timeout=60, check=check
                        )
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took to long, Please rerun the register command."
                        )
                    options = [
                        "male",
                        "female",
                        "genderfluid",
                        "agender",
                        "non-binary",
                        "transgender",
                        "trangender male",
                        "transgender female",
                    ]
                    if response.content.lower() not in options:
                        await ctx.author.send("Invalid response.")
                    else:
                        if response.content.lower() == "male":
                            role = discord.utils.get(
                                ctx.guild.roles, name="Male"
                            )
                            give_roles.append(role)
                            information += "Gender: ``Male``\n"
                        elif response.content.lower() == "female":
                            role = discord.utils.get(
                                ctx.guild.roles, name="Female"
                            )
                            give_roles.append(role)
                            information += "Gender: ``Female``\n"
                        elif response.content.lower() == "genderfluid":
                            role = discord.utils.get(
                                ctx.guild.roles, name="Genderfluid"
                            )
                            give_roles.append(role)
                            information += "Gender: ``Genderfluid``\n"
                        elif response.content.lower() == "agender":
                            role = discord.utils.get(
                                ctx.guild.roles, name="Agender"
                            )
                            give_roles.append(role)
                            information += "Gender: ``Agender``\n"
                        elif response.content.lower() == "non-binary":
                            role = discord.utils.get(
                                ctx.guild.roles, name="Non-binary"
                            )
                            give_roles.append(role)
                            information += "Gender: ``Non-Binary``\n"
                        elif response.content.lower() == "transgender":
                            role = discord.utils.get(
                                ctx.guild.roles, name="Transgender"
                            )
                            give_roles.append(role)
                            information += "Gender: ``Transgender``\n"
                        elif (
                                response.content.lower()
                                == "transgender male"
                        ):
                            ge_roles = ["Male", "Transgender"]
                            for x in ge_roles:
                                role = discord.utils.get(
                                    ctx.guild.roles, name=x
                                )
                                give_roles.append(role)
                            information += "Gender: ``Transgender Male``\n"
                        elif (
                                response.content.lower()
                                == "transgender female"
                        ):
                            ge_roles = ["Female", "Transgender"]
                            for x in ge_roles:
                                role = discord.utils.get(
                                    ctx.guild.roles, name=x
                                )
                                give_roles.append(role)
                            information += "Gender: ``Transgender Female``\n"
                        break
                    if not response:
                        break

                # Rules Question
                await ctx.author.send(
                    f"**__Have you read the rules of ``{ctx.guild.name}`` and will comply with them?__**\n"
                    "The following responses are valid for this question:\n"
                    "```fix\n"
                    "Yes | No```")
                while True:
                    try:
                        response = await ctx.bot.wait_for(
                            "message", timeout=60, check=check
                        )
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took to long, Please rerun the register command."
                        )

                    options = ["yes", "no"]

                    if response.content.lower() not in options:
                        await ctx.author.send("Invalid response.")
                    else:
                        if response.content.lower() == "yes":
                            pass
                        elif response.content.lower() == "no":
                            return await ctx.author.send(
                                "You better go and read the rules and rerun registration"
                            )
                        break
                    if not response:
                        break

                # Direct Message Question
                await ctx.author.send("**__Are you okay with being directly messaged?__**\n"
                                      "The following responses are valid for this question:\n"
                                      "```fix\n"
                                      "Yes | No | Ask```")
                while True:
                    options = ["yes", "no", "ask"]
                    try:
                        response = await ctx.bot.wait_for(
                            "message", timeout=60, check=check
                        )
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took to long, Please rerun the register command."
                        )
                    if response.content.lower() not in options:
                        await ctx.author.send("Invalid response.")
                    else:
                        if response.content.lower() == "yes":
                            role = discord.utils.get(
                                ctx.guild.roles, name="DMs Allowed"
                            )
                            give_roles.append(role)
                            information += "Direct Messages: ``Yes``\n"
                        elif response.content.lower() == "no":
                            role = discord.utils.get(
                                ctx.guild.roles, name="DMs NOT Allowed"
                            )
                            give_roles.append(role)
                            information += "Direct Messages: ``No``\n"
                        elif response.content.lower() == "ask":
                            role = discord.utils.get(
                                ctx.guild.roles, name="Ask to DM"
                            )
                            give_roles.append(role)
                            information += "Direct Messages: ``Ask First``\n"
                        break
                    if not response:
                        break

                # Mention Question
                await ctx.author.send("__**Are you okay with being mentioned?**__\n"
                                      "The following responses are valid for this question:\n"
                                      "```fix\n"
                                      "Yes | No```")
                while True:
                    options = ["yes", "no"]
                    try:
                        response = await ctx.bot.wait_for(
                            "message", timeout=60, check=check
                        )
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took to long, Please rerun the register command."
                        )
                    if response.content.lower() not in options:
                        await ctx.author.send("Invalid response.")
                    else:
                        if response.content.lower() == "yes":
                            role = discord.utils.get(
                                ctx.guild.roles, name="Mention"
                            )
                            give_roles.append(role)
                            information += "Mentions: ``Yes``\n"
                        elif response.content.lower() == "no":
                            role = discord.utils.get(
                                ctx.guild.roles, name="No Mention"
                            )
                            give_roles.append(role)
                            information += "Mentions: ``No``\n"
                        break
                    if not response:
                        break

                # Age Question
                await ctx.author.send(
                    "__**What is your date of birth?**__\n"
                    "The current valid date format is ``MM/DD/YYYY``\n"
                    "An example of the date format is: ``11/01/1900``\n"
                    "Do **NOT** Lie about your age, it can get you into some **SERIOUS** trouble."
                )
                while True:
                    try:
                        response = await ctx.bot.wait_for(
                            "message", timeout=60, check=check
                        )
                        bd_datetime = datetime.datetime.strptime(
                            response.content, "%m/%d/%Y"
                        )
                        delta = relativedelta(
                            datetime.datetime.now(), bd_datetime
                        )
                        if int(delta.years) >= 69:
                            return await ctx.author.send("HA, you're funny! And I'm 1,000 years old!")
                        if int(delta.years) >= 18:
                            role = discord.utils.get(
                                ctx.guild.roles, name="18+"
                            )
                            give_roles.append(role)
                            information += f"Age: ``{delta.years}`` Years\n"
                        elif int(delta.years) <= 17:
                            role = discord.utils.get(
                                ctx.guild.roles, name="Underage"
                            )
                            give_roles.append(role)
                            information += f"Age: ``{delta.years}`` Years\n"
                        break

                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took to long, Please rerun the register command."
                        )
                    except ValueError:
                        return await ctx.author.send(
                            "Invalid Birthday, Due to a bug, You will need to rerun registeration.")

                if discord.utils.get(ctx.guild.roles, name="18+") in give_roles:

                    # RelationShip Status
                    await ctx.author.send(
                        "Are you currently Taken, Single, Seeking for a partner or Single, Not seeking for a partner?"
                        "The valid responses in this question are:\n"
                        "```fix\n"
                        "Taken | Single, seeking for partner | single, not seeking for partner```"
                    )
                    while True:
                        options = [
                            "single, seeking for partner",
                            "single, not seeking for partner",
                            "taken"
                        ]

                        try:
                            response = await ctx.bot.wait_for(
                                "message", timeout=60, check=check
                            )
                        except asyncio.TimeoutError:
                            return await ctx.author.send(
                                "Registration has timed out."
                            )
                        if response.content.lower() not in options:
                            await ctx.author.send("Invalid response.")
                        else:
                            if response.content.lower() == "taken":
                                role = discord.utils.get(
                                    ctx.guild.roles, name="Taken"
                                )
                                give_roles.append(role)
                                information += "Relationship: ``Taken``\n"
                            elif response.content.lower() == "single, seeking for partner":
                                role = discord.utils.get(
                                    ctx.guild.roles,
                                    name="Seeking for partner",
                                )
                                role_2 = discord.utils.get(
                                    ctx.guild.roles, name="Single"
                                )
                                give_roles.append(role)
                                give_roles.append(role_2)
                                information += "Relationship: ``Single and ready to mingle``\n"
                            elif response.content.lower() == "single, not seeking for partner":
                                role = discord.utils.get(
                                    ctx.guild.roles,
                                    name="Not seeking for partner",
                                )
                                role_2 = discord.utils.get(
                                    ctx.guild.roles, name="Single"
                                )
                                give_roles.append(role)
                                give_roles.append(role_2)
                                information += "Relationship: ``Single and not ready to mingle``\n"
                            break
                        if not response:
                            break
                    if config['registration_nsfw']:
                        # Sexual Content Question
                        await ctx.author.send(
                            f"**__Do you want to view explict content in ``{ctx.guild.name}``?__**\n"
                            "The valid responses for this question are:\n"
                            "```fix\n"
                            "Yes | No```")
                        while True:
                            options = ["yes", "no"]
                            try:
                                response = await ctx.bot.wait_for(
                                    "message", timeout=60, check=check
                                )
                            except asyncio.TimeoutError:
                                return await ctx.author.send(
                                    "You took to long, Please rerun the register command."
                                )
                            if response.content.lower() not in options:
                                await ctx.author.send("Invalid response.")
                            else:
                                if response.content.lower() == "yes":
                                    role = discord.utils.get(
                                        ctx.guild.roles, name="NSFW"
                                    )
                                    give_roles.append(role)
                                elif response.content.lower() == "no":
                                    pass
                                break
                            if not response:
                                break

                        # Sexual Question Answers
                        await ctx.author.send(
                            "**__Would you like to answer some questions concerning"
                            " your sexuality and preference of sexual position?__**\n"
                            "The valid responses for this question are:\n"
                            "```fix\n"
                            "Yes | No```"
                        )
                        while True:
                            options = ["yes", "no"]
                            try:
                                response = await ctx.bot.wait_for(
                                    "message", timeout=60, check=check
                                )
                            except asyncio.TimeoutError:
                                return await ctx.author.send(
                                    "Registration has timed out."
                                )
                            if response.content.lower() not in options:
                                await ctx.author.send(
                                    "Invalid response."
                                )
                            else:
                                if response.content.lower() == "yes":
                                    sexual_questions = True
                                elif response.content.lower() == "no":
                                    sexual_questions = False
                                break
                            if not response:
                                break

                        if sexual_questions:
                            # Sexual Orientation Question
                            await ctx.author.send(
                                "**__What is your sexual orientation.__**\n"
                                "The valid responses for this question are:\n"
                                "```fix\n"
                                "Asexual | Bisexual | Gay | Lesbian | Pansexual | Straight | Aromantic```")
                            while True:
                                options = [
                                    "asexual",
                                    "bisexual",
                                    "gay",
                                    "lesbian",
                                    "pansexual",
                                    "straight",
                                    "aromantic",
                                ]
                                try:
                                    response = await ctx.bot.wait_for(
                                        "message",
                                        timeout=60,
                                        check=check,
                                    )
                                except asyncio.TimeoutError:
                                    return await ctx.author.send(
                                        "Registration has timed out."
                                    )
                                if response.content.lower() not in options:
                                    await ctx.author.send(
                                        "Invalid response."
                                    )
                                else:
                                    if response.content.lower() == "asexual":
                                        role = discord.utils.get(
                                            ctx.guild.roles,
                                            name="Asexual",
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Orientation: ``Asexual``\n"
                                    elif response.content.lower() == "bisexual":
                                        role = discord.utils.get(
                                            ctx.guild.roles,
                                            name="Bisexual",
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Orientation: ``Bisexual``\n"
                                    elif response.content.lower() == "gay":
                                        role = discord.utils.get(
                                            ctx.guild.roles, name="Gay"
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Orientation: ``Gay``\n"
                                    elif response.content.lower() == "lesbian":
                                        role = discord.utils.get(
                                            ctx.guild.roles,
                                            name="Lesbian",
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Orientation: ``Lesbian``\n"
                                    elif response.content.lower() == "pansexual":
                                        role = discord.utils.get(
                                            ctx.guild.roles,
                                            name="Pansexual",
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Orientation: ``Pansexual``\n"
                                    elif response.content.lower() == "straight":
                                        role = discord.utils.get(
                                            ctx.guild.roles,
                                            name="Straight",
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Orientation: ``Straight``\n"
                                    elif response.content.lower() == "aromantic":
                                        role = discord.utils.get(
                                            ctx.guild.roles,
                                            name="Aromantic",
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Orientation: ``Aromantic``\n"
                                    break
                                if not response:
                                    break

                            # Sexual Position Question
                            await ctx.author.send(
                                "__**What sexual position do you prefer?**__"
                                "The valid responses for this question are:\n"
                                "```fix\n"
                                "Dominant | Submissive | Switch | Rather Not say | Neither```")
                            while True:
                                options = [
                                    "dominant",
                                    "submissive",
                                    "switch",
                                    "neither",
                                    "rather not say",
                                ]
                                try:
                                    response = await ctx.bot.wait_for(
                                        "message",
                                        timeout=60,
                                        check=check,
                                    )
                                except asyncio.TimeoutError:
                                    return await ctx.author.send(
                                        "Registration has timed out."
                                    )
                                if response.content.lower() not in options:
                                    await ctx.author.send(
                                        "Invalid response."
                                    )
                                else:
                                    if response.content.lower() == "dominant":
                                        role = discord.utils.get(
                                            ctx.guild.roles,
                                            name="Dominant",
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Position: ``Dominant``\n"
                                    elif (
                                            response.content.lower()
                                            == "submissive"
                                    ):
                                        role = discord.utils.get(
                                            ctx.guild.roles,
                                            name="Submissive",
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Position: ``Submissive``\n"
                                    elif (
                                            response.content.lower()
                                            == "switch"
                                    ):
                                        role = discord.utils.get(
                                            ctx.guild.roles,
                                            name="Switch",
                                        )
                                        give_roles.append(role)
                                        information += "Sexual Position: ``Switch``\n"
                                    elif (
                                            response.content.lower()
                                            == "rather not say"
                                    ):
                                        information += "Sexual Position: ``Rather not say``\n"
                                    elif (
                                            response.content.lower()
                                            == "neither"
                                    ):
                                        information += "Sexual Position: ``Neither``\n"
                                    break
                                if not response:
                                    break

                # Introduction
                registered_embed.add_field(name="User's Information",
                                           value=information)
                await ctx.author.send("**__Would you like to introduce yourself?__**\n"
                                      "```fix\n"
                                      "YES | NO```")
                while True:
                    options = [
                        "yes",
                        "no"
                    ]
                    try:
                        response = await ctx.bot.wait_for(
                            "message",
                            timeout=60,
                            check=check,
                        )
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "Registration has timed out."
                        )
                    if response.content.lower() not in options:
                        await ctx.author.send(
                            "Invalid response."
                        )
                    else:
                        if response.content.lower() == "yes":
                            await ctx.author.send(
                                content="Please introduce yourself to me in this direct message.\n"
                                        "After you have introduced yourself, Your registration will be completed.\n"
                                        "If at any time you need to change/adjust/update your registration, "
                                        "You can furunregister and reregister again."
                            )
                            try:
                                response = await ctx.bot.wait_for(
                                    "message", timeout=1600, check=check
                                )
                            except asyncio.TimeoutError:
                                registered_embed.add_field(
                                    name="About:", value="A mysterious person..."
                                )
                            else:
                                pagenum = 0
                                pages = pagify(response.content, None, 0, 1000)
                                for page in pages:
                                    pagenum += 1
                                    registered_embed.add_field(
                                        name=f"About{' (continued):' if pagenum > 1 else ':'}",
                                        value=page,
                                        inline=False,
                                    )
                                    give_roles.append(registered[1])
                                    await ctx.author.send(
                                        "Thank you, Your registration is now completed. You may now browse the server."
                                    )
                                    if can_embed(guild=ctx.guild, channel=output):
                                        registered_embed.set_thumbnail(url=avatar_check(ctx.author))
                                        await output.send(embed=registered_embed)
                                    await ctx.author.add_roles(
                                        *give_roles, reason="Registration")
                        elif response.content.lower() == "no":
                            give_roles.append(registered[1])
                            await ctx.author.send(
                                "Thank you, Your registration is now completed. You may now browse the server.")
                            if can_embed(guild=ctx.guild, channel=output):
                                registered_embed.set_thumbnail(url=avatar_check(ctx.author))
                                await output.send(embed=registered_embed)
                            await ctx.author.add_roles(*give_roles, reason="Registration")
                        break
                    if not response:
                        break
        except discord.Forbidden:
            return


def setup(bot):
    bot.add_cog(Register(bot))
