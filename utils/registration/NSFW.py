import asyncio
from utils.registration.ROLES import roles_NSFW
import discord

from Formats.formats import current_time, pagify, icon_check, avatar_check

roles = roles_NSFW


class NSFW_Questions:
    def __init__(self, bot):
        self.bot = bot

    async def ask_questions(self, ctx, member):
        print("This does get triggered.")

        sexual_questions = None
        explict_content = None
        rule_agreement = None
        age = None
        registered_role = discord.utils.get(ctx.ctx.guild.roles, name="Registered")
        try:
            valid_options = discord.Embed(color=self.bot.color)
            valid_options.set_author(
                name=f"Registration for {ctx.guild.name}",
                icon_url=icon_check(ctx.guild),
            )
            valid_options.add_field(
                name="What is your Gender?",
                value="Please choose from the valid options!",
            )
            valid_options.add_field(
                name="Valid Options",
                value="Male, Female, Genderfluid, Agender, Transgender",
            )
            valid_options.set_footer(
                text="You will receive a role based on your gender!",
                icon_url=self.bot.footer_emote,
            )
            await member.send(embed=valid_options)
        except discord.Forbidden:
            return await ctx.send(
                f"{ctx.member.mention} "
                f"It looks like you have your DMs disabled! Please enable them so I can register you."
            )

        def check(m):
            return m.channel == member.dm_channel and m.member == member

        em = discord.Embed(color=self.bot.color)
        avatar = avatar_check(member)
        em.set_author(name=f"Introduction for {member}:", icon_url=avatar)
        em.set_footer(text="ID: {} | {}".format(member.id, await current_time()))
        give_roles = []
        # Gender Question
        while True:
            options = ["male", "female", "genderfluid", "agender", "transgender"]
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await member.send(
                    "You took to long, Please rerun the register command."
                )
            if response.content.lower() not in options:
                await member.send("Invalid response.")
            else:
                if response.content.lower() == "male":
                    role = discord.utils.get(ctx.guild.roles, name="Male")
                    give_roles.append(role)
                    em.add_field(name="Gender:", value="Male")
                elif response.content.lower() == "female":
                    role = discord.utils.get(ctx.guild.roles, name="Female")
                    give_roles.append(role)
                    em.add_field(name="Gender:", value="Female")
                elif response.content.lower() == "genderfluid":
                    role = discord.utils.get(ctx.guild.roles, name="Genderfluid")
                    give_roles.append(role)
                    em.add_field(name="Gender:", value="Genderfluid")
                elif response.content.lower() == "agender":
                    role = discord.utils.get(ctx.guild.roles, name="Agender")
                    give_roles.append(role)
                    em.add_field(name="Gender:", value="Agender")
                elif response.content.lower() == "transgender":
                    role = discord.utils.get(ctx.guild.roles, name="Transgender")
                    give_roles.append(role)
                    em.add_field(name="Gender:", value="Transgender")
                break
            if not response:
                break
        # Rules question
        while True:
            options = ["yes", "no"]
            valid_options = discord.Embed(color=self.bot.color)
            valid_options.set_author(
                name=f"Registration for {ctx.guild.name}",
                icon_url=icon_check(ctx.guild),
            )
            valid_options.set_footer(
                text=f"If you haven't read the rules of {ctx.guild.name}, then do it now.",
                icon_url=self.bot.footer_emote,
            )
            valid_options.add_field(
                name="Have you read the rules and will comply with the rules?\n"
                "Failure to follow the rules can result in being removed from the server.",
                value="Please choose from the valid options!",
            )
            valid_options.add_field(name="Valid Options", value="Yes, No", inline=False)

            await member.send(embed=valid_options)
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await member.send(
                    "You took to long, Please rerun the register command."
                )
            if response.content.lower() not in options:
                await member.send("Invalid response.")
            else:
                if response.content.lower() == "yes":
                    pass
                elif response.content.lower() == "no":
                    return await member.send(
                        "You better go and read the rules and rerun registration"
                    )
                break
            if not response:
                break

        # Direct Message Question
        while True:
            options = ["yes", "no", "ask"]
            valid_options = discord.Embed(color=self.bot.color)
            valid_options.set_author(
                name=f"Registration for {ctx.guild.name}",
                icon_url=icon_check(ctx.guild),
            )
            valid_options.add_field(
                name="Are you okay with being directly messaged?",
                value="Please choose from the valid options!",
            )
            valid_options.add_field(
                name="Valid Options", value="Yes, No, Ask", inline=False
            )
            valid_options.set_footer(
                text="You will receive a role based on your response!",
                icon_url=self.bot.footer_emote,
            )
            await member.send(embed=valid_options)
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await member.send(
                    "You took to long, Please rerun the register command."
                )
            if response.content.lower() not in options:
                await member.send("Invalid response.")
            else:
                if response.content.lower() == "yes":
                    role = discord.utils.get(ctx.guild.roles, name="DMs Allowed")
                    give_roles.append(role)
                    em.add_field(name="DMs open:", value="Yes")
                elif response.content.lower() == "no":
                    role = discord.utils.get(ctx.guild.roles, name="DMs NOT Allowed")
                    give_roles.append(role)
                    em.add_field(name="DMs open:", value="No")
                elif response.content.lower() == "ask":
                    role = discord.utils.get(ctx.guild.roles, name="Ask to DM")
                    give_roles.append(role)
                    em.add_field(name="DMs open:", value="Ask first")
                break
            if not response:
                break

        #  Mentioned Question
        while True:
            options = ["yes", "no"]
            valid_options = discord.Embed(color=self.bot.color)
            valid_options.set_author(
                name=f"Registration for {ctx.guild.name}",
                icon_url=icon_check(ctx.guild),
            )
            valid_options.set_footer(
                text="You will receive a role based on your response!",
                icon_url=self.bot.footer_emote,
            )
            valid_options.add_field(
                name="Are you okay with being mentioned?",
                value="Please choose from the valid options!",
            )
            valid_options.add_field(name="Valid Options", value="Yes, No", inline=False)

            await member.send(embed=valid_options)
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await member.send(
                    "You took to long, Please rerun the register command."
                )
            if response.content.lower() not in options:
                await member.send("Invalid response.")
            else:
                if response.content.lower() == "yes":
                    role = discord.utils.get(ctx.guild.roles, name="Mention")
                    give_roles.append(role)
                    em.add_field(name="Mentions:", value="Yes")
                elif response.content.lower() == "no":
                    role = discord.utils.get(ctx.guild.roles, name="No Mention")
                    give_roles.append(role)
                    em.add_field(name="Mentions:", value="No")
                break
            if not response:
                break

        # Age Question
        while True:
            valid_options = discord.Embed(color=self.bot.color)
            valid_options.set_author(
                name=f"Registration for {ctx.guild.name}",
                icon_url=icon_check(ctx.guild),
            )
            valid_options.set_footer(
                text="You will receive a role based on your response!",
                icon_url=self.bot.footer_emote,
            )
            valid_options.add_field(
                name="How old are you?",
                value="Please be truthful! Lying can get your account BANNED or RESTRICTED!",
            )
            await member.send(embed=valid_options)
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await member.send(
                    "You took to long, Please rerun the register command."
                )
            if response.content.isdigit():
                if int(response.content) > 100 or int(response.content) < 5:
                    await member.send("Please enter a real age, not some made up age.")
                elif int(response.content) >= 18:
                    age = int(response.content)
                    role = discord.utils.get(ctx.guild.roles, name="18+")
                    give_roles.append(role)
                    em.add_field(name="Age:", value=response.content)
                elif int(response.content) <= 17:
                    age = int(response.content)
                    role = discord.utils.get(ctx.guild.roles, name="Underage")
                    give_roles.append(role)
                    em.add_field(name="Age:", value=response.content)
                break
            elif not response.content.isdigit():
                await member.send("Age must be a number!")
            if not response:
                break

        # check to see if they are 15+ for relationship status
        if discord.utils.get(ctx.guild.roles, name="18+") in give_roles:

            # Sexual Content Question
            while True:
                options = ["yes", "no"]
                valid_options = discord.Embed(color=self.bot.color)
                valid_options.set_author(
                    name=f"Registration for {ctx.guild.name}",
                    icon_url=ctx.guild.icon_url,
                )
                valid_options.set_footer(
                    text="You will receive a role based on your response!",
                    icon_url=self.bot.footer_emote,
                )
                valid_options.add_field(
                    name=f"Do you want to view explict content in {ctx.guild.name}?",
                    value="Please choose from the valid options!",
                )
                valid_options.add_field(
                    name="Valid Options", value="Yes, No", inline=False
                )

                await member.send(embed=valid_options)
                try:
                    response = await ctx.bot.wait_for(
                        "message", timeout=60, check=check
                    )
                except asyncio.TimeoutError:
                    return await member.send(
                        "You took to long, Please rerun the register command."
                    )
                if response.content.lower() not in options:
                    await member.send("Invalid response.")
                else:
                    if response.content.lower() == "yes":
                        explict_content = True
                        role = discord.utils.get(ctx.guild.roles, name="NSFW")
                        give_roles.append(role)
                    elif response.content.lower() == "no":
                        explict_content = False
                    break
                if not response:
                    break

            # RelationShip Status
            while True:
                options = [
                    "taken",
                    "single",
                    "single, seeking for partner",
                    "single, not seeking for partner",
                ]

                await member.send(
                    "Are you currently Taken or Single? "
                    "Please chose from:\n`Single`, `Taken`,"
                    "`Single, Seeking for partner`, `Single, Not seeking for partner`."
                )
                try:
                    response = await ctx.bot.wait_for(
                        "message", timeout=60, check=check
                    )
                except asyncio.TimeoutError:
                    return await member.send("Registration has timed out.")
                if response.content.lower() not in options:
                    await member.send("Invalid response.")
                else:
                    if response.content.lower() == "taken":
                        role = discord.utils.get(ctx.guild.roles, name="Taken")
                        give_roles.append(role)
                        em.add_field(name="Relationship Status:", value="Taken")
                    elif response.content.lower() == "single":
                        role = discord.utils.get(ctx.guild.roles, name="Single")
                        give_roles.append(role)
                        em.add_field(name="Relationship Status:", value="Single")
                    elif response.content.lower() == "single, seeking for partner":
                        role = discord.utils.get(
                            ctx.guild.roles, name="Seeking for partner"
                        )
                        role_2 = discord.utils.get(ctx.guild.roles, name="Single")
                        give_roles.append(role)
                        give_roles.append(role_2)
                        em.add_field(
                            name="Relationship Status:",
                            value="Single - Seeking for partner",
                        )
                    elif response.content.lower() == "single, not seeking for partner":
                        role = discord.utils.get(
                            ctx.guild.roles, name="Not seeking for partner"
                        )
                        role_2 = discord.utils.get(ctx.guild.roles, name="Single")
                        give_roles.append(role)
                        give_roles.append(role_2)
                        em.add_field(
                            name="Relationship Status:",
                            value="Single - Not seeking for partner",
                        )
                    break
                if not response:
                    break

        if explict_content:

            # Should Sexual questions be given?
            while True:
                options = ["yes", "no"]
                await member.send(
                    "Would you like to answer some questions concerning"
                    " your sexuality and preference of sexual position?\n"
                    "Please choose from ``Yes`` or ``No``."
                )
                try:
                    response = await ctx.bot.wait_for(
                        "message", timeout=60, check=check
                    )
                except asyncio.TimeoutError:
                    return await member.send("Registration has timed out.")
                if response.content.lower() not in options:
                    await member.send("Invalid response.")
                else:
                    if response.content.lower() == "yes":
                        sexual_questions = True
                    elif response.content.lower() == "no":
                        sexual_questions = False
                    break
                if not response:
                    break

            # Check to see if sexual questions are true
            if sexual_questions:
                # Sexual Orientation Question
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
                    await member.send(
                        "What is your sexual orientation."
                        " Please choose from:\n`Asexual`, `Bisexual`, `Pansexual`,"
                        " `Lesbian`, `Aromantic`, `Gay`, or `Straight`."
                    )
                    try:
                        response = await ctx.bot.wait_for(
                            "message", timeout=60, check=check
                        )
                    except asyncio.TimeoutError:
                        return await member.send("Registration has timed out.")
                    if response.content.lower() not in options:
                        await member.send("Invalid response.")
                    else:
                        if response.content.lower() == "asexual":
                            role = discord.utils.get(ctx.guild.roles, name="Asexual")
                            give_roles.append(role)
                            em.add_field(name="Sexual Orientation:", value="Asexual")
                        elif response.content.lower() == "bisexual":
                            role = discord.utils.get(ctx.guild.roles, name="Bisexual")
                            give_roles.append(role)
                            em.add_field(name="Sexual Orientation", value="Bisexual")
                        elif response.content.lower() == "gay":
                            role = discord.utils.get(ctx.guild.roles, name="Gay")
                            give_roles.append(role)
                            em.add_field(name="Sexual Orientation", value="Gay")
                        elif response.content.lower() == "lesbian":
                            role = discord.utils.get(ctx.guild.roles, name="Lesbian")
                            give_roles.append(role)
                            em.add_field(name="Sexual Orientation", value="Lesbian")
                        elif response.content.lower() == "pansexual":
                            role = discord.utils.get(ctx.guild.roles, name="Pansexual")
                            give_roles.append(role)
                            em.add_field(name="Sexual Orientation", value="Pansexual")
                        elif response.content.lower() == "straight":
                            role = discord.utils.get(ctx.guild.roles, name="Straight")
                            give_roles.append(role)
                            em.add_field(name="Sexual Orientation", value="Straight")
                        elif response.content.lower() == "aromantic":
                            role = discord.utils.get(ctx.guild.roles, name="Aromantic")
                            give_roles.append(role)
                            em.add_field(name="Sexual Orientation", value="Aromantic")
                        break
                    if not response:
                        break

                # Sexual Position Question
                while True:
                    options = ["dominant", "submissive", "switch", "neither"]
                    await member.send(
                        "What sexual position do you prefer?"
                        " Please chose from:\n`Dominant`, `Submissive`, or `Switch`."
                    )
                    try:
                        response = await ctx.bot.wait_for(
                            "message", timeout=60, check=check
                        )
                    except asyncio.TimeoutError:
                        return await member.send("Registration has timed out.")
                    if response.content.lower() not in options:
                        await member.send("Invalid response.")
                    else:
                        if response.content.lower() == "dominant":
                            role = discord.utils.get(ctx.guild.roles, name="Dominant")
                            give_roles.append(role)
                            em.add_field(name="Sexual Position:", value="Dominant")
                        elif response.content.lower() == "submissive":
                            role = discord.utils.get(ctx.guild.roles, name="Submissive")
                            give_roles.append(role)
                            em.add_field(name="Sexual Position", value="Submissive")
                        elif response.content.lower() == "switch":
                            role = discord.utils.get(ctx.guild.roles, name="Switch")
                            give_roles.append(role)
                            em.add_field(name="Sexual Position", value="Switch")
                        elif response.content.lower() == "rather not say":
                            em.add_field(name="Sexual Position", value="Rather not say")
                        elif response.content.lower() == "neither":
                            em.add_field(name="Sexual Position", value="Neither")
                        break
                    if not response:
                        break

        await member.send(
            "Please briefly introduce yourself!\n"
            "After you introduce yourself, your registration will be completed"
        )
        try:
            response = await ctx.bot.wait_for("message", timeout=500, check=check)
        except asyncio.TimeoutError:
            em.add_field(name="Info:", value="A mysterious person...")
        else:
            pagenum = 0
            pages = pagify(response.content, None, 0, 1000)
            for page in pages:
                pagenum += 1
                em.add_field(
                    name=f"About{' (continued):' if pagenum > 1 else ':'}",
                    value=page,
                    inline=False,
                )
        give_roles.append(registered_role)
        await member.send("Thank you, Registration is now complete!")
        await member.add_roles(*give_roles, reason="Registration")
        return em
