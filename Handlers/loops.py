import asyncio
import datetime

import discord
import pytz
from discord.ext import commands, tasks

from API.API import Retrieval
from Functions.reminders import Reminders
from Functions.snp import send_smash_n_pass
from Lines.valid_endpoints import endpoints_nsfw, endpoints_sfw

emotes = [":Upvote:523277460624769025", ":Downvote:523277460637351951"]

sfw_endpoints = endpoints_sfw
nsfw_endpoints = endpoints_nsfw


# don't comment out or i will break your legs myself
class Loops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.smash_or_pass_auto.start()
        # self.auto_poster.start()
        self.reminder_loop.start()
        self.update_command_count.start()

    def cog_unload(self):
        self.smash_or_pass_auto.stop()
        # self.auto_poster.stop()
        self.reminder_loop.stop()
        self.update_command_count.stop()

    @tasks.loop(minutes=5)
    async def smash_or_pass_auto(self):
        try:
            async with self.bot.pool.acquire() as db:
                channels = await db.fetch(
                    "SELECT * FROM botsettings_smashnpass WHERE enabled=True"
                )
                now = datetime.datetime.now()
                next_message = now + datetime.timedelta(hours=12)
                self.bot.log.info("[Smash n Pass] - Starting.....")
                self.bot.log.info(
                    f"[Smash n Pass] - Obtained {len(channels)} configured channels."
                )
                for channel in channels:
                    await asyncio.sleep(5.5)

                    guild = self.bot.get_guild(id=channel["guild_id"])
                    ch = guild.get_channel(channel["channel"])
                    next_db_message = (
                        True if channel["next_message"] is not None else False
                    )
                    if next_db_message:
                        if datetime.datetime.now(pytz.utc) >= channel["next_message"]:
                            if ch is not None:
                                if ch.is_nsfw():
                                    self.bot.log.info(
                                        f"[Smash N pass] - Posting on {ch.name} in {guild.name}.."
                                    )
                                    sheri_api = await Retrieval.main_api(
                                        self.bot, channel["endpoint"]
                                    )
                                    embed = discord.Embed(
                                        color=self.bot.color,
                                        title="Smash or Pass?",
                                        description="React with a <:Upvote:523277460624769025> for smash\n"
                                                    "React with a <:Downvote:523277460637351951> for pass",
                                    )
                                    embed.set_image(url=sheri_api["url"])
                                    await send_smash_n_pass(
                                        role_enabled=channel["role_enabled"],
                                        role=channel["role"],
                                        guild=guild,
                                        embed=embed,
                                        channel=ch,
                                    )
                                    self.bot.log.info(
                                        "[Smash n Pass] - Posted the image :)"
                                    )
                                    await db.execute(
                                        "UPDATE botsettings_smashnpass SET next_message=$1 WHERE channel=$2 AND endpoint=$3",
                                        next_message,
                                        channel["channel"],
                                        channel["endpoint"]

                                    )
                            else:
                                pass
                    else:
                        self.bot.log.info("[Smash n Pass] - NEW CHANNEL DETECTED!!")
                        if ch is not None:
                            if ch.is_nsfw():
                                sheri_api = await Retrieval.main_api(
                                    self.bot, channel["endpoint"]
                                )
                                embed = discord.Embed(
                                    color=self.bot.color,
                                    title="Smash or Pass?",
                                    description="React with a <:Upvote:523277460624769025> for smash\n"
                                                "React with a <:Downvote:523277460637351951> for pass",
                                )
                                embed.set_image(url=sheri_api["url"])

                                await send_smash_n_pass(
                                    role_enabled=channel["role_enabled"],
                                    role=channel["role"],
                                    guild=guild,
                                    embed=embed,
                                    channel=ch,
                                )
                                await db.execute(
                                    "UPDATE botsettings_smashnpass SET next_message=$1 WHERE channel=$2 AND endpoint=$3",
                                    next_message,
                                    channel["channel"],
                                    channel['endpoint']
                                )
                                self.bot.log.info("[Smash n Pass] - Posted an Image :)")
                            else:
                                await ch.edit(
                                    nsfw=True, reason="Smash n passes are NSFW!!!"
                                )
                        else:
                            await db.execute(
                                "DELETE FROM botsettings_smashnpass WHERE channel=$1",
                                channel["channel"],
                            )
                    await asyncio.sleep(3)

        except Exception as e:
            self.bot.log.error(f"[Auto Smash N Pass]{e}")
            self.bot.sentry.capture_exception(e)

    @tasks.loop(minutes=1)
    async def reminder_loop(self):
        try:
            await Reminders.check(self.bot)
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @tasks.loop(minutes=1)
    async def update_command_count(self):
        try:
            self.bot.log.info("[Statistics Updater] - Attempting to save the statuses from counter")
            async with self.bot.pool.acquire() as db:
                self.bot.log.info("[Statistics Updater] - Copying and clearing counter...")
                temp_counter = self.bot.counter.copy()
                self.bot.counter.clear()
                for command, count in temp_counter.items():
                    await db.execute(
                        """INSERT INTO botsettings_commandcount (command, usage_count) VALUES ($1, $2)
                        ON CONFLICT (command) DO UPDATE 
                        SET usage_count = botsettings_commandcount.usage_count + EXCLUDED.usage_count""",
                        command, count
                    )
            self.bot.log.info("[Statistics Updater] - Done, stats saved to DB")
        except Exception as e:
            self.bot.log.info("[Statistics Updater] - Error - Sent to Sentry")
            self.bot.sentry.capture_exception(e)


    @smash_or_pass_auto.before_loop
    @reminder_loop.before_loop
    @update_command_count.before_loop
    async def before_update_loop(self):
        self.bot.log.info("[Loops Manager] - Waiting for the on_ready signal.......")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Loops(bot))
