import asyncio
import random
from random import randint

import discord

from API.API import Retrieval as Get
from Checks.bot_checks import can_delete
from Formats.chat_markdown import box
from Functions.core import (send_message)
from Functions.randomization import advchoice
from Lines.custom_emotes import CustomEmotes
from Lines.names import varients

prefixes = ["!", "?", "-", ".", "<", ">", "/", "~", "+", "_", "=" ":", ";", "@", "#", "$", "%", "^", "&", "*"]
suffixes = ["!", "?", ".", "~"]
phrases = [
    "catch",
    "mine",
    "arf arf",
    "awh",
    "cute",
    "uwu",
    "owo",
    "aw",
    "aww",
    "awww",
    "awwww",
    "awwwww",
    "daw",
    "daww",
    "dawww",
    "dawwww",
    "dawwwww",
    "moo",
    "murr",
    "purr",
    "yay",
    "gotta catch em all",
    "some kind of phrase",
    "beef jerky",
    "oh dear",
    "nya",
    "nyah",
    "furriez r cool",
    "awoo",
    "awooo",
    "awoooo",
    "awooooo",
    "paw",
    "pawb",
    "pawbs",
    "fursona",
    "fursuit"
]
nsfw_phrases = [
    "daddy",
    "master",
    "slave",
    "slut",
    "whore",
    "fuck me",
    "harder",
    "faster",
    "choke me",
    "gachi",
    "gachimuchi",
    "ricardo",
    "ricardo milos",
    "me horny",
    "I’m a little foxy short and shout. Here’s is my tail hole. Here is my snout, "
    "get me on all fours and hear me shout! Oh Gawd yes! Please don’t pull out!"
]
nsfw_ends = [
    "daddy",
    "master",
    "slave"
]


def get_phrase(*, nsfw=False):
    prefix = rand_amt(prefixes)
    suffix = rand_amt(suffixes)
    body = capitalize(random.choice(phrases if not nsfw else nsfw_phrases))
    nsfw_suffix = capitalize(
        random.choice(
            nsfw_ends
        )
        if nsfw
        and not len([body.lower().count(a) for a in nsfw_ends if body.lower().count(a)]) > 0
        and len(body.split()) < 5
        else ""
     )
    return prefix + body + suffix + nsfw_suffix


def rand_amt(items):
    choice = random.randint(0, len(items))
    if choice == 0:
        return ''
    else:
        amount = random.randint(1, 3)
        to_send = ""
        for i in range(0, amount):
            to_send += random.choice(items)
        return to_send


def capitalize(string):
    seq = ""
    if len(string) > 0:
        for char in string:
            chance = random.randint(0, 1)
            if chance:  # 0 is falsy, 1 is truthy
                seq += char.upper()
            else:
                seq += char.lower()
    return seq


author = ["OwO", "UwU"]

responses = [
    "I wonder what they are going to do with it :thinking:",
    "That was a cute {animal}",
]


def catch_embed(animal, url, report_url, phrase, color):
    embed = discord.Embed(color=color,
                          title=f"A wild {animal} has spawned!",
                          description=f"Image not loading? You can view it by using this [link]({url}).\n"
                                      f"Something wrong with the image? Report it [here]({report_url})\n"
                                      f"**__Type the following phrase to capture it__!**\n"
                                      f"> Catch Phrase: `{phrase}`").set_image(url=url)
    embed.set_footer(icon_url='https://cdn.discordapp.com/emojis/457367016823848970.png?v=1',
                     text="Image Hosted on: https://sheri.bot/ | Powered by: https://furhost.net")
    return embed


def animal_type(channel):
    if channel:
        animals = ["foxes", "wolves", "bunnies", "cats", 'lustshards', 'keyshards']
        return advchoice(animals)
    else:
        animals = ["foxes", "wolves", "bunnies", "cats", 'keyshards']
        return advchoice(animals)


async def confirm_capture(ctx, author, usrdata, imgjson, animal_name, animal, dm: bool = False):
    paws = CustomEmotes.get_emote(paw=True)
    embed = discord.Embed(color=ctx.bot.color,
                          title=f"{paws} {author.display_name} caught the wild {animal_name[animal]}! {paws}",
                          description=f"{'I sent the image to your DMs ' if dm else 'Want the image sent to your DMs? Go to https://sheri.bot/settings/profile/ to enable the option. '}"
                                      f"{'(Keep in mind you must be logged into the website via Discord to access profile settings.)'}\n"
                                      f"**{author.display_name}** now has ``{usrdata} {animal}``")
    embed.set_footer(icon_url='https://cdn.discordapp.com/emojis/457367016823848970.png?v=1',
                     text="Image Hosted on: https://sheri.bot/ | Powered by: https://furhost.net")
    embed.set_author(icon_url=imgjson['url'], url=imgjson['url'],
                     name="Click here for the image that was caught")
    await send_message(ctx, embed=embed, custom_emoji=True, delete_delay=20)
    if dm:
        try:
            embed = discord.Embed(
                color=ctx.bot.color,
                description=f"You caught {animal_name[animal]} in "
                            f"**{ctx.guild.name}**.\n"
                            f"Here is the image. [**{animal_name[animal]} image**]({imgjson['url']})",
            )
            embed.set_image(url=imgjson['url'])
            await author.send(f"You now have {usrdata} {animal} ^_^", embed=embed)
        except discord.Forbidden:
            pass


