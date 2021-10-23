from random import choice

import discord
from discord.ext import commands

from API.API import Retrieval
from Checks.bot_checks import can_send, can_embed

emotes = [":Upvote:523277460624769025", ":Downvote:523277460637351951"]
nsfw_endpoints = [
    "yiff",
    "gif",
    "bang",
    "gay",
    "ntease",
    "nseduce",
    "pussy",
    "dick",
    "bisexual",
    "cuntboy",
    "lesbian",
    "finger",
    "nhug",
    "nkiss",
    "nlick",
    "suck",
    "nboop",
    "nbound",
    "nbulge",
    "ngroup",
    "nsolo",
    "nspank",
    "ntrap",
    "nfuta",
]


class Smashnpass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # async def twitter_smash_n_pass(self, ctx):
    #    url = await Retrieval.main_api(self.bot, choice(nsfw_endpoints))
    #    await Twitter.tweet_image(
    #        self.bot, url["url"], "Smash or Pass?\n Retweet for smash, Like for pass"
    #    )

    async def content_randomization(self, amount: int):
        urls = []
        counter = 0
        while not counter == amount:
            api = await Retrieval.main_api(self.bot, choice(nsfw_endpoints))
            url = api["url"]
            urls.append(url)
            counter += 1
        return urls

    async def manage_mention(self, guild, role, mention, channel):
        role_to_edit = discord.utils.get(guild.roles, id=role)
        try:
            try:
                if mention:
                    await role_to_edit.edit(mentionable=True, reason="Smash or Pass")
                    return role_to_edit.mention
                else:
                    await role_to_edit.edit(mentionable=False, reason="Smash or Pass")
            except TypeError:
                # Looks like we have to remove it...
                async with self.bot.pool.acquire() as db:
                    await db.execute(
                        "UPDATE botsettings_smashnpass SET role_enabled=$1, role=$2 WHERE channel=$3",
                        False,
                        None,
                        channel.id,
                    )
                return "DELETED"
        except discord.Forbidden:
            message = "Permission error on role EDIT"
            return message

    @staticmethod
    async def smash_n_pass_emotes(channel, message):
        try:
            for x in emotes:
                await message.add_reaction(x)
        except discord.Forbidden:
            return await channel.send(
                "It appears that I can not add reactions to the above message. Please correct this."
            )

    async def send_smash_n_pass(
            self, role_enabled: bool, role: discord.Role, guild, channel, embed
    ):
        if channel.is_nsfw():
            if can_send(guild=guild, channel=channel) and can_embed(
                    guild=guild, channel=channel
            ):
                if role_enabled:
                    mention = await self.manage_mention(
                        guild, role, mention=True, channel=channel
                    )
                    if mention == "DELETED":
                        return await channel.send(
                            "There was an error posting the next smash n pass.\n"
                            "The error is geared to a nonexistent role!\n"
                            "Please reset and readd the role. "
                            "I will continue to attempt to post the smash n pass without pings now."
                        )
                    message = await channel.send(
                        embed=embed,
                        content=f"{mention}\n"
                                "The next smash or pass will be in 12 hours.",
                    )
                    await self.smash_n_pass_emotes(channel, message)
                    await self.manage_mention(
                        guild, role, mention=False, channel=channel
                    )
                else:
                    message = await channel.send(embed=embed)
                    await self.smash_n_pass_emotes(channel, message)

    async def smash_n_pass_logic(self, amount: int):
        urls = await self.content_randomization(amount)
        embeds = []
        for url in urls:
            embed = discord.Embed(
                color=self.bot.color,
                title="Smash or Pass?",
                description="React with a <:Upvote:523277460624769025> for smash\n"
                            "React with a <:Downvote:523277460637351951> for pass",
            )
            embed.set_image(url=url)
            embeds.append(embed)
        return embeds

    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.command(name="snp")
    async def snp(self, ctx, channel: discord.TextChannel = None, endpoint: str = None):
        if channel is None:
            channel = ctx.channel
        if channel.is_nsfw():
            sheri_api = None
            if endpoint is None:
                sheri_api = await Retrieval.main_api(self.bot, "yiff")
            elif endpoint in nsfw_endpoints and not None:
                if endpoint:
                    sheri_api = await Retrieval.main_api(self.bot, endpoint)
            else:
                return await ctx.send(
                    "Seems like you chose an invalid endpoint. Valid endpoints are:\n"
                    "```fix\n"
                    f"{', '.join(nsfw_endpoints)}```"
                )
            embed = discord.Embed(
                color=self.bot.color,
                title="Smash or Pass?",
                description="React with a <:Upvote:523277460624769025> for smash\n"
                            "React with a <:Downvote:523277460637351951> for pass",
            )
            embed.set_image(url=sheri_api["url"])
            msg = await channel.send(embed=embed)
            await self.smash_n_pass_emotes(channel, msg)
        else:
            await ctx.send(
                "Oh no! It appears that this channel is not NSFW."
                " If you want to do smash or passes, the channel must be marked NSFW. Server staff with the `Manage Messages` permission can run `furnsfw` to quicly toggle this channel setting."
            )


def setup(bot):
    bot.add_cog(Smashnpass(bot))
