import json

lists = {
    "bots": "https://discordbots.org/api",
    "listcord": "https://listcord.com/api",
    "discord.bots.gg": "https://discord.bots.gg/api/v1/",
    "space": "https://api.botlist.space/",
    "bfd": "https://botsfordiscord.com/api/v1/",
    "lewdbots": "https://lbots.org/api/v1",
}
authkey = {
    "bots": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjM0NjcwMjg5MDM2ODM2ODY0MCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTIwMDI1MDE3fQ.pdKTWXXu8XY3pGGPeAcPxCjkOm4kv_voV5Kyfigwjac",
    "space": "5675fac090840e710d156bfdd6c30a56b5b5cb6658813f640b1293"
    "fa4f1139a12e73c3a9937605ce6e87ee948504cb645e6d7b29f601c4"
    "c4333261d01220b895",
    "discord.bots.gg": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOnRydWUsImlkIjoiMTM5ODAwMzY1MzkzNTEwNDAwIiw"
    "iaWF0IjoxNTQ0Mjc4MzI5fQ.8_v9MMG5xW7Ff-mCVi5Srv5fH9fLHZvq5D6eY7cF74s",
    "bfd": "0cf8f7c70f3fd0b5c60d551bf5356634433f4770f7907adc314a4fa977e859d4530f014a93da7dd97c61cc8a45f8ef28e821a224131c5ea2a221713b8a15d108",
    "newdbl": "7219d8497b3b0fa59d3bb2a4b8aaf8f9e3089238e999045cd54d0f592b9ace984772af6ccc267afa5bee807cb968545fcc4d31047d098205fb6be9d22b1e2cf2",
}


class Botlists:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    async def dbots(self):
        payload = json.dumps({"server_count": len(self.bot.guilds)})

        headers = {"authorization": authkey["bots"], "content-type": "application/json"}

        url = "{0}/bots/{1}/stats".format(lists["bots"], self.bot.user.id)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            print("DBots statistics returned {0.status} for {1}".format(resp, payload))

    async def bfd(self):
        payload = json.dumps({"server_count": len(self.bot.guilds)})

        headers = {"Authorization": authkey["bfd"], "content-type": "application/json"}

        url = "{0}/bots/{1.user.id}".format(lists["bfd"], self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            print(
                "Bots For Discord statistics returned {0.status} for {1}".format(
                    resp, payload
                )
            )

    async def botspace(self):
        payload = json.dumps({"server_count": len(self.bot.guilds)})

        headers = {
            "authorization": authkey["space"],
            "content-type": "application/json",
        }

        url = "{0}/bots/{1.user.id}/".format(lists["space"], self.bot)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            print(
                "botlist.space statistics returned {0.status} for {1}".format(
                    resp, payload
                )
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
            print(
                "https://discord.bots.gg/ statistics returned {0.status} for {1}".format(
                    resp, payload
                )
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
            print(
                "lewdbots.org statistics returned {0.status} for {1}".format(
                    resp, payload
                )
            )

    async def ds(self):
        payload = {"server_count": len(self.bot.guilds)}
        headers = {
            "Authorization": "ux0zjo1xri78xr4i64iqffe157ie6nbpryiqv7wub5elogoqm3"
        }
        url = "https://discord.services/api/bots/{}/".format(self.bot.user.id)
        async with self.bot.session.post(url, json=payload, headers=headers) as resp:
            print(
                "http://discord.services statistics returned {0.status} for {1}".format(
                    resp, payload
                )
            )
