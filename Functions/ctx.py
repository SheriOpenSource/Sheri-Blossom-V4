import discord
from discord.ext import commands
from Formats.chat_markdown import *
from API.API import Retrieval


class CustomContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self):
        return self.bot.session

    @property
    def pool(self):
        return self.bot.pool

    @property
    def redis(self):
        return self.bot.redis_pool.get()

    @property
    def log(self):
        return self.bot.log

    @property
    def color(self):
        return self.bot.color

    @property
    def sentry(self):
        return self.bot.sentry

    @property
    def bold(self):
        return bold

    @property
    def inline(self):
        return inline

    @property
    def code_block(self):
        return box

    @property
    def italics(self):
        return italics

    @property
    def strike_through(self):
        return strikethrough

    @property
    def sheri_img(self):
        return Retrieval.main_api

    async def send_error(self, content):
        channel = self.channel
        em = discord.Embed(color=self.bot.error_color, title="Error ❌")
        em.description = str(content)
        await channel.send(embed=em)

    async def bad_argument(self, content):
        channel = self.channel
        em = discord.Embed(color=self.bot.error_color, title="Invalid argument ❌")
        em.description = str(content)
        await channel.send(embed=em)

    async def group_help(self):
        message = self.message
        prefix = await self.bot.get_prefix(message)
        message.content = f"{prefix}help {self.command}"
        await self.bot.invoke(await self.bot.get_context(message, cls=CustomContext))
