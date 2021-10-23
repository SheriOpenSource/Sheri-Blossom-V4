import asyncio
import datetime
import io
import random
from io import BytesIO
from random import choice, randint

import aiohttp
import discord
import pytz
from PIL import ImageFont, Image, ImageDraw
from dateutil.relativedelta import relativedelta
from discord.ext import commands

from API.API import Retrieval as Get
from Checks.bot_checks import can_delete
from Formats.formats import avatar_check
from Functions.core import send_message
from Lines.custom_emotes import CustomEmotes


# gif time 1.6


def cooldown(time1, time2):
    delta = relativedelta(time1, time2)
    return delta


def catching_animal_unboxing(catch):
    def chance():
        return randint(1, 10000)  # hmm 100 x 100

    bunny = chance()
    wolf = chance()
    fox = chance()
    item = None

    if wolf < 100:  # For I think 0.1% chance? No it's actually 1% chance u dum dum
        item = "wolves"
    if bunny < 250:  # For I think 0.25% chance? also override the wolf NO MULTIPLE CATCHES YOU GREEDY BAS... no 2.5%
        item = "bunnies"
    if fox < 500:  # For I think 0.5% chance? also override all the above NO MULTIPLE CATCHES YOU GREEDY BAS... no 5%
        item = "foxes"

    return True, item  # if item is None -> You caught nothing, TOO BAD try again next time


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def daily_gui(
            self,
            ctx,
            user,
            url,
            word,
            streak_end,
            coin_rewards,
            box_rewards,
            key_rewards,
            updated_coins,
            updated_boxes,
            updated_keys,
    ):
        font = "utils/fonts/NOVASQUARE.TTF"
        sexyfont = "utils/fonts/AKRONIM-REGULAR.TTF"

        if streak_end is False:
            color = [255, 255, 255]
        else:
            color = [0, 255, 0]

        stat_font = ImageFont.truetype(font, size=45)
        up_font = ImageFont.truetype(font, size=30)
        bonus_font = ImageFont.truetype(sexyfont, size=100)

        im = Image.new("RGBA", (1000, 300), (0, 0, 169, 0))
        im_draw = ImageDraw.Draw(im)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://cdn.discordapp.com/attachments/436367441224925193/635691464193474570/sheridailyF.png"
            ) as raw_response:
                banner = BytesIO(await raw_response.read())

                banner = Image.open(banner)

        im.paste(banner, (0, 0))

        # This is going to be annoying
        w1, _ = im_draw.textsize(f"{updated_keys:,}", font=stat_font)
        w2, _ = im_draw.textsize(f"{updated_coins:,}", font=stat_font)
        w3, _ = im_draw.textsize(f"{updated_boxes:,}", font=stat_font)
        w4, _ = im_draw.textsize(word, font=bonus_font)

        # Keys
        im_draw.text(
            (((450 - w1) / 2), 105),
            text=f"{updated_keys:,}",
            fill=(255, 255, 255, 200),
            font=stat_font,
        )
        im_draw.text(
            (200, 155),
            text=f"+{key_rewards}",
            fill=(color[0], color[1], color[2], 100),
            font=up_font,
        )

        # Coins
        im_draw.text(
            (((1000 - w2) / 2), 105),
            text=f"{updated_coins:,}",
            fill=(255, 255, 255, 200),
            font=stat_font,
        )
        im_draw.text(
            (450, 155),
            text=f"+{coin_rewards}",
            fill=(color[0], color[1], color[2], 100),
            font=up_font,
        )

        # Daily Word
        im_draw.text(
            (((1000 - w4) / 2), 200),
            text=word,
            fill=(255, 255, 255, 200),
            font=bonus_font,
        )

        # Boxes
        im_draw.text(
            (((450 - w3) / 2 + 550), 105),
            text=f"{updated_boxes:,}",
            fill=(255, 255, 255, 200),
            font=stat_font,
        )
        im_draw.text(
            (750, 155),
            text=f"+{box_rewards}",
            fill=(color[0], color[1], color[2], 100),
            font=up_font,
        )

        buffer = BytesIO()
        im.save(buffer, "png")
        buffer.seek(0)

        return buffer

    # Concept and prototype
    @staticmethod
    async def randomize_loot(data, values, rare=False, halloween=False, christmas=False):
        if data is None:
            return None
        else:
            if values is None:
                return None
            if rare:
                # Input rare logic
                pass
            if halloween:
                # input halloween logic
                pass
            if christmas:
                # input christmas logic
                pass
            if ["bunnies", "foxes", "wolves"] in data:
                rng = choice(range(1, 5))

    async def get_image(self, ctx):
        if ctx.channel.is_nsfw():
            # pull an image from /yiff for dailies
            api = await Get.main_api(self.bot, "yiff")
            return api["url"]
        else:
            # Pull an image from /mur for dailies
            api = await Get.main_api(self.bot, "mur")
            return api["url"]

    @staticmethod
    async def get_user_currency(ctx, user):
        async with ctx.bot.pool.acquire() as db:
            user_info = await db.fetchrow(
                """SELECT coins, boxes, keys, foxes, bunnies, wolves, foxesall, wolvesall, bunniesall  
                FROM botsettings_user WHERE id = $1""",
                user.id,
            )
            return user_info

    @staticmethod
    async def update_user_currency(ctx, user, keys=None, boxes=None, coins=None):
        if (keys, boxes, coins) is not None:
            async with ctx.bot.pool.acquire() as db:
                await db.execute(
                    "UPDATE botsettings_user SET keys=$1, boxes=$2, coins=$3 WHERE id=$4",
                    keys,
                    boxes,
                    coins,
                    user.id,
                )
        else:
            await ctx.send("Internal error has occurred.")
            return None

    @staticmethod
    async def get_user_animals(ctx, user, item):
        async with ctx.bot.pool.acquire() as db:
            animal = await db.fetchrow(
                f"""SELECT {item} FROM botsettings_user WHERE id=$1""", user.id
            )
            return animal

    @staticmethod
    async def update_user_animals(ctx, user, item, value):
        async with ctx.bot.pool.acquire() as db:
            await db.execute(
                f"UPDATE botsettings_user SET {item}=$1 WHERE id=$2", value + 1, user.id
            )

    @commands.command(aliases=['inventory', 'bal'])
    async def balance(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author

        cmd = self.bot.get_command("daily")
        daily_warning = None
        # if cmd.is_on_cooldown(ctx) is False and user == ctx.author:
        # daily_warning = "Your dailies collection is avaliable! Run `furdaily`"

        # user_info = await self.get_user_currency(ctx, user)
        async with ctx.bot.pool.acquire() as db:
            user_info = await db.fetchrow(
                """SELECT coins, boxes, keys, foxes, bunnies, wolves, cats, foxesall, wolvesall, bunniesall, next_daily  
                FROM botsettings_user WHERE id = $1""",
                user.id,
            )
        keys, boxes, coins, wolves, foxes, bunnies, cats = user_info["keys"], user_info["boxes"], user_info["coins"], \
                                                           user_info["wolves"], user_info["foxes"], user_info[
                                                               "bunnies"], user_info["cats"]

        # The Cooldown Section Check:
        cooldown_data = user_info["next_daily"]
        now = datetime.datetime.now(pytz.utc)
        delta = cooldown(cooldown_data, now)

        if not delta.seconds:
            daily_warning = "Your dailies collection is avaliable! Run `furdaily` to collect your dailies!"
        elif delta.seconds < 0:
            daily_warning = "Your dailies collection is avaliable! Run `furdaily` to collect your dailies!"

        # Start of the GUI interface==================================
        digital = "utils/fonts/SYDNIE.TTF"
        dig_font = ImageFont.truetype(digital, size=50)
        dig_font_coin = ImageFont.truetype(digital, size=60)

        output = io.BytesIO()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    'https://cdn.discordapp.com/attachments/346892627108560902/638579696312778753/image0.png') as raw_response:
                bg = BytesIO(await raw_response.read())

                bg = Image.open(bg).convert('RGBA')

        bg = bg.resize((1250, 950), Image.NEAREST)

        bg.save(output, format='PNG')

        # return bg

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    'https://i.pinimg.com/originals/9d/f1/e3/9df1e357e6b4e99f4a7e8ae5263274d6.png') as raw_response:
                bg1 = BytesIO(await raw_response.read())

                bg1 = Image.open(bg1).convert('RGBA')

        bg1 = bg1.resize((75, 75), Image.NEAREST)

        bg1.save(output, format='PNG')

        # return bg1

        async with aiohttp.ClientSession() as session:
            async with session.get('https://img.pngmix.com/pm/rabbits/rabbits_003.png') as raw_response:
                bg2 = BytesIO(await raw_response.read())

                bg2 = Image.open(bg2).convert('RGBA')

        bg2 = bg2.resize((65, 65), Image.NEAREST)
        bg2.save(output, format='PNG')
        # return bg2

        url = 'https://images.vexels.com/media/' \
              'users/3/140314/isolated/preview/645b3ddb021b03c735970864318c255e-fox-silhouette-by-vexels.png'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as raw_response:
                bg3 = BytesIO(await raw_response.read())

                bg3 = Image.open(bg3).convert('RGBA')

        bg3 = bg3.resize((75, 75), Image.NEAREST)

        bg3.save(output, format='PNG')
        # return bg3

        url2 = 'https://media.discordapp.net/attachments/633443509495660554/' \
               '678094084405067778/TG6bJCm7-hb7H4dX-4gGbz_GfQGxjB2NwCOn-' \
               'fWf8yZQU0aTybOoamErjGQDtrKGNGVq477duoOOJ7hLn96vEyhxGTxhIaBJWS3w.png'

        async with aiohttp.ClientSession() as session:
            async with session.get(url2) as raw_response:
                bg4 = BytesIO(await raw_response.read())

                bg4 = Image.open(bg4).convert('RGBA')

        bg4 = bg4.resize((75, 75), Image.NEAREST)

        bg4.save(output, format='PNG')

        im = Image.new('RGBA', (1250, 950), (0, 0, 0, 0))
        im_draw = ImageDraw.Draw(im)

        if wolves > 9999:
            wolves = "+9,999"
        else:
            wolves = f"{wolves:,}"
        if bunnies > 9999:
            bunnies = "+9,999"
        else:
            bunnies = f"{bunnies:,}"
        if foxes > 9999:
            foxes = "+9,999"
        else:
            foxes = f"{foxes:,}"
        if cats > 9999:
            cats = "+9,999"
        else:
            cats = f"{cats:,}"
        im_draw.rectangle((40, 75, 1200, 600), fill=(25, 223, 50, 255))
        im.paste(bg, (0, 0), bg)
        im_draw.text((515, 300), text=f"Coins: {coins:,}", fill=(55, 25, 55, 200), font=dig_font_coin)
        im_draw.text((150, 215), text=f"Boxes: {boxes:,}", fill=(55, 25, 55, 200), font=dig_font)
        im_draw.text((150, 275), text=f"Keys: {keys:,}", fill=(55, 25, 55, 200), font=dig_font)

        im.paste(bg1, (140, 400), bg1)
        im_draw.text((200, 400), text=wolves, fill=(55, 25, 55, 200), font=dig_font)

        im.paste(bg2, (350, 400), bg2)
        im_draw.text((420, 400), text=bunnies, fill=(55, 25, 55, 200), font=dig_font)

        im.paste(bg4, (600, 390), bg4)
        im_draw.text((680, 400), text=cats, fill=(55, 25, 55, 200), font=dig_font)

        im.paste(bg3, (840, 400), bg3)
        im_draw.text((920, 400), text=foxes, fill=(55, 25, 55, 200), font=dig_font)

        buffer = BytesIO()
        im.save(buffer, 'png')
        buffer.seek(0)
        post = discord.Embed()
        post.set_image(url="attachment://bal.png")

        await ctx.send(file=discord.File(fp=buffer, filename='bal.png'), content=daily_warning, embed=post)

    @commands.command()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.user)
    async def daily(self, ctx, user: discord.Member = None):
        cooldown_format = ""
        if user is None:
            gifter = None
            user = ctx.author
            received = f"<:information_sheri:648192172629426177> | " \
                       f"**{ctx.author.name}**, you have collected your dailies."

            cool_down_message = f"You're a bit too early, {ctx.author.name}! " \
                                f"You've already collected your dailies for the day.\n" \
                                f"You can try again in {cooldown_format}."

            message = "You have collected your dailies! Let's see what you got today!"

        else:
            gifter = user

            received = f"<:information_sheri:648192172629426177> | **{user.name}**, " \
                       f"{ctx.author.name} has given you their dailies today!"

            cool_down_message = f"Sorry {ctx.author.name}, you can't gift your dailies to {user.name} " \
                                f"because you have recently collected or gifted your dailies.\n" \
                                f"You can try again in {cooldown_format}."

            message = f"You have given {user.name} your dailies for today!"

        streak_end = False
        coin_rewards = randint(100, 300)  # Default: 100,300
        box_rewards = randint(1, 5)  # Default: 1, 5
        key_rewards = randint(1, 5)  # Default: 1, 5
        # delta = relativedelta(ctx.message.created_at, ctx.author.created_at)

        async with ctx.bot.pool.acquire() as db:
            cooldown_data = await db.fetchval("SELECT next_daily FROM botsettings_user WHERE id=$1",
                                              ctx.author.id)
            user_info = await db.fetchrow(
                """SELECT coins, boxes, dailies_streak, keys, foxes, bunnies, wolves 
                FROM botsettings_user WHERE id = $1""",
                user.id,
            )
            keys, boxes, coins = user_info["keys"], user_info["boxes"], user_info["coins"]

            now = datetime.datetime.now(pytz.utc)
            delta = cooldown(cooldown_data, now)
            next_message = now + datetime.timedelta(days=1)

            if delta.hours:
                cooldown_format += f"{delta.hours} hours"

            if delta.minutes:
                cooldown_format += f" {delta.minutes} minutes"

            if delta.seconds:
                cooldown_format += f" {delta.seconds} seconds"

            cooldown_format += "."

            if user == ctx.author:
                cool_down_message = f"Whoa there, {ctx.author.name}! " \
                                    f"You've already collected your dailies for the day.\n" \
                                    f"You can try again in {cooldown_format}"
            else:
                cool_down_message = f"Hold up, {ctx.author.name}! You can't gift your dailies to {user.name} " \
                                    f"because you've recently collected or gifted your dailies.\n" \
                                    f"You can try again in {cooldown_format}."

            # Cooldown by Seconds for more accuracy

            if cooldown_data:
                if delta.minutes < 0 or delta.seconds < 0 or delta.hours < 0:
                    pass
                elif delta.seconds >= 0:
                    return await send_message(ctx, message=cool_down_message)
                elif delta.seconds is None and delta.minutes >= 0:
                    return await send_message(ctx, message=cool_down_message)
                elif delta.seconds >= 0 and delta.minutes is None:
                    return await send_message(ctx, message=cool_down_message)
                elif delta.seconds >= 0 and delta.hours is None:
                    return await send_message(ctx, message=cool_down_message)

            msg = await send_message(ctx,
                                     message=f"<:information_sheri:648192172629426177> | "
                                             f"**{ctx.author.name}**, {message}"
                                     )
            await asyncio.sleep(2)

            if ctx.channel.is_nsfw():
                # pull an image from /yiff for dailies
                api = await Get.main_api(self.bot, "yiff")
                url = api["url"]
            else:
                # Pull an image from /mur for dailies
                api = await Get.main_api(self.bot, "mur")
                url = api["url"]

            spell = list("Furry")

            # Count the times its been used.
            token = user_info['dailies_streak']
            if not token:
                token = 0
            day = delta.days
            if not day:
                day = 0
            if day > -1:  # The streak continuation window
                if token >= 4:
                    streak_end = True
                    token = 0
                    streak = "You've received a **BONUS** for completing your streak! " \
                             "Come back tomorrow to start your streak again."
                else:
                    token += 1
                    streak = "You're on a streak to spell out `Furry`! Come back tomorrow for the next letter! :)"
            else:
                if token != 0:
                    token = 0
                    streak = "Aw heck, you've lost your streak! You can come back tomorrow to begin your streak again."
                else:
                    token = 0
                    streak = "Come back tomorrow to begin your streak!"

                    # Math time
            if streak_end is False:
                updated_coins, updated_boxes, updated_keys = (
                    coins + coin_rewards,
                    boxes + box_rewards,
                    keys + key_rewards,
                )
            else:
                coin_rewards = int(coin_rewards * 2.5)  # Default: 2.5
                box_rewards = int(box_rewards * 2.5)  # Default: 2.5
                key_rewards = int(key_rewards * 2.5)  # Default: 2.5

                updated_coins, updated_boxes, updated_keys = (
                    coins + coin_rewards,
                    boxes + box_rewards,
                    keys + key_rewards,
                )

            # Database things
            if gifter is None:
                await db.execute(
                    "UPDATE botsettings_user SET dailies_streak=$1, boxes=$2, keys=$3, "
                    "coins=$4, next_daily=$6 WHERE id=$5",
                    token, updated_boxes, updated_keys, updated_coins, user.id, next_message)

            else:
                await db.execute(
                    "UPDATE botsettings_user SET boxes=$1, keys=$2, coins=$3 WHERE id=$4",
                    updated_boxes, updated_keys, updated_coins, user.id)

                await db.execute(
                    "UPDATE botsettings_user SET dailies_streak=$1, next_daily=$3 WHERE id=$2",
                    token, ctx.author.id, next_message)

            word = []

            i = 0

            while i < token:
                word.append(spell[i])

                i += 1

                if i == 20:
                    break

            word = "".join(word)
            gui = await self.daily_gui(
                ctx,
                user,
                url,
                word,
                streak_end,
                coin_rewards,
                box_rewards,
                key_rewards,
                updated_coins,
                updated_boxes,
                updated_keys,
            )

            post = discord.Embed(
                color=0x836193
            )

            post.add_field(
                name="Image Info",
                value=f"**Link to image [here]({api['url']})\n"
                      f"Something wrong? Report it [here]({api['report_url']})**",
                inline=True,
            )

            post.set_author(
                icon_url="https://cdn.discordapp.com/attachments/515925482617700392/635686603741724682/logo.png",
                url="https://sheri.bot/",
                name="https://sheri.bot",
            )

            post.set_thumbnail(url=avatar_check(user))
            post.set_footer(
                icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                text="Image hosted on https://sheri.bot/",
            )

            post.set_image(url=url)

            await send_message(ctx, message=f"{received}\n{streak}", embed=post,
                               file=discord.File(fp=gui,
                                                 filename="daily_card.png"))
            if can_delete(ctx):
                await msg.delete()

    @commands.group(name="unbox", aliases=['unwrap'])
    @commands.cooldown(5, 5, type=commands.BucketType.user)
    @commands.guild_only()
    async def unbox_index(self, ctx):
        if not ctx.invoked_subcommand:
            embed = discord.Embed(color=self.bot.color)
            embed.add_field(name="Commands",
                            value="fur**unbox box** - Opens a fur box\n"
                                  "fur**unwrap treat** - Unwraps a treat",
                            inline=False)
            await ctx.send(embed=embed)

    @unbox_index.command(name="box")
    async def unbox_box(self, ctx, open: str = None):
        if open:
            return await ctx.invoke(self.bot.get_command('multiunbox'), open)

        # Logic check for things
        user = ctx.message.author
        coin_rewards = randint(100, 250)  # Default 100, 250
        doubloon = "<:doubloons:448498718795366410>"
        if not ctx.invoked_subcommand:
            catch = False
            item = None
            user_info = await self.get_user_currency(ctx, user)
            keys = user_info["keys"]
            boxes = user_info["boxes"]
            db_coin = user_info["coins"]

            # Check to make sure they have keys
            if keys <= 0:
                return await send_message(ctx, message="You don't have a key to open a fur box\n"
                                                       "You can craft one with ``furcraft key``")
            elif boxes <= 0:
                return await send_message(ctx, message="You have no fur boxes to open.\n"
                                                       "You can craft one with ``furcraft box``")
            else:
                catch, item = catching_animal_unboxing(catch)
                db_key = keys - 1
                db_box = boxes - 1
                db_coin = db_coin + coin_rewards
                await self.update_user_currency(
                    ctx, ctx.author, db_key, db_box, db_coin
                )

                if item is not None:
                    animal = await self.get_user_animals(ctx, user, item)
                    value = animal[str(item)]
                    await self.update_user_animals(ctx, user, item, value)
                else:
                    animal = None

                # Opening Boxes representation

                # 2019-11-18T0800-0800: Swap out custom emotes with paws emoji due to
                # custom emotes not rendering. Code was {CustomEmotes.get_emote(paw=True)}
                # Also swapped {doubloon} for raw emoji

                # 2019-11-18T0830-0800: Put new IDs into custom emotes. Trying this out again.

                if item is None:
                    results_embed = discord.Embed(
                        color=self.bot.color,
                        description=f"{CustomEmotes.get_emote(paw=True)} **Hey {user.name}!** *wags tail~* {CustomEmotes.get_emote(paw=True)}"
                                    f"\n\n You opened a Fur Box with a Fur Key and received **{coin_rewards}** "
                                    f"<:doubloons:646022920602255400> Doubloons! ",
                    )
                    gif_embed = discord.Embed(color=self.bot.color)
                    gif_embed.set_image(
                        url="https://sheri.bot/media/sheri_open_box.gif"
                    )
                    msg = await ctx.send(embed=gif_embed)
                else:
                    phrases = choice(
                        ["Legendary", "Got Um", "UwU", "OwO", "Cutie", "Fluffy"]
                    )

                    if item == "foxes":
                        animal = "fox"
                    elif item == "wolves":
                        animal = "wolves"
                    elif item == "bunnies":
                        animal = "bunny"
                    else:
                        animal = item
                    results_embed = discord.Embed(
                        color=self.bot.color,
                        description=f" {CustomEmotes.get_emote(paw=True)}{phrases}{CustomEmotes.get_emote(paw=True)} \n"
                                    f"**{user.name}** *bounces*"
                                    f"\n\n You opened a Fur Box with a Fur Key and got a **{animal}** "
                                    f"which had **{coin_rewards}** {doubloon} Doubloons in their mouth! ",
                    )
                    gif_embed = discord.Embed(color=self.bot.color)
                    gif_embed.set_image(
                        url="https://sheri.bot/media/sheri_open_box.gif"
                    )
                    msg = await ctx.send(embed=gif_embed)

                # image logic
                if ctx.channel.is_nsfw():
                    # pull an image from /yiff for dailies
                    if item is None:
                        api = await Get.main_api(self.bot, "yiff")
                        results_embed.set_image(url=api["url"])
                    else:
                        api = await Get.main_api(self.bot, animal)
                        results_embed.set_image(url=api["url"])
                else:
                    # Pull an image from /mur for dailies
                    if item is None:
                        api = await Get.main_api(self.bot, "mur")
                        results_embed.set_image(url=api["url"])
                    else:
                        api = await Get.main_api(self.bot, animal)
                        results_embed.set_image(url=api["url"])

                # Results Embed
                results_embed.set_footer(
                    text=f"Keys Left: {db_key} | Boxes Left: {db_box} | Doubloons: {db_coin}"
                )
                # Wait for the gif to play all the way through
                await asyncio.sleep(2)
                await msg.edit(embed=results_embed)

    @unbox_index.command(name="treat", aliases=["treats"])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def unbox_treats(self, ctx, amt: str = None):
        async with self.bot.pool.acquire() as db:
            user_info = await db.fetchrow("SELECT bunnies, foxes, wolves, treats FROM botsettings_user WHERE id=$1",
                                          ctx.author.id)
            treats = user_info['treats']
            if not amt:
                rng = choice(range(1, 5))
                if treats > 0:
                    updated_treats = treats - 1
                    updated_foxes, updated_wolves, updated_bunnies = (user_info['foxes'] + rng,
                                                                      user_info['wolves'] + rng,
                                                                      user_info['bunnies'] + rng)
                    message = await ctx.send(
                        f"{ctx.author.name} begins unwrapping their treat. "
                        f"It's a chocolate egg with a hollow center... and there's something inside!\n"
                        f"Upon cracking the egg open, {rng} of each animal pops out and surrounds {ctx.author.name} "
                        f"with warm floofy hugs and cuddles! D'awww~!")
                    await db.execute(
                        "UPDATE botsettings_user SET bunnies=$1, foxes=$2, wolves=$3, treats=$4 WHERE id=$5",
                        updated_bunnies, updated_foxes, updated_wolves, updated_treats, ctx.author.id)
                else:
                    await ctx.send("You do not have a treat to unwrap.")
            else:
                if amt.isdigit():
                    amt = int(amt)
                else:
                    return

                test_treats = treats - amt

                if test_treats >= 0:
                    updated_foxes, updated_wolves, updated_bunnies = \
                        user_info['foxes'], user_info['wolves'], user_info['bunnies']
                    updated_treats = treats
                    total_rng = 0

                    while amt > 0:
                        rng = choice(range(1, 5))
                        updated_treats -= 1
                        total_rng += rng
                        updated_foxes += rng
                        updated_wolves += rng
                        updated_bunnies += rng

                        amt -= 1

                    await db.execute(
                        "UPDATE botsettings_user SET bunnies=$1, foxes=$2, wolves=$3, treats=$4 WHERE id=$5",
                        updated_bunnies, updated_foxes, updated_wolves, updated_treats, ctx.author.id)
                    await ctx.send(
                        f"{ctx.author.name} begins unwrapping their treat. It's a chocolate egg "
                        f"with a hollow center... and there's something inside!\n"
                        f"Upon cracking the egg open, {total_rng} of each animal pops out and surrounds "
                        f"{ctx.author.name} with warm floofy hugs and cuddles! D'awww~!")
                else:
                    await ctx.send("Oh no! You don't have any treats!")

    @unbox_index.command(name="present", aliases=["presents"])
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def unbox_presents(self, ctx, amt: str = None):
        async with self.bot.pool.acquire() as db:

            lottery = [69, 420, 2020, 15, 35, 500, 900, 344, 32, 1010, 2]

            drawed_number = randint(1, 10000)

            if drawed_number in lottery:
                waspy = await self.bot.fetch_user(139800365393510400)
                await waspy.send(f"{ctx.author} won a user premium from {ctx.guild}!")
                await db.execute("UPDATE botsetting_user SET premium = True, premium_count=10 WHERE id= $1",
                                 ctx.author.id)

                return await ctx.send(
                    "You opened a present that had a shiny premium! "
                    "You can enjoy my user premium commands now! Head to <https://sheri.bot/commands> "
                    "and scroll down to the **Donators** section to see my premium commands.")

            user_info = await db.fetchrow("SELECT bunnies, foxes, wolves, presents FROM botsettings_user WHERE id=$1",
                                          ctx.author.id)

            treats = user_info['presents']

            if not amt:
                rng = choice(range(1, 5))
                if treats > 0:
                    updated_treats = treats - 1
                    updated_foxes, updated_wolves, updated_bunnies = (user_info['foxes'] + rng,
                                                                      user_info['wolves'] + rng,
                                                                      user_info['bunnies'] + rng)
                    message = await ctx.send(
                        f"{ctx.author.name} unwraps their present in a flurry. "
                        f"In a blizzard of ribbons and wrapping paper they hurry. There's something inside! "
                        f"Who knows what it could be? They open their present, eager to see.\n "
                        f"Oh gosh, oh golly, look here! {rng} of every animal springs out "
                        f"at {ctx.author.name} full of holiday cheer!\n"
                        f"**Have a merry Christmas and a happy New Year!**")
                    await db.execute(
                        "UPDATE botsettings_user SET bunnies=$1, foxes=$2, wolves=$3, presents=$4 WHERE id=$5",
                        updated_bunnies, updated_foxes, updated_wolves, updated_treats, ctx.author.id)
                else:
                    await ctx.send("Aw, looks like you don't have a treat to unwrap.")
            else:
                if amt.isdigit():
                    amt = int(amt)
                else:
                    return

                test_treats = treats - amt

                if test_treats >= 0:
                    updated_foxes, updated_wolves, updated_bunnies = \
                        user_info['foxes'], user_info['wolves'], user_info['bunnies']
                    updated_treats = treats
                    total_rng = 0

                    while amt > 0:
                        rng = choice(range(1, 5))
                        updated_treats -= 1
                        total_rng += rng
                        updated_foxes += rng
                        updated_wolves += rng
                        updated_bunnies += rng

                        amt -= 1

                    await db.execute(
                        "UPDATE botsettings_user SET bunnies=$1, foxes=$2, wolves=$3, presents=$4 WHERE id=$5",
                        updated_bunnies, updated_foxes, updated_wolves, updated_treats, ctx.author.id)
                    await ctx.send(
                        f"{ctx.author.name} unwraps their present in a flurry. "
                        f"In a blizzard of ribbons and wrapping paper they hurry. There's something inside! "
                        f"Who knows what it could be? They open their present, eager to see.\n "
                        f"Oh gosh, oh golly, look here! {total_rng} of every animal springs out "
                        f"at {ctx.author.name} full of holiday cheer!\n"
                        f"**Have a merry Christmas and a happy New Year!**")
                else:
                    await ctx.send("Aw nu, you don't have any presents to open! Here's some hot cocoa instead! ☕")

    @commands.group(name="craft", aliases=["create"])
    async def craft_index(self, ctx):
        if not ctx.invoked_subcommand:
            embed = discord.Embed(
                color=self.bot.color, description="Crafting system v1.0"
            )
            embed.add_field(
                name="craft key",
                value="Crafts a key\n"
                      "You need the following items to make a key:\n"
                      "``5`` foxes, ``5`` bunnies, ``5`` wolves and ``400`` doubloons.",
            )
            embed.add_field(
                name="craft box",
                value="Crafts a box\n"
                      "You need the following items to put box together:\n"
                      "``2`` foxes, ``2`` bunnies, ``2`` wolves and ``200`` doubloons.",
            )
            await ctx.send(embed=embed)

    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @craft_index.command(name="box")
    async def craft_box(self, ctx, amount: int = None):
        current = await self.get_user_currency(ctx, ctx.author)
        # Coin checker
        message = "You don't have the required items to create a box.\n"
        if current["coins"] >= 200:
            coins = True
        else:
            coins = False
            message += (
                f"  - Required: ``200 coins`` > Current: ``{current['coins']} coins``\n"
            )

        if current["wolves"] >= 2:
            wolves = True
        else:
            wolves = False
            message += f"  - Required: ``2 wolves`` > Current: ``{current['wolves']} wolves``\n"

        if current["bunnies"] >= 2:
            bunnies = True
        else:
            bunnies = False
            message += f"  - Required: ``2 bunnies`` > Current: ``{current['bunnies']} bunnies``\n"
        if current["foxes"] >= 2:
            foxes = True
        else:
            foxes = False
            message += (
                f"  - Required: ``2 foxes`` > Current: ``{current['foxes']} foxes``\n"
            )
        if coins:
            if foxes:
                if bunnies:
                    if wolves:
                        msg = await ctx.send(
                            f"{CustomEmotes.get_emote(paw=True)} Ooh! I'll help you put the pieces together~!"
                        )
                        await asyncio.sleep(3)
                        wolves = current["wolves"] - 2
                        bunnies = current["bunnies"] - 2
                        foxes = current["foxes"] - 2
                        coins = current["coins"] - 200
                        async with ctx.bot.pool.acquire() as db:
                            await db.execute(
                                "UPDATE botsettings_user SET wolves=$1, bunnies=$2, foxes=$3, coins=$4 WHERE id=$5",
                                wolves,
                                bunnies,
                                foxes,
                                coins,
                                ctx.author.id,
                            )
                            await db.execute(
                                "UPDATE botsettings_user SET boxes=$1 WHERE id=$2",
                                current["boxes"] + 1,
                                ctx.author.id,
                            )
                            await msg.edit(
                                content=f"Here you go, {ctx.author.name}! One fur box assembled to your specifications!"
                            )
                    else:
                        return await ctx.send(content=message)
                else:
                    return await ctx.send(content=message)
            else:
                return await ctx.send(content=message)
        else:
            return await ctx.send(content=message)

    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @craft_index.command(name="key")
    async def craft_key(self, ctx, amount: int = None):
        current = await self.get_user_currency(ctx, ctx.author)
        # Coin checker
        message = "Oops! Looks like you don't have the required items to make a key.\n"
        if current["coins"] >= 300:
            coins = True
        else:
            coins = False
            message += (
                f"  - Required: ``400 coins`` > Current: ``{current['coins']} coins``\n"
            )

        if current["wolves"] >= 5:
            wolves = True
        else:
            wolves = False
            message += f"  - Required: ``5 wolves`` > Current: ``{current['wolves']} wolves``\n"

        if current["bunnies"] >= 5:
            bunnies = True
        else:
            bunnies = False
            message += f"  - Required: ``5 bunnies`` > Current: ``{current['bunnies']} bunnies``\n"
        if current["foxes"] >= 5:
            foxes = True
        else:
            foxes = False
            message += (
                f"  - Required: ``5 foxes`` > Current: ``{current['foxes']} foxes``\n"
            )
        if coins:
            if foxes:
                if bunnies:
                    if wolves:
                        msg = await ctx.send(
                            f"{CustomEmotes.get_emote(paw=True)} Here, let me help you with that!"
                        )
                        await asyncio.sleep(3)
                        wolves = current["wolves"] - 5
                        bunnies = current["bunnies"] - 5
                        foxes = current["foxes"] - 5
                        coins = current["coins"] - 400
                        async with ctx.bot.pool.acquire() as db:
                            await db.execute(
                                "UPDATE botsettings_user SET wolves=$1, bunnies=$2, foxes=$3, coins=$4 WHERE id=$5",
                                wolves,
                                bunnies,
                                foxes,
                                coins,
                                ctx.author.id,
                            )
                            await db.execute(
                                "UPDATE botsettings_user SET keys=$1 WHERE id=$2",
                                current["keys"] + 1,
                                ctx.author.id,
                            )
                            await msg.edit(
                                content=f"Here's that key you wanted, {ctx.author.name}! Who needs a locksmith when you've got me~?"
                            )
                    else:
                        return await ctx.send(content=message)
                else:
                    return await ctx.send(content=message)
            else:
                return await ctx.send(content=message)
        else:
            return await ctx.send(content=message)

    @commands.command(aliases=["munbox", "massunbox"])
    @commands.max_concurrency(1, commands.BucketType.user)
    async def multiunbox(self, ctx, amt: str = None):

        if amt is None:
            return await ctx.send("You need to tell me how many boxes you want to open! **50 at most!**")
        if amt.isdigit():
            amt = int(amt)

            if amt > 50:
                return await ctx.send(
                    "I can't open that many boxes! 50 is the most I can handle at one time."
                )
            else:
                user = ctx.author

                user_info = await self.get_user_currency(ctx, user)
                db_key = user_info["keys"]
                db_box = user_info["boxes"]

                if db_box > 0 and db_key > 0:
                    db_coin = user_info["coins"]
                    db_fox = user_info["foxes"]
                    db_wolf = user_info["wolves"]
                    db_bunny = user_info["bunnies"]
                    post = ""
                    times = 1
                    coins = 0
                    foxes = 0
                    boxes = 0
                    keys = 0
                    wolves = 0
                    bunnies = 0
                    embed = discord.Embed(
                        color=self.bot.color,
                        title="Loot Engine v3.0",
                        description=post,
                    )
                    embed.set_author(
                        name=ctx.author.name, icon_url=ctx.author.avatar_url
                    )
                    embed.set_footer(text="Loot Engine V3.0")
                    msg = await ctx.send("Starting Loot Engine v3.0")
                    await asyncio.sleep(3)

                    check = 0
                    while db_box >= 0 and db_key >= 0 and amt > 0:
                        check += 1

                        if check > 50:
                            break

                        coin_rewards = randint(100, 300)
                        box_rewards = randint(1, 5)
                        key_rewards = randint(1, 5)
                        catch = False
                        item = None

                        catch, item = catching_animal_unboxing(catch)
                        db_key -= 1
                        db_box -= 1
                        coins += coin_rewards
                        db_coin += coin_rewards
                        bonus_key = random.randint(1, 100)
                        bonus_box = random.randint(1, 100)
                        keys += bonus_key
                        boxes += bonus_box

                        post += f"{times} | {coin_rewards} Coins "

                        if bonus_box <= 35:
                            post += "| Got Box! "
                            db_box += 1
                        if bonus_key <= 35:
                            db_key += 1
                            post += "| Got Key! "

                        if item == "foxes":
                            # animal = "fox"
                            foxes += 1
                            db_fox += 1
                            post += "| Got Fox! "

                        elif item == "wolves":
                            # animal = "wolves"
                            db_wolf += 1
                            wolves += 1
                            post += "| Got Wolf! "
                        elif item == "bunnies":
                            # animal = "bunny"
                            db_bunny += 1
                            bunnies += 1
                            post += "| Got Bunny! "

                        post += "\n"

                        embed = discord.Embed(
                            color=self.bot.color,
                            title="Loot Engine v3.0",
                            description=post,
                        )
                        embed.set_author(name=user.name, icon_url=user.avatar_url)
                        embed.add_field(
                            name=f"Unboxed {times} Boxes of Loot",
                            value=f"Coins: {coins}\n"
                                  f"Boxes: {boxes}\n"
                                  f"Keys: {keys}\n"
                                  f"Foxes: {foxes}\n"
                                  f"Wolves: {wolves}\n"
                                  f"Bunnies: {bunnies}\n",
                            inline=False,
                        )
                        embed.set_footer(
                            text="Boxes Ahhhhhhh", icon_url=self.bot.footer_emote
                        )
                        embed.add_field(
                            name="Item Pouch",
                            value=f"Current Boxes: {db_box}\n"
                                  f"Current Keys: {db_key}",
                        )
                        await msg.edit(content="Processing Request\n", embed=embed)
                        await asyncio.sleep(2.2)

                        times += 1
                        amt -= 1
                    times -= 1

                    completed = discord.Embed(
                        color=self.bot.color,
                        title=ctx.author.name + f" Unboxed {times} boxes.",
                    )
                    completed.set_author(
                        name="Multi Unbox System V3.0",
                        icon_url=self.bot.user.avatar_url,
                        url="https://sheri.fun/",
                    )
                    completed.add_field(
                        name="Loot Acquired",
                        value=f"Coins: {coins}\n"
                              f"Boxes: {boxes}\n"
                              f"Keys: {keys}\n"
                              f"Foxes: {foxes}\n"
                              f"Wolves: {wolves}\n"
                              f"Bunnies: {bunnies}\n",
                    )
                    completed.add_field(
                        name="New Balances",
                        value=f"Coins: {db_coin}\n"
                              f"Boxes: {db_box}\n"
                              f"Keys: {db_key}\n"
                              f"Foxes: {db_fox}\n"
                              f"Wolves: {db_wolf}\n"
                              f"Bunnies: {db_bunny}\n",
                    )
                    async with ctx.bot.pool.acquire() as db:
                        await db.execute(
                            "UPDATE botsettings_user SET wolves=$1, bunnies=$2, foxes=$3, coins=$4, boxes=$5, keys=$6 "
                            "WHERE id=$7",
                            db_wolf,
                            db_bunny,
                            db_fox,
                            db_coin,
                            db_box,
                            db_key,
                            ctx.author.id,
                        )
                    await ctx.send(embed=completed)
                    await asyncio.sleep(30)
                    await msg.delete()
                else:
                    return await ctx.send(
                        "You need at least one box and one key... aaaand it looks like you're missing one of those. "
                        "Feel free to come back when you've got what you need~"
                    )
        else:
            await ctx.send("Digit only")


def setup(bot):
    bot.add_cog(Economy(bot))
