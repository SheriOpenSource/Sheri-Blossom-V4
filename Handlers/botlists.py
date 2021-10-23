import json

from discord.ext import commands, tasks

lists = {
    "bots": "https://top.gg/api",
    "listcord": "https://listcord.com/api",
    "discord.bots.gg": "https://discord.bots.gg/api/v1/",
    "space": "https://api.botlist.space/v1/",
    "bfd": "https://botsfordiscord.com/api/v1/",
    "lewdbots": "https://lbots.org/api/v1",
}
authkey = {
    "bots": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjM0NjcwMjg5MDM2ODM2ODY0MCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTIwMDI1MDE3fQ.pdKTWXXu8XY3pGGPeAcPxCjkOm4kv_voV5Kyfigwjac",
    "space": "f3db25c4e6743ae3e6015d4d87c9419c101bd1ecac44b765b02293d9f489b989825238b3d01ff8cec3736ce7bcf57500",
    "discord.bots.gg": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOnRydWUsImlkIjoiMTM5ODAwMzY1MzkzNTEwNDAwIiw"
                       "iaWF0IjoxNTQ0Mjc4MzI5fQ.8_v9MMG5xW7Ff-mCVi5Srv5fH9fLHZvq5D6eY7cF74s",
    "bfd": "0cf8f7c70f3fd0b5c60d551bf5356634433f4770f7907adc314a4fa977e859d4530f014a93da7dd97c61cc8a45f8ef28e821a224131c5ea2a221713b8a15d108",
    "newdbl": "7219d8497b3b0fa59d3bb2a4b8aaf8f9e3089238e999045cd54d0f592b9ace984772af6ccc267afa5bee807cb968545fcc4d31047d098205fb6be9d22b1e2cf2",
}


class botlists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.botlist_updates.start()
        self.session = bot.session

    def cog_unload(self):
        self.botlist_updates.cancel()

    async def dbots(self):
        payload = json.dumps({"server_count": len(self.bot.guilds)})

        headers = {"authorization": authkey["bots"], "content-type": "application/json"}

        url = "{0}/bots/{1}/stats".format(lists["bots"], self.bot.user.id)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            if resp.status == 401:
                self.bot.log.info(
                    "[Bot Listings] - top.gg is returning unauthorized error."
                )
            elif resp.status == 404:
                self.bot.log.info(
                    "[Bot Listings] - top.gg is returning endpoint not found."
                )
            elif resp.status == 200:
                self.bot.log.info(
                    f"[Bot Listings] - top.gg accepted the post for guild count updates. Guilds: {payload}"
                )
            else:
                self.bot.log.info(
                    f"[Bot Listings] - top.gg is returning the code {resp.status}"
                )

    async def bfd(self):
        payload = json.dumps({"server_count": len(self.bot.guilds)})

        headers = {"Authorization": authkey["bfd"], "content-type": "application/json"}

        url = "{0}/bots/{1.user.id}".format(lists["bfd"], self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            self.bot.log.info(
                "Bots For Discord statistics returned {0.status} for {1}".format(
                    resp, payload
                )
            )

    # TODO Fix this peice of garbage api post
    # Documentation https://docs.botlist.space/bl-docs/bots
    async def botspace(self):
        payload = json.dumps({"server_count": len(self.bot.guilds)})

        headers = {
            "authorization": authkey["space"],
            "content-type": "application/json",
        }

        url = "https://api.botlist.space/v1/bots/346702890368368640"
        async with self.session.post(url, data=payload, headers=headers) as resp:
            if resp.status == 401:
                self.bot.log.info(
                    "[Bot Listings] - botlist.space is returning unauthorized error."
                )
            elif resp.status == 404:
                self.bot.log.info(
                    "[Bot Listings] - botlist.space is returning endpoint not found."
                )
            elif resp.status == 200:
                self.bot.log.info(
                    f"[Bot Listings] - botlist.space accepted the post for guild count updates. Guilds: {payload}"
                )
            else:
                self.bot.log.info(
                    f"[Bot Listings] - botlists.space is returning the code {resp.status}"
                )

    async def bots_gg(self):
        payload = json.dumps(
            {"guildCount": len(self.bot.guilds), "shardCount": len(self.bot.shards)}
        )

        headers = {
            "authorization": authkey["discord.bots.gg"],
            "content-type": "application/json",
        }

        url = "{0}/bots/{1.user.id}/stats".format(lists["discord.bots.gg"], self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            if resp.status == 401:
                self.bot.log.info(
                    "[Bot Listings] - discord.bots.gg is returning unauthorized error."
                )
            elif resp.status == 404:
                self.bot.log.info(
                    "[Bot Listings] - discord.bots.gg is returning endpoint not found."
                )
            elif resp.status == 200:
                self.bot.log.info(
                    f"[Bot Listings] - discord.bots.gg accepted the post for guild count updates. Guilds: {payload}"
                )
            else:
                self.bot.log.info(
                    f"[Bot Listings] - discord.bots.gg is returning the code {resp.status}"
                )

    async def lewdbots(self):
        payload = json.dumps(
            {"guild_count": len(self.bot.guilds), "shard_count": self.bot.shard_count}
        )
        headers = {
            "Authorization": authkey["newdbl"],
            "content-type": "application/json",
        }
        url = f'{lists["lewdbots"]}/bots/{self.bot.user.id}/stats'
        async with self.session.post(url, data=payload, headers=headers) as resp:
            if resp.status == 401:
                self.bot.log.info(
                    "[Bot Listings] - lbots.org is returning unauthorized error."
                )
            elif resp.status == 404:
                self.bot.log.info(
                    "[Bot Listings] - lbots.org is returning endpoint not found."
                )
            elif resp.status == 200:
                self.bot.log.info(
                    f"[Bot Listings] - lbots.org accepted the post for guild count updates. Guilds: {payload}"
                )
            else:
                self.bot.log.info(
                    f"[Bot Listings] - lbots.org is returning the code {resp.status}"
                )

    @tasks.loop(minutes=5)
    async def botlist_updates(self):
        voice_count = 0
        redis_count = 0
        values = [
            len(self.bot.guilds),
            len(self.bot.users),
            self.bot.counter["messages_seen"],
            self.bot.counter["guilds_join"],
            self.bot.counter["guilds_leave"],
            self.bot.counter["commands_processed"],
        ]
        value_names = [
            "sheri_guild_count",
            "sheri_user_count",
            "sheri_activity_messages",
            "sheri_guild_join",
            "sheri_guild_leave",
            "sheri_commands_processed",
        ]
        voice_channels = [617039070966710272, 617041109021097984]
        voice_channel_names = [
            f"Servers: {len(self.bot.guilds):,}",
            f"Members: {len([member for member in self.bot.users if not member.bot]):,}",
        ]
        websites = []
        try:
            # Bot lists Auto Posting
            await self.lewdbots()
            await self.bots_gg()
            await self.botspace()

            # Voice Channel checks
            for channel in voice_channels:
                if (
                        self.bot.get_channel(channel).name
                        == voice_channel_names[voice_count]
                ):
                    voice_count += 1
                    pass
                else:
                    # Voice channel update
                    variable = voice_channel_names[voice_count]
                    await self.bot.get_channel(channel).edit(
                        name=variable, reason="Guild Updates"
                    )
                    voice_count += 1

            # Redis Updating
            async with self.bot.redis_pool.get() as r:
                for value in value_names:
                    variable = values[redis_count]
                    await r.execute("set", value, variable)
                    redis_count += 1
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @botlist_updates.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(botlists(bot))