async def initiate_catch(self, ctx):
    async with self.bot.pool.acquire() as db:
        if not ctx.guild:
            return 
        enabled = await db.fetchval(
            "SELECT catching_enabled FROM botsettings_guild WHERE id=$1", ctx.guild.id
        )
        if not enabled:
            return
        guild_data = await db.fetchrow("SELECT catching_channels, premium FROM botsettings_guild WHERE id=$1",
                                       ctx.guild.id)
        channels = guild_data['catching_channels']
        premium = guild_data['premium']
        if ctx.channel.id in channels:
            async with self.bot.redis_pool.get() as r:
                res = await r.execute("get", ctx.channel.id)
                if not res:
                    await r.execute("set", ctx.channel.id, 0)
                    res = 0
                if premium:
                    chance = randint(25, 35)
                else:
                    chance = randint(35, 45)
                if int(res) > chance:
                    self.bot.counter['catching_initiated'] += 1
                    await r.execute("set", ctx.channel.id, 0)
                    # animals = ["foxes", "wolves", "bunnies", "cats"]
                    animal = animal_type(ctx.channel.is_nsfw())
                    await r.execute("incr", f"{animal}_spawned")
                    animal_name = {"foxes": "fox",
                                   "wolves": "wolf",
                                   "bunnies": "bunny",
                                   "cats": "cat",
                                   "keyshards": "furry",
                                   "lustshards": "lewd furry"}
                    image = await get_image_url(self, animal)
                    catch_phrase = get_phrase(nsfw=True if ctx.channel.is_nsfw() else False)
                    embed = catch_embed(animal_name[animal], image['url'], image['report_url'], catch_phrase,
                                        self.bot.color)
                    msg = await send_message(ctx, embed=embed)

                    def check(m):
                        return m.content == catch_phrase and m.channel == ctx.channel

                    try:
                        answer = await self.bot.wait_for(
                            "message", check=check, timeout=60
                        )
                    except asyncio.TimeoutError:
                        timeout_message = await ctx.send(
                            f"The wild {animal_name[animal]} escaped!"
                        )
                        try:
                            await msg.delete()
                            await asyncio.sleep(3)
                            await timeout_message.delete()
                        except discord.NotFound:
                            return
                        except discord.Forbidden:
                            return await send_message(ctx, message= "I don't have enough permissions to fully utilize "
                                                                    "the catching system")
                        return
                    except discord.NotFound:
                        return
                    else:
                        if answer:
                            await r.execute("incr", f"{animal}_caught")
                            try:
                                await msg.delete()
                            except discord.NotFound:
                                pass
                            else:
                                pass
                            
                            sql = (
                                f"UPDATE botsettings_user SET {animal}all = {animal}all + 1, {animal} ="
                                f" {animal} + 1 WHERE id=$1"
                            )
                            await db.execute(sql, answer.author.id)
                            sql = f"SELECT {animal} FROM botsettings_user WHERE id=$1"
                            new_count = await db.fetchval(sql, answer.author.id)
                            wants_dm = await db.fetchval(
                                "SELECT animal_catch_dm FROM botsettings_user WHERE id=$1",
                                answer.author.id,
                            )
                            await confirm_capture(ctx, answer.author, new_count, image, animal_name, animal,
                                                  dm=wants_dm)

                            await asyncio.sleep(5)

                            def delete_check(m):
                                return m.content.lower() == catch_phrase.lower()

                            try:
                                if can_delete(ctx):
                                    return await ctx.channel.purge(
                                        limit=100, check=delete_check
                                    )
                            except discord.HTTPException:
                                pass
                else:
                    await r.execute("incr", ctx.channel.id)


async def get_image_url(self, animal):
    if animal == "foxes":
        image = await Get.main_api(self.bot, "fox")
        return image
    elif animal == "wolves":
        image = await Get.main_api(self.bot, "wolves")
        return image
    elif animal == "bunnies":
        image = await Get.main_api(self.bot, "bunny")
        return image
    elif animal == "cats":
        image = await Get.main_api(self.bot, "cat")
        return image
    elif animal == "lustshards":
        image = await Get.main_api(self.bot, "yiff")
        return image
    elif animal == "keyshards":
        image = await Get.main_api(self.bot, "mur")
        return image
