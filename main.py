import asyncio
import logging
import os
import platform
from collections import Counter
from datetime import datetime

import aiohttp
import aioredis
import asyncpg
import coloredlogs
import discord
import sentry_sdk as sentry
import yaml
from discord.ext.commands import AutoShardedBot

from Database.custom_prefix import Prefixes
from Formats.chat_markdown import bold, inline
from Formats.formats import (
    get_icon, avatar_check,
    format_retry_after)
from Functions.core import (
    embed_color, send_message, make_embed)
from Functions.ctx import CustomContext
from Lines.custom_emotes import footer
from Lines.custom_emotes import get as get_emote

logger = logging.getLogger()

sheri_colors = [
    0xFCBACB,
    0xFDABBF,
    0xFD9DB4,
    0xFE8EA8,
    0xFE7F9C,
    0xFFC0CB,
    0xDD96C4,
    0xE19AD3,
    0xF0AEED,
    0xF2B7F0,
    0xF6C9EE,
    0xF3B9E9,
    0xF1A8E4,
    0xEF6BB0,
    0xFF8899,
    0xFF7788
]

sentry.init(
    "https://2c5e35943bc142c085b059cf0757695f@sentry.ourmainfra.me/4",
    attach_stacktrace=True,
    max_breadcrumbs=100,
)


def setup_logger():
    with open("Config/logging.yml", "r") as log_config:
        config = yaml.safe_load(log_config)

    coloredlogs.install(
        level="INFO",
        logger=logger,
        fmt=config["formats"]["console"],
        datefmt=config["formats"]["datetime"],
        level_styles=config["levels"],
        field_styles=config["fields"],
    )

    # file = logging.FileHandler(filename=f"logs/bot.log", encoding="utf-8", mode="w")
    # ile.setFormatter(logging.Formatter(Config["formats"]["file"]))
    # logger.addHandler(file)
    return logger


async def run():
    setup_logger()
    log = logging.getLogger("bot")
    discord_log = logging.getLogger("discord")
    discord_log.setLevel(logging.INFO)
    description = "Sheri Blossom, the best furry bot out there"
    credentials = {
        "user": os.environ["PG_USER"],
        "password": os.environ["PG_PASSWORD"],
        "database": "sheri",
        "host": "127.0.0.1",
    }
    db_pool = await asyncpg.create_pool(**credentials)
    redis_pool = await aioredis.create_pool(
        "redis://localhost", password=os.environ["REDIS_PASSWORD"]
    )
    bot = Bot(
        description=description, pool=db_pool, redis_pool=redis_pool, sentry=sentry
    )
    bot.color = embed_color()
    bot.footer_emote = footer
    bot.session = aiohttp.ClientSession(loop=bot.loop)
    bot.sentry = sentry
    if __name__ == "__main__":
        commands = 0
        for extension in os.listdir("Commands"):
            if extension.endswith(".py"):
                try:
                    extension = "Commands." + extension[:-3]
                    bot.load_extension(extension)
                    commands += 1
                except Exception as e:
                    log.error(
                        f"Failed to load cog {extension}\n"
                        f"Exception: {e}\n"
                        f"{e.__cause__}"
                    )
                    sentry.capture_exception(e)
        log.info(f"[Commands Manager] - Loaded {commands} command cogs")
        handlers = 0
        for extension in os.listdir("Handlers"):
            if extension.endswith(".py"):
                try:
                    extension = "Handlers." + extension[:-3]
                    bot.load_extension(extension)
                    handlers += 1
                except Exception as e:
                    log.error(
                        f"Failed to load cog {extension}\n"
                        f"Exception: {e}\n"
                        f"{e.__cause__}"
                    )
                    sentry.capture_exception(e)
        log.info(f"[Handler Manager] - Loaded {handlers} Handlers")
    try:
        await bot.start(os.environ["SHERI_PROD_KEY"])
    except KeyboardInterrupt:
        await db_pool.close()
        await bot.logout()


