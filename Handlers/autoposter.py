import asyncio

import discord
from discord.ext import commands, tasks
import API.API
from Checks.bot_checks import can_send, can_embed
from Lines.valid_endpoints import endpoints_nsfw, endpoints_sfw


class AutopostEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autopost.start()

    def cog_unload(self):
        self.autopost.stop()

    def image_embed(self, url, endpoint, report_url):
        embed = discord.Embed(color=self.bot.color, title=f"Category: {endpoint}",
                              description=f"**<:globe:451849914096287745> [Image Url]({url})\n"
                                          f"Something Wrong? [Report it Here]({report_url})**\n"
                                          f"``{report_url}``")
        embed.set_image(url=url)
        return embed

    @staticmethod
    async def edit_to_nsfw(channel):
        try:
            await channel.edit(nsfw=True, reason="[Auto Poster] Endpoint contains Sexual content")
        except discord.Forbidden:
            return

    async def send_post(self, guild, channel, endpoint):
        api_request = await API.API.Retrieval.main_api(self.bot, endpoint)
        if not api_request['report_url']:
            return
        if not guild or not channel:
            return
        if not can_send(guild=guild, channel=channel):
            return
        try:
            if endpoint in endpoints_nsfw:
                if not channel.is_nsfw():
                    await self.edit_to_nsfw(channel)

                if can_embed(guild=guild, channel=channel):
                    embed = self.image_embed(url=api_request['url'], endpoint=endpoint,
                                             report_url=api_request['report_url'])
                    await channel.send(embed=embed)
                    return self.bot.log.info(f"[Auto Post] Sent an image in {guild.name}")
                await channel.send(content=f"{api_request['url']}\n"
                                           f"``{api_request['report_url']}``")
                self.bot.log.info(f"[Auto Post] Sent an image in {guild.name}")
            if endpoint in endpoints_sfw:
                if can_embed(guild=guild, channel=channel):
                    embed = self.image_embed(url=api_request['url'], endpoint=endpoint,
                                             report_url=api_request['report_url'])
                    await channel.send(embed=embed)
                    return self.bot.log.info(f"[Auto Post] Sent an image in {guild.name}")
                await channel.send(content=f"{api_request['url']}\n"
                                           f"``{api_request['report_url']}``")
                self.bot.log.info(f"[Auto Post] Sent an image in {guild.name}")

        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @tasks.loop(minutes=10)
    async def autopost(self):
        self.bot.log.info(f"[Auto post] Starting the loop")
        try:
            async with self.bot.pool.acquire() as db:
                autopost_data = await db.fetch("SELECT * FROM botsettings_autoposter WHERE enabled=True")
                counter = 0
                for data in autopost_data:
                    if counter == 5:
                        counter = 0
                        await asyncio.sleep(4)
                    guild = self.bot.get_guild(data['guild_id'])
                    if not guild:
                        pass
                    channel = guild.get_channel(data['channel'])
                    await self.send_post(guild=guild, channel=channel, endpoint=data['endpoint'])
                    counter += 1
            self.bot.log.info(f"[Auto post] Loop finished, SLeeping for 10")
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @autopost.before_loop
    async def before_update_loop(self):
        self.bot.log.info("[Autopost Manager] - Waiting for the on_ready signal.......")
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(AutopostEvent(bot))
