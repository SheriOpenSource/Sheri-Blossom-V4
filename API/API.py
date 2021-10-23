# APIs Managed by us.
import os

import discord

base_url = "https://sheri.bot/api/"

mainframe = ""



class Retrieval:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    async def main_api(self, endpoint):
        async with self.session.get(
                base_url + endpoint, headers=headers,
        ) as resp:
            if resp.status == 200:
                json = await resp.json()
                return json
            else:
                return {"url": "https://sheri.bot/media/service-unavaliable.png"}

    async def main_api_multiple(self, endpoint, count):
        async with self.session.get(
                base_url + endpoint + f"?count={count}",
                headers=headers,
        ) as resp:
            if resp.status == 200:
                json = await resp.json()
                return json
            else:
                results = []
                for x in count:
                    results.append({"url": "https://sheri.bot/media/service-unavaliable.png"})
                return results

    @staticmethod
    async def fetch_ship_or_smash_img(ctx, user1, user2, nsfw: bool = False):
        if nsfw:
            async with ctx.session.get(base_url + f"smash?p1={user1}&p2={user2}",
                                       headers=headers) as resp:
                if resp.status == 200:
                    response = await resp.read()
                    with open("ship.png", "wb") as f:
                        f.write(response)
                    return True, discord.File("ship.png")
                else:
                    return False, None
        else:
            async with ctx.session.get(base_url + f"ship?p1={user1}&p2={user2}",
                                       headers=headers) as resp:
                if resp.status == 200:
                    response = await resp.read()
                    with open("ship.png", "wb") as f:
                        f.write(response)
                    return True, discord.File("ship.png")
                else:
                    return False, None
