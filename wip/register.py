import asyncio

from discord.ext import commands

from Lines.custom_emotes import get as get_emote
from utils.registration.NSFW import NSFW_Questions
from Checks.bot_checks import can_send, can_embed
import discord


# TODO 1.


class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def register_settings():
        register_output = 509374698900029445
        register_channel = 509374698900029445
        register_forum = "SFW, NSFW, CUSTOM"
        data = {
            "register_output": register_output,
            "register_channel": register_channel,
            "register_forum": register_forum,
            "register_channel_lock": False,
        }
        return data

    async def get_forum(self, ctx, forum):
        if forum == "NSFW":
            await NSFW_Questions.ask_questions(self.bot, ctx, ctx.author)

    @commands.command()
    async def register(self, ctx):
        config = self.register_settings(ctx)

        if (
            config["register_channel"] == ctx.message.channel.id
            and config["register_channel_lock"]
        ):
            return await ctx.send(
                f"Registration is not allowed in {ctx.author.channel.name}"
            )
        if not config["register_output"]:
            return await ctx.send(
                f"Registration does not have an output channel. Please set this in the dashboard."
            )
        if can_send(ctx) and can_embed(ctx):
            send_register_notif = await ctx.send(
                f"{get_emote['sheri emotes']['Paws']} "
                f"Please make sure your direct messages are open as "
                f"I will direct message you to collect your info.\n"
                f"Do not lie, as this can get you banned or penalized."
            )
            await asyncio.sleep(5)
            try:
                await send_register_notif.edit(
                    content=f"{get_emote['sheri emotes']['Paws']} **{ctx.author}** "
                    f"is currently registering,"
                    f" Please stand by........"
                )
                await self.get_forum(ctx, config["register_forum"])

            except discord.Forbidden:
                return await ctx.send(
                    "Looks like you didn't make sure your direct messages were open!"
                )


def setup(bot):
    bot.add_cog(Register(bot))
