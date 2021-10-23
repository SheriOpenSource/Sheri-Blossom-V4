import asyncio
import mimetypes
import os
from random import choice

import discord
import requests
import tweepy
from discord.ext import commands, tasks

from API.API import Retrieval as Get
from Lines.valid_endpoints import *

consumer_key = "2lZTcyv7P3cyAjFTubzt0NiX5"
consumer_secret = "IhlgGutn2D5UIaBBJi7G8rS8Y7ty4hoQzdCLh6JBiHPubPDYXz"
access_token = "919695694499377152-FaESHG86lYAglgDt9pMQydzf2CKzW5p"
access_token_secret = "5Vb2dsVvc2CDfa6o9YhQ5a99tsXLOyayIKXBaF7Sj5Aqt"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def get_random_string(
        length=12,
        allowed_chars="abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
):
    return "".join(choice(allowed_chars) for i in range(length))


def get_name():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return get_random_string(5, chars)


class Twitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.auto_poster.start()

    def cog_unload(self):
        self.auto_poster.cancel()

    @commands.group(name="twitter", hidden=True)
    async def twitter_index(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(".")

    @staticmethod
    async def tweet_image(url, msg, self):
        request = requests.get(url, stream=True)
        if request.status_code == 200:
            content_type = request.headers["content-type"]
            extension = mimetypes.guess_extension(content_type)
            filename = get_name() + extension
            try:
                with open(filename, "wb") as image:
                    for chunk in request:
                        image.write(chunk)
                    self.bot.log.info(
                        f"[Auto Tweeter] - Attempting to send {image} to Sheri's Twitter........."
                    )
                    api.update_with_media(filename, msg)
                os.remove(filename)
                self.bot.log.info(f"[Auto Tweeter] - {image} has been successfully sent....")
            except Exception as e:
                self.bot.log.info(f"[Auto Tweeter] - {e}\n" f"Too big most likely...")
                os.remove(filename)
                pass
        else:
            self.bot.log.info("[Auto Tweeter] - Unable to download image")

    @twitter_index.command(name="user")
    async def twitter_user(self, ctx):
        twitter_user = api.get_user("twitter")
        embed = discord.Embed(
            color=self.bot.color,
            description=f"{twitter_user.screen_name}\n"
                        f"{twitter_user.followers_count}",
        )
        await ctx.send(embed=embed)

    @tasks.loop(minutes=2)
    async def auto_poster(self):
        self.bot.log.info("[Auto Tweeter]- Starting the Tweet Loop")
        try:

            # endpoints = [
            #     "yiff",
            #     "ngroup",
            #     "gay",
            #     "tease",
            #     "bang",
            #     "fsolo",
            #     'msolo',
            #     'cuntboy',
            #     'booty',
            #     "nspank",
            #     "pussy",
            #     "nbound",
            #     "nfemboy",
            # ]
            random_endpoint = choice(endpoints_nsfw)
            img = await Get.main_api(self.bot, random_endpoint)
            url = img['url']
            report = img['report_url']
            message = (f"🌐 DOWNLOAD URL: {url}\n"
                       f"🔔 REPORT URL: {report}\n"
                       f"#yiff #yiffartwork #yiffart #furryporn\n"
                       f"#furrynsfw #porn")
            await self.tweet_image(url, message, self)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @auto_poster.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Twitter(bot))
