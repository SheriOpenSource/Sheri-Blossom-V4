import asyncio
from random import choice

import discord
# import rethinkdb as r
from discord.ext import commands
from pytz import timezone

# from datetime import datetime
from API.API import Retrieval

dates = list(range(1, 31))  # This is for furhoho (Do not Remove)


async def get_user_gifty(ctx, user):
    async with ctx.bot.pool.acquire() as db:
        user_info = await db.fetchrow(
            """SELECT *  
            FROM botsettings_user WHERE id = $1""",
            user.id,
        )
        return user_info


async def update_user_gifty(
        ctx, user, animal_name, animal, animal_all, a, b, treat_bag
):
    # a is the animal adder
    # b is the treats adder
    animal += a
    # animal_all += a
    treat_bag += b
    # animal_name_all = animal_name + "all"

    async with ctx.bot.pool.acquire() as db:
        await db.execute(
            f"UPDATE botsettings_user SET {animal_name}=$1, presents=$2 WHERE id=$3",
            animal,
            treat_bag,
            user.id,
        )


class Holidays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @checks.admin_or_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_nicknames=True)
    @commands.guild_only()
    @commands.cooldown(1, 3600, type=commands.BucketType.guild)
    @commands.command()
    async def massspookify(self, ctx):
        """ Changes members names to include spook themed emojis. """
        time_set = ctx.message.created_at.replace(tzinfo=timezone("UTC")).astimezone(
            timezone("US/Eastern")
        )
        time_set = time_set.strftime("%m")

        if time_set == "10":
            users = ctx.guild.members
            errors, members = 0, 0
            phrases = [
                "Time for shivers, scares, and thrills, for pumpkin grins in windowsills, for black cats in the full "
                "moon’s glow, and a happy Halloween hello!",
                "Hope your night is so happy, it makes you glow from the inside out.",
                "Wishing you a great fall season. Stay warm and cozy.",
                "Everybody is scared of something. I hope you find yours!",
                "Have a spooktakular good time.",
                "May your Halloween be scarier than what goes on every night on the news.",
                "Trick or Treat! Give me something good to eat – Give me candy. "
                "Give me cake – Give me something sweet to "
                "take!",
                "Bugs & Hisses to you!",
            ]
            await ctx.send(
                f"{choice(phrases)}\n"
                f"Changing {len(users)} Members's nickname to have a little spookified"
            )
            for member in users:
                decorations = ["👻", "🧛", "🦇", "🕷️"]
                decorate = choice(decorations)
                try:
                    await member.edit(
                        nick=decorate + "" + member.name,
                        reason=f"[Spookify] {ctx.author.name} executed this command.",
                    )
                    members += 1
                except (discord.Forbidden, discord.HTTPException):
                    errors += 1
                    pass
                await asyncio.sleep(3)
            await ctx.send(
                "Done!\n"
                f"Members renamed {members}\n"
                f"Failed to rename {errors} members."
            )
        else:
            await ctx.send("Ooooo, not yet.... This unlocks in Octooober")

    # @checks.admin_or_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_nicknames=True)
    @commands.guild_only()
    @commands.cooldown(1, 3600, type=commands.BucketType.guild)
    @commands.command()
    async def masschristmasify(self, ctx):
        """ Changes members names to include spook themed emojis. """
        timeset = ctx.message.created_at.replace(tzinfo=timezone("UTC")).astimezone(
            timezone("US/Eastern")
        )
        timeset = timeset.strftime("%m")

        if timeset == "12":
            users = ctx.guild.members
            errors, members = 0, 0
            phrases = [
                "Happy Holidays! Lets make it rain with joy "
                "*You can hear the jingle bells ring*",
                "Santa's Comming!"
            ]
            await ctx.send(
                f"{choice(phrases)}\n"
                f"Changing {len(users)} Members's nickname to have a little christmas cheer"
            )
            for member in users:
                decorations = ["🎅", "🎁", "⛄", "🎄", "🦌", "❄", "☃"]
                decorate = choice(decorations)
                try:
                    await member.edit(
                        nick=decorate + "" + member.name,
                        reason=f"[Spookify] {ctx.author.name} executed this command.",
                    )
                    members += 1
                except (discord.Forbidden, discord.HTTPException):
                    errors += 1
                    pass
                await asyncio.sleep(3)
            await ctx.send(
                "Done?\n"
                f"Members renamed {members}\n"
                f"Failed to rename {errors} members."
            )
        else:
            await ctx.send("Ooooo, not yet.... This unlocks in December")

    @commands.guild_only()
    @commands.command()
    async def spookify(self, ctx):
        """ Change your names to include spook themed emojis. """
        timeset = ctx.message.created_at.replace(tzinfo=timezone("UTC")).astimezone(
            timezone("US/Eastern")
        )
        timeset = timeset.strftime("%m")

        if timeset == "10":
            member = ctx.author
            phrases = [
                "Time for shivers, scares, and thrills, for pumpkin grins in windowsills, for black cats in the full "
                "moon’s glow, and a happy Halloween hello!",
                "Hope your night is so happy, it makes you glow from the inside out.",
                "Wishing you a great fall season. Stay warm and cozy.",
                "Everybody is scared of something. I hope you find yours!",
                "Have a spooktakular good time.",
                "May your Halloween be scarier than what goes on every night on the news.",
                "Trick or Treat! Give me something good to eat – Give me candy. Give me cake "
                "– Give me something sweet to "
                "take!",
                "Bugs & Hisses to you!",
            ]
            await ctx.send(f"{choice(phrases)}")

            decorations = ["👻", "🧛", "🦇", "🕷️"]
            decorate = choice(decorations)
            try:
                await member.edit(
                    nick=decorate + "" + member.name,
                    reason=f"[Spookify] {ctx.author.name} executed this command.",
                )
            except (discord.Forbidden, discord.HTTPException):
                await ctx.send("There was a problem changing your name!")

        else:
            await ctx.send("Ooooo, This command in used on Octooober")

    @commands.command(aliases=["tot", "ahh"])
    @commands.cooldown(1, 86400, type=commands.BucketType.user)
    async def treaties(self, ctx):
        """ Changes members names to include spook themed emojis. """
        timeset = ctx.message.created_at.replace(tzinfo=timezone("UTC")).astimezone(
            timezone("US/Eastern")
        )
        timeset = timeset.strftime("%m")

        if timeset == "10":
            user = ctx.author
            animals = ["wolves", "bunnies", "foxes"]

            user_info = await get_user_gifty(ctx, user)
            treat_bag = user_info["treats"]
            rng = choice(animals)
            animal_count = range(10, 20)
            treats = range(10, 25)

            spoopy_img = await Retrieval.main_api(self.bot, "trickortreat")

            if rng == "wolves":
                awoo = choice(animal_count)
                stnick = choice(treats)
                wolves = user_info["wolves"]
                wolves_all = user_info["wolvesall"]

                await update_user_gifty(
                    ctx, user, rng, wolves, wolves_all, awoo, stnick, treat_bag
                )
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"[Image Link]({spoopy_img['url']})",
                )
                embed.set_image(url=spoopy_img["url"])
                await ctx.send(
                    "Trick or treat, my delicious one!\n"
                    f"I'm going to give you {stnick} treats alongside {awoo} wolves!",
                    embed=embed,
                )

            if rng == "bunnies":
                carrots = choice(animal_count)
                stnick = choice(treats)
                bunnies = user_info["bunnies"]
                bunnies_all = user_info["bunniesall"]

                await update_user_gifty(
                    ctx, user, rng, bunnies, bunnies_all, carrots, stnick, treat_bag
                )
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"[Image Link]({spoopy_img['url']})",
                )
                embed.set_image(url=spoopy_img["url"])
                await ctx.send(
                    "Trick or treat, my delicious one!\n"
                    f"I'm going to give you {stnick} treats alongside {carrots} bunnies!",
                    embed=embed,
                )

            if rng == "foxes":
                owo = choice(animal_count)
                stnick = choice(treats)
                foxes = user_info["foxes"]
                foxes_all = user_info["foxesall"]
                await update_user_gifty(
                    ctx, user, rng, foxes, foxes_all, owo, stnick, treat_bag
                )
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"[Image Link]({spoopy_img['url']})",
                )
                embed.set_image(url=spoopy_img["url"])
                await ctx.send(
                    "Trick or treat, my delicious one!\n"
                    f"I'm going to give you {stnick} treats alongside {owo} foxes!",
                    embed=embed,
                )

        else:
            await ctx.send(
                "You will be able to use this command again on ``October 1st, 2020``"
            )

    @commands.command(aliases=["merry", "gifts"])
    @commands.cooldown(1, 86400, type=commands.BucketType.user)
    async def hoho(self, ctx):
        """Changes members names to include spook themed emojis."""
        timeset = ctx.message.created_at.replace(tzinfo=timezone("UTC")).astimezone(
            timezone("US/Eastern")
        )
        timeset_month = timeset.strftime("%m")
        timeset_day = int(timeset.strftime("%d"))

        if timeset_month == "12" and timeset_day in dates:
            user = ctx.author
            animals = ["wolves", "bunnies", "foxes"]

            user_info = await get_user_gifty(ctx, user)
            gift_bag = user_info["presents"]
            rng = choice(animals)
            animal_count = range(10, 20)
            treats = range(10, 25)

            christmas_img = await Retrieval.main_api(self.bot, "christmas")

            if rng == "wolves":
                awoo = choice(animal_count)
                stnick = choice(treats)
                wolves = user_info["wolves"]
                wolves_all = user_info["wolvesall"]

                await update_user_gifty(
                    ctx, user, rng, wolves, wolves_all, awoo, stnick, gift_bag
                )

                if ctx.channel.is_nsfw():
                    embed = discord.Embed(color=self.bot.color)
                    embed.description = f"[Image Link]({christmas_img['url']})"
                    embed.set_image(url=christmas_img["url"])
                    return await ctx.send(
                        "Jingle Bells, Jingle Bells!\n"
                        f"I'm going to give you {stnick} presents and {awoo} wolves!",
                        embed=embed, )

                await ctx.send(
                    "Jingle Bells, Jingle Bells!\n"
                    f"I'm going to give you {stnick} presents and {awoo} wolves!")

            if rng == "bunnies":
                carrots = choice(animal_count)
                stnick = choice(treats)
                bunnies = user_info["bunnies"]
                bunnies_all = user_info["bunniesall"]

                await update_user_gifty(
                    ctx, user, rng, bunnies, bunnies_all, carrots, stnick, gift_bag
                )
                if ctx.channel.is_nsfw():
                    embed = discord.Embed(color=self.bot.color)
                    embed.description = f"[Image Link]({christmas_img['url']})"
                    embed.set_image(url=christmas_img["url"])
                    return await ctx.send(
                        "Jingle Bells, Jingle Bells!\n"
                        f"I'm going to give you {stnick} presents and {carrots} bunnies!",
                        embed=embed, )

                await ctx.send(
                    "Jingle Bells, Jingle Bells!\n"
                    f"I'm going to give you {stnick} presents and {carrots} bunnies!")

            if rng == "foxes":
                owo = choice(animal_count)
                stnick = choice(treats)
                foxes = user_info["foxes"]
                foxes_all = user_info["foxesall"]
                await update_user_gifty(
                    ctx, user, rng, foxes, foxes_all, owo, stnick, gift_bag
                )
                if ctx.channel.is_nsfw():
                    embed = discord.Embed(color=self.bot.color)
                    embed.description = f"[Image Link]({christmas_img['url']})"
                    embed.set_image(url=christmas_img["url"])
                    return await ctx.send(
                        "Jingle Bells, Jingle Bells!\n"
                        f"I'm going to give you {stnick} presents and {owo} foxes!",
                        embed=embed)

                await ctx.send(
                    "Jingle Bells, Jingle Bells!\n"
                    f"I'm going to give you {stnick} presents and {owo} foxes!")
        else:
            await ctx.send("This command will be available again during the Christmas seasons of ``2020``!")


def setup(bot):
    bot.add_cog(Holidays(bot))