class Bot(AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description"),
            command_prefix=Prefixes.get,
            # activity=discord.Game(name="https://sheri.bot/commands/ || furinvite"),
            status=discord.Status.idle,
            case_insensitive=True,
            shard_count=20,
            max_messages=10000
        )
        self.pool = kwargs.pop("pool")
        self.redis_pool = kwargs.pop("redis_pool")
        self.sentry = kwargs.pop("sentry")
        self.uptime = datetime.utcnow()
        self.home = 346892627108560901
        self.primary_color = 0x007BFF
        self.info_color = 0x17A2B8
        self.success_color = 0x28A745
        self.warning_color = 0xFFC107
        self.danger_color = 0xDC3545
        self.counter = Counter()
        self.emote = get_emote["sheri emotes"]
        log = logging.getLogger("bot")
        discord_log = logging.getLogger("discord")
        discord_log.setLevel(logging.INFO)
        self.log = log
        self.log.info(
            f"{get_icon()}\n[Shard Manager] - Configuration Received. - Launching {self.shard_count} Shards"
        )

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)

    async def on_ready(self):
        self.log.info(
            f"########################################################################\n"
            f"- I have successfully connected to discord!\n"
            f"- Bot account: {self.user}\n"
            f"- Guilds: {len(self.guilds):,}\n"
            f"- Users: {len([member for member in self.users if not member.bot]):,}\n"
            f"- Bots: {len([bot for bot in self.users if bot.bot]):,}\n"
            f"- Discord.py Version: {discord.__version__}\n"
            f"- Python Version: {platform.python_version()}\n"
            f"########################################################################"
        )
        self.log.info("I am now listening for commands/events.")

    async def on_connect(self):
        await self.change_presence(
            activity=discord.Activity(name="Handling my business!", type=discord.ActivityType.playing),
            status=discord.Status.dnd)

    # async def on_disconnect(self):
    #    self.gateway_server_name = json.loads(self.shards[0].ws._trace[0])[0]
    #    self.session_server_name = json.loads(self.shards[0].ws._trace[0])[1]["calls"][0]

    async def on_shard_ready(self, shard_id):
        self.log.info(
            f"""#######################################################################################################
                ####### PUSSY SHARD {shard_id} SUCCESSFULLY ESTABLISHED CONNECTION AND READY FOR GANG BANGS ###########
                #######################################################################################################"""

        )

    # async def get_context(self, message, *, cls=None):
    #    return await super().get_context(message, cls=cls or CustomContext)

    async def on_command_error(self, ctx, exception):
        try:
            if isinstance(exception, discord.ext.commands.MissingRequiredArgument):
                ctx.command.reset_cooldown(ctx)
                return await send_message(ctx,
                                          embed=make_embed(color=embed_color(),
                                                           thumbnail=avatar_check(self.user),
                                                           title="<:error:451845273124208652> Missing Argument",
                                                           description=f"{exception}\n"
                                                                       f"Usage: ``fur{ctx.command.name} "
                                                                       f"{ctx.command.signature}``",
                                                           author="Command Help",
                                                           author_icon=avatar_check(self.user),
                                                           author_link="https://sheri.bot/commands",
                                                           footer_icon="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                                                           footer_text="Powered by furhost.net"),
                                          custom_emoji=True)
            elif isinstance(exception, discord.ext.commands.BadArgument):
                ctx.command.reset_cooldown(ctx)
                return await send_message(ctx,
                                          embed=make_embed(color=embed_color(),
                                                           thumbnail=avatar_check(self.user),
                                                           title="<:error:451845273124208652> Bad Argument",
                                                           description=f"{exception}\n"
                                                                       f"Usage: ``fur{ctx.command.name} "
                                                                       f"{ctx.command.signature}``",
                                                           author="Command Help",
                                                           author_icon=avatar_check(self.user),
                                                           author_link="https://sheri.bot/commands",
                                                           footer_icon="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                                                           footer_text="Powered by furhost.net"),
                                          custom_emoji=True)

            elif isinstance(exception, discord.ext.commands.CommandNotFound):
                return

            elif isinstance(exception, discord.ext.commands.CheckFailure):
                return

            elif isinstance(exception, discord.NotFound):
                return
            elif isinstance(exception, OSError):
                return
            elif isinstance(exception, discord.HTTPException):
                if exception.status == 503:
                    return
            elif isinstance(exception, discord.ext.commands.CommandOnCooldown):
                return await send_message(ctx,
                                          message=f"Slow down, {bold(ctx.author)}! {bold(inline(ctx.command))} is currently on cooldown.\n"
                                                  f"{format_retry_after(exception.retry_after)}.😉")
            elif isinstance(exception, discord.ext.commands.MaxConcurrencyReached):
                return await send_message(ctx,
                                          message=f"Slow down, {bold(ctx.author.name)}! "
                                                  f"You can only run {bold(inline(ctx.command))} "
                                                  f"{bold(str(exception.number))} time(s) at once. "
                                                  f"You can try again after the command has finished processing. 😉")

            elif isinstance(exception, discord.ext.commands.NoPrivateMessage):
                ctx.command.reset_cooldown(ctx)
                return await send_message(ctx, message="This command is only allowed in discord servers, sorry!")
            else:
                ctx.command.reset_cooldown(ctx)
                self.sentry.capture_exception(exception)
                cmd = ctx.command.name
                message = (
                    f"<a:error:474000184263573544> | **UNEXPECTED ERROR IN ``{cmd}``** | <a:error:474000184263573544>\n"
                    "I have logged the error and have alerted the team. If this error continues to persist, please reach out to us!\n"
                    f"**```fix\n{exception}```**"
                )
                return await send_message(ctx, message=message, custom_emoji=True)
        except Exception as e:
            self.sentry.capture_exception(e)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
except KeyboardInterrupt:
    pass
