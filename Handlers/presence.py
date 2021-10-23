from random import choice
import websockets
import discord
from discord.ext import commands, tasks

statuses = {
    "christmas": [
        "with snow ❄ | furhelp",
        "with santa 🎅 | furhelp",
        "with snowball fights ❄ | furhelp",
        "with christmas joy 🎄 | furhelp",
    ],
    "normal": [
        "with my cpu. 🛠 | furhelp",
        "with my friends. 💖 | furhelp",
        "with my tail. 😸 | furhelp",
        "with furries. 🐾 | furhelp",
        "with magic. ✨ | furhelp",
        "with foxes. 🦊 | furhelp",
        "with bunnies. 🐰 | furhelp",
        "with wolves. 🐺 | furhelp",
        "with cats. 🐱 | furhelp",
        "with floof. ☁️ | furhelp",
    ],
    "new years": [
        "with fireworks 🎆 | furhelp",
        "with new years resolutions | furhelp",
        "with the wishing game | furhelp",
    ],
    "valentines": [
        "with love 💘 | furhelp",
        "with Cupid's Bow 🏹 | furhelp",
        "with xoxoxo 💖",
    ],
    "holloween": [
        "with wands :D | furhelp",
        "Carving pumpkins 🎃| furhelp",
    ],
}

twitch = {
    "stream url": "https://api.twitch.tv/helix/streams?user_login=waspyeh",
    "game url": "https://api.twitch.tv/helix/games/?id=",
    "headers": {"Client-ID": "kosdx10n3a3rs3jxuypl9zug7g5jf9",
                "User-Agent": "Sheri Blossom V4 https://sheri.bot/",
                "Authorization": "OAuth trulralxrlgr7r3pdz1fkkfgeqcc93"},
}


class Presence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.rotate_status.start()

    def cog_unload(self):
        self.rotate_status.stop()

    async def twitch_api(self):
        check = await self.session.get(
            twitch["stream url"], headers=twitch['headers'])
        response = await check.json()
        return response

    @tasks.loop(minutes=1)
    async def rotate_status(self):
        try:
            twitch = await self.twitch_api()
            if twitch['data']:
                self.bot.log.info("[Shard Game Changer] - MASTER IS STREAMING!!! BROADCASTING IT NOW")
                await self.bot.change_presence(
                    activity=discord.Streaming(name="with my master!", url="https://twitch.tv/waspyeh"))
            else:
                status_type = statuses["normal"]
                self.bot.log.info("[Shard Game Changer] - Setting the game now...")
                random_status = choice(status_type)
                try:
                    await self.bot.change_presence(
                        activity=discord.Activity(
                            name=random_status, type=discord.ActivityType.playing
                        ),
                        status=discord.Status.online,
                    )
                except websockets.ConnectionClosed:
                    return 
                self.bot.log.info(
                    f"[Shard Game Changer] - The new game is {random_status}"
                )
                self.bot.log.info("[Shard Game Changer] - Waiting 30 seconds now..")
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @rotate_status.before_loop
    async def before_update_loop(self):
        await self.bot.change_presence(
            activity=discord.Activity(
                name="with boot sequence!", type=discord.ActivityType.playing
            ),
            status=discord.Status.dnd,
        )
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Presence(bot))
