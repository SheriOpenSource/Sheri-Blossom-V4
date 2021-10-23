import asyncio
from io import BytesIO

import discord
from discord.ext import commands

from Formats.formats import avatar_check


class References(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def rp_char_config(ctx):
        async with ctx.bot.pool.acquire() as db:
            config = await db.fetchrow(
                """SELECT rp_sfw_channel, rp_nsfw_channel FROM botsettings_guild WHERE id=$1""",
                ctx.guild.id,
            )
            return config

    @staticmethod
    async def delete_rp_character(ctx, character):
        async with ctx.bot.pool.acquire() as db:
            await db.execute(
                """DELETE FROM botsettings_character WHERE owner_id=$1 and name=$2""",
                ctx.author.id,
                character["name"],
            )

    async def post_character(self, ctx, character):
        # grab the Config
        config = await self.rp_char_config(ctx)

        if not config:
            return None
        # Check to make sure character is sfw or nsfw
        if character["nsfw"]:
            try:
                if config["rp_nsfw_channel"] is not None:
                    channel = self.bot.get_channel(config["rp_nsfw_channel"])
                    if channel.is_nsfw():
                        embed = self.build_rp_character_embed(character)
                        await channel.send(embed=embed)
                        return True
                    else:
                        return None
                else:
                    return None
            except (discord.HTTPException, discord.Forbidden):
                return None
        else:
            try:
                if config["rp_sfw_channel"] is not None:
                    channel = self.bot.get_channel(config["rp_sfw_channel"])
                    embed = self.build_rp_character_embed(character)
                    await channel.send(embed=embed)
                    return True
                else:
                    return None
            except (discord.HTTPException, discord.Forbidden):
                return None

    @staticmethod
    async def add_rp_character(
            ctx, owner, name, nsfw, age, gender, sexuality, image, species, bio
    ):
        async with ctx.bot.pool.acquire() as db:
            test = await db.execute(
                """INSERT INTO botsettings_character (owner_id, name, nsfw, age, gender,
             sexuality, image, species, bio) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)""",
                owner,
                name,
                nsfw,
                age,
                gender,
                sexuality,
                image,
                species,
                bio,
            )

    def build_rp_character_embed(self, character):
        owner = self.bot.get_user(id=character["owner_id"])
        embed = discord.Embed(
            color=self.bot.color,
            title=f"{character['name']}",
            description=character["bio"],
        )
        embed.add_field(name="Gender", value=f"{character['gender']}")
        embed.add_field(name="Age", value=f"{character['age']}")
        embed.add_field(name="Species", value=f"{character['species']}")
        embed.add_field(name="Sexuality", value=f"{character['sexuality']}")
        embed.set_image(url=character["image"])
        embed.set_author(name=owner, icon_url=avatar_check(owner))
        return embed

    @staticmethod
    async def get_rp_characters(ctx):
        async with ctx.bot.pool.acquire() as db:
            characters = await db.fetch(
                """SELECT name, age, gender, species, nsfw FROM botsettings_character WHERE owner_id=$1""",
                ctx.author.id,
            )
            data = []
            if characters:
                for row in characters:
                    data.append(
                        f"Name: {row['name']}\n"
                        f"Species: {row['species']}\n"
                        f"NSFW: {'Yes' if row['nsfw'] else 'No'}"
                    )
                return data
            else:
                return None

    @staticmethod
    async def get_rp_character(ctx, name):
        async with ctx.bot.pool.acquire() as db:
            try:
                character = await db.fetchrow(
                    """SELECT * FROM botsettings_character WHERE owner_id=$1 and name=$2""",
                    ctx.author.id,
                    name,
                )
                return character
            except KeyError:
                return None

    @staticmethod
    async def rp_editor(ctx, character, slot, value):
        async with ctx.bot.pool.acquire() as db:
            await db.execute(f"UPDATE botsettings_character "
                             f"SET {slot}=$1 "
                             f"WHERE owner_id=$2 AND name=$3",
                             value,
                             ctx.author.id,
                             character)

    @staticmethod
    async def view_rp_character(ctx, name):
        async with ctx.bot.pool.acquire() as db:
            try:
                character = await db.fetchrow(
                    """SELECT * FROM botsettings_character WHERE name=$1, owner_id=$2""",
                    name,
                    ctx.author.id,
                )
                return character
            except KeyError:
                return None

    @commands.group(name="rp", aliases=["char", "character"])
    async def rp_index(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=self.bot.color)
            # embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_footer(
                text=f"01001000 01100101 01110111 01110111 01101111 00100001"
            )
            embed.add_field(
                name="Commands",
                value="fur**rp create**: Goes through the character creation process.\n"
                      "fur**rp view**: View a character.\n"
                      "fur**rp post**: Posts a character to the server's character channel.\n"
                      "fur**rp delete**: Deletes a character. This is irreversible.\n"
                      "fur**rp list**: Lists all your current characters.\n"
                      "fur**rp edit**: Edit your character's name, age, gender, sexuality, species, "
                      "bio, or image for any changes.\n"
                      "***Note: NSFW status can't be edited.***",
            )
            await ctx.send(embed=embed)

    @rp_index.command(name="create", aliases=["make"])
    @commands.guild_only()
    async def rp_create(self, ctx):
        character_data = {"owner_id": ctx.author.id}
        try:
            await ctx.send(
                "I will DM you to collect information regarding your character"
            )
            await ctx.author.send(
                "Is your character going to be NSFW(Not Safe For Work) or SFW(Safe For Work)?\n"
                "Valid responses: ``NSFW``, ``SFW``"
            )
        except discord.Forbidden:
            return await ctx.send(
                "It appears that your privacy settings do not allow DMs form server members, or you "
                "may have be blocked."
            )

        def check(m):
            return isinstance(m.channel, discord.DMChannel) and m.author == ctx.author

        # NSFW Question
        while True:
            options = ["nsfw", "sfw"]
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send(
                    "You took too long to respond. Please run the character creation command again."
                )
            if response.content.lower() not in options:
                await ctx.author.send("Invalid response.")
            else:
                if response.content.lower() == "nsfw":
                    character_data["nsfw"] = True
                elif response.content.lower() == "sfw":
                    character_data["nsfw"] = False
                break
            if not response:
                break

        # Name Question
        await ctx.author.send(
            "What would you like to name your character? Please keep in mind that names are case-sensitive. Any capitalization you include here "
            "will need to be included whenever you use the ``furchar view`` command, otherwise I will return an error when attempting to fetch your character's information.")
        
        while True:

            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send(
                    "You took too long to respond. Please run the character creation command again."
                )

            char = len(response.content)

            if char > 30:
                await ctx.author.send("Too many characters for this field. Try condensing your response.")
                continue

            character_data["name"] = response.content
            break

        while True:
            await ctx.author.send(f"How old is {character_data['name']}?\n")
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send(
                    "You took too long to respond. Please run the character creation command again."
                )
            if response.content.isdigit():
                if int(response.content) >= 18:
                    character_data["age"] = response.content
                elif int(response.content) <= 17:
                    character_data["age"] = response.content
                    if character_data["nsfw"]:
                        return await ctx.send(
                            "I'm sorry, but you are not allowed to store NSFW cub characters in me.\n"
                            "NSFW cub is **NOT** allowed on Discord."
                        )
                break
            elif not response.content.isdigit():
                character_data["age"] = response.content
            if not response:
                break

        while True:
            await ctx.author.send(f"What is {character_data['name']}'s gender?")
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send(
                    "You took too long to respond. Please run the character creation command again."
                )
            character_data["gender"] = response.content
            break

        await ctx.author.send(f"What is {character_data['name']}'s species?")

        while True:
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send(
                    "You took too long to respond. Please run the character creation command again."
                )

            char = len(response.content)

            if char > 30:
                await ctx.author.send("Too many characters for this field. Try condensing your response.")
                continue

            character_data["species"] = response.content
            break

        await ctx.author.send(f"What is {character_data['name']}'s sexuality?")

        while True:
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send(
                    "You took too long to respond. Please run the character creation command again."
                )

            char = len(response.content)

            if char > 30:
                await ctx.author.send("Too many characters for this field. Try condensing your response.")
                continue

            character_data["sexuality"] = response.content
            break

        while True:
            await ctx.author.send(
                f"Any additional information about {character_data['name']}?"
            )
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send(
                    "You took too long to respond. Please run the character creation command again."
                )
            character_data["bio"] = response.content
            break

        while True:
            await ctx.author.send(
                "In order to complete your entry for your character, please upload an image. Images must be of `.jpg`, `.mjpg`, or `.png` file type. "
                "Links to images are not accepted and will return an error."
            )
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send(
                    "You took too long to respond. Please run the character creation command again."
                )
            img_url = None
            try:
                img_url = response.attachments[0].url
            except (KeyError, IndexError, discord.errors.HTTPException):
                pass
            if (
                    response.content.endswith(".png")
                    or response.content.endswith(".jpg")
                    or response.content.endswith(".mjpg")
            ):
                img_url = response.content
            elif img_url is not None:
                pass
            else:
                return await ctx.author.send(
                    "You provided a URL that isn't acceptable. Please run the character creation command again."
                )
            character_data["image"] = img_url
            break

        await self.add_rp_character(
            ctx,
            character_data["owner_id"],
            character_data["name"],
            character_data["nsfw"],
            character_data["age"],
            character_data["gender"],
            character_data["sexuality"],
            character_data["image"],
            character_data["species"],
            character_data["bio"],
        )
        char_embed = self.build_rp_character_embed(character_data)
        try:
            await ctx.author.send(
                "This is what your character looks like!", embed=char_embed
            )
        except discord.HTTPException:
            return await ctx.author.send("It seems Discord had in issue making your. . .\nMake sure you keep within the 2000 character limits and the url you gave for the imagel is an acutal url! "
                                         "Redo the command when ready, but remember in a server!")
        else:
            pass
        
        await ctx.author.send(
            f"Character creation completed. You can view your character anytime using ``furchar "
            f"view {character_data['name']}``. Remember that character names are case-sensitive. Any capitalization here will need to be included when using the command, "
            f"otherwise I will return an error when attampting to fetch your character's information."
        )
        while True:
            options = ["yes", "no"]
            await ctx.author.send(
                f"Would you like me to post your character to {ctx.guild.name}?"
            )
            try:
                response = await ctx.bot.wait_for("message", timeout=60, check=check)
            except asyncio.TimeoutError:
                return await ctx.author.send(
                    "You took to long to respond. You can post later on with the command ``furchar post``"
                )
            if response.content.lower() not in options:
                await ctx.author.send(
                    "Invalid response: please only answer yes or no. Your character has not been posted, but you can post it to the server's designated "
                    "RP character channel with the ``furchar post`` command.")
            else:
                if response.content.lower() == "yes":
                    await ctx.author.send(
                        f"Attempting to post your character in {ctx.guild.name}. Stand by."
                    )
                    post = await self.post_character(ctx, character_data)
                    if not post:
                        return await ctx.author.send(
                            "There was a problem posting your character. "
                            "Please consult a server administrator to resolve the issue. "
                            "RP character channels may not be properly configured, or I may not have "
                            "necessary permissions to post your charcter."
                        )
                    else:
                        await ctx.author.send(
                            "You're character has been posted. Hope you enjoy! ;)"
                        )
                elif response.content.lower() == "No":
                    await ctx.author.send(
                        "Understood, I won't your character. Have a nice day! ;)"
                    )
            break

    @rp_index.command(name="view", aliases=["see"])
    @commands.guild_only()
    async def rp_viewer(self, ctx, *, character):
        if character is None:
            return await ctx.send(
                "You must enter the name of the character you want to see."
            )
        db_character = await self.get_rp_character(ctx, character)

        if db_character is None:
            return await ctx.send(
                "I couldn't find a character by this name. Are you sure your spelling is correct and any necessary capitalization is included?"
            )
        try:
            if db_character["nsfw"]:
                if ctx.channel.is_nsfw():
                    embed = self.build_rp_character_embed(db_character)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(
                        "This character is an NSFW character. Please try to view this in an NSFW channel!"
                    )
            else:
                embed = self.build_rp_character_embed(db_character)
                await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Uh oh! It seems Discord couldn't render thee command. Try to edit the image of your character. If still issue feel free to contact support")

    @rp_index.command(name="list")
    async def char_list(self, ctx):
        character_list = await self.get_rp_characters(ctx)
        characters = ""
        if character_list:
            for i in character_list:
                characters += f"{i}\n\n"
            try:
                await ctx.send(characters)
            except discord.HTTPException:
                data = BytesIO(characters.encode('utf-8'))
                await ctx.send(content=f"The result was a bit too long.. so here is a text file instead 🎁",
                               file=discord.File(data, filename=f'Result.txt'))
        else:
            await ctx.send("No character(s) to list")

    @rp_index.command(name="post")
    @commands.guild_only()
    async def rp_post(self, ctx, *, character):
        db_character = await self.get_rp_character(ctx, character)
        if db_character is None:
            await ctx.send(
                "I couldn't find a character by this name. Are you sure your spelling is correct and any necessary capitalization is included?"
            )
        else:
            message = await self.post_character(ctx, db_character)
            if message is None:
                await ctx.send(
                    "There was a problem posting your character. "
                    "Please consult your discord server "
                    "administrator for further diagnosis of the issue."
                )
            else:
                await ctx.send("Done, You should see it!")

    @rp_index.command(name="edit")
    @commands.guild_only()
    async def rp_editing(self, ctx, slot: str, *, character):
        slot_picks = ["name", "age", "species", "bio", "img", "gender", "sexuality"]

        slot = slot.lower()
        if slot not in slot_picks:
            return await ctx.send("Invalid edit field:\n"
                                  "`name`\n`age`\n`gender`\n`sexuality`\n`species`\n`bio` - description\n`img` - image")
        if character is None:
            return await ctx.send(
                "You must enter the name of the character you want to edit."
            )

        db_character = await self.get_rp_character(ctx, character)

        if db_character is None:
            return await ctx.send(
                "I couldn't find a character by this name. Are you sure your spelling is correct and any necessary capitalization is included?"
            )
        else:
            while True:
                def check(m):
                    return isinstance(m.channel, discord.DMChannel) and m.author == ctx.author

                if slot == "name":
                    await ctx.author.send(
                        "What would you like to name your character? Please keep in mind that names are case-sensitive. Any capitalization you include here "
                        "will need to be included whenever you use the ``furchar view`` command, otherwise I will return an error when attempting to fetch your character's information.")
                    try:
                        response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took too long to respond. Please run the character creation command again."
                        )
                    value = response.content
                    break
                elif slot == "age":
                    await ctx.author.send(f"How old is {character}?\n")
                    try:
                        response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took too long to respond. Please run the character creation command again."
                        )
                    if response.content.isdigit():
                        if int(response.content) >= 18:
                            value = response.content
                        elif int(response.content) <= 17:
                            value = response.content
                            if db_character["nsfw"]:
                                return await ctx.send(
                                    "I'm sorry, but you are not allowed to store NSFW cub characters in me.\n"
                                    "NSFW cub is **NOT** allowed on Discord."
                                )
                        break
                    elif not response.content.isdigit():
                        value = response.content
                    if not response:
                        break
                    break
                elif slot == "gender":
                    await ctx.author.send(f"What is {character}'s gender?")
                    try:
                        response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took too long to respond. Please run the character creation command again."
                        )
                    value = response.content
                    break
                elif slot == "sexuality":
                    await ctx.author.send(f"What is {character}'s sexuality?")
                    try:
                        response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took too long to respond. Please run the character creation command again."
                        )
                    value = response.content
                    break
                elif slot == "species":
                    await ctx.author.send(f"What is {character}'s species?")
                    try:
                        response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took too long to respond. Please run the character creation command again."
                        )
                    value = response.content
                    break
                elif slot == "bio":
                    await ctx.author.send(
                        f"Any additional information about {character}?"
                    )
                    try:
                        response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took too long to respond. Please run the character creation command again."
                        )
                    value = response.content
                    break
                elif slot == "img":
                    slot = "image"

                    await ctx.author.send(
                        "In order to complete your entry for your character, please upload an image or provide a URL "
                        "that represents your character. Image URLs must be `.png`, `.jpg`, or `.mjpg` file type.\n"
                        "**If your character is NSFW, please only provide a URL as Discord does not allow NSFW "
                        "content to be sent to bots.**\n"
                    )
                    try:
                        response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        return await ctx.author.send(
                            "You took too long to respond. Please run the character creation command again."
                        )
                    img_url = None
                    try:
                        img_url = response.attachments[0].url
                    except (KeyError, IndexError):
                        pass
                    if (
                            response.content.endswith(".png")
                            or response.content.endswith(".jpg")
                            or response.content.endswith(".mjpg")
                    ):
                        img_url = response.content
                    elif img_url is not None:
                        pass
                    else:
                        return await ctx.author.send(
                            "You provided a URL that isn't acceptable. Please run the character creation command again."
                        )
                    # db_character["image"] = img_url
                    value = img_url
                    break

            await self.rp_editor(ctx, character, slot, value)
            await ctx.send("Editing completed!")

    @rp_index.command(name="delete", aliases=["remove"])
    @commands.guild_only()
    async def rp_char_delete(self, ctx, *, character):
        char_to_delete = await self.get_rp_character(ctx, character)
        if char_to_delete is None:
            await ctx.send(
                "I couldn't find a character by this name. Are you sure your spelling is correct and any necessary capitalization is included?"
            )
        else:
            await ctx.send(f"Attempting to delete {char_to_delete['name']}")
            await self.delete_rp_character(ctx, char_to_delete)
            await ctx.send("Done!")


def setup(bot):
    bot.add_cog(References(bot))
