import asyncio
import os
import platform
from collections import Counter
from Checks.permissions import can_send, can_react, can_embed
import coloredlogs
import logging
from Lines.custom_emotes import get as get_emote
import aiohttp
import aioredis
import asyncpg
import yaml
import discord
import sentry_sdk as sentry
from random import choice
from datetime import datetime, timedelta
from discord.ext.commands import AutoShardedBot
# from Database.custom_prefix import get_prefix
from Formats.formats import get_icon
from Checks.bot_checks import can_send, can_embed, can_react

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
    0xFF7788,
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
    discord_log = logging.getLogger("discord")
    log = logging.getLogger("bot")
    discord_log.setLevel(logging.CRITICAL)
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
    bot.color = choice(sheri_colors)
    bot.footer_emote = "https://cdn.discordapp.com/emojis/457367016823848970.png?v=1"
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
            command_prefix="fur",
            activity=discord.Game(name="https://sheri.bot/commands/ || furinvite"),
            status=discord.Status.online,
            case_insensitive=True,
            shard_count=21,
            shard_ids=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        )
        self.pool = kwargs.pop("pool")
        self.redis_pool = kwargs.pop("redis_pool")
        self.sentry = kwargs.pop("sentry")
        self.uptime = datetime.utcnow()
        self.home = self.get_guild(346892627108560901)
        self.primary_color = 0x007BFF
        self.info_color = 0x17A2B8
        self.success_color = 0x28A745
        self.warning_color = 0xFFC107
        self.danger_color = 0xDC3545
        self.counter = Counter()
        self.emote = get_emote["sheri emotes"]
        discord_log = logging.getLogger("discord")
        log = logging.getLogger("bot")
        discord_log.setLevel(logging.CRITICAL)
        self.log = log
        self.log.info(
            f"{get_icon()}\n[Shard Manager] - Configuration Received. - Launching {self.shard_count} Shards"
        )

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

    async def on_connect(self, shard_id):
        self.log.info(
            f"[Shard Manager] - [{shard_id}] shard has successfully connected to discord."
        )

    async def on_disconnect(self, shard_id):
        self.log.info(
            f"[Shard Manager] - [{shard_id}] shard has been disconnected from discord. (Internet?)"
        )

    async def on_shard_ready(self, shard_id):
        self.log.info(
            f"[Shard Primer] - Shard [{shard_id}] has been primed and ready to be fucked by the public."
        )

    async def on_resume(self, shard_id):
        self.log.info(
            f"[Shard Maintainer] - [{shard_id}] shard has resumed it's connection to discord. (Internet?) (Crash?)"
        )

    async def on_message(self, msg):
        if not self.is_ready():
            return
        await self.process_commands(msg)

    # async def get_context(self, message, *, cls=None):
    #    return await super().get_context(message, cls=cls or CustomContext)

    @staticmethod
    def error_embed(error):
        embed = discord.Embed(
            color=0xDC3545,
            description="<a:bug:474000184901369856> "
            "Error in processing command! <a:bug:474000184901369856>\n"
            "```py\n"
            f"{error}```",
        ).set_image(url="https://sheri.bot/media/command_error.png")
        embed.set_author(
            icon_url="http://myovchev.github.io/sentry-slack/images/logo32.png",
            name="Error, Logged in sentry",
            url="https://sentry.ourmainfra.me/",
        )

        embed.set_footer(
            text="Sheri Blossom, Version: v4.2",
            icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
        )
        return embed

    @staticmethod
    def format_retry_after(retry_after):
        delta = timedelta(seconds=int(round(retry_after, 0)))
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = (
                f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
            )
        elif hours:
            fmt = f"{hours} hours, {minutes} minutes, and {seconds} seconds"
        elif minutes:
            fmt = f"{minutes} minutes and {seconds} seconds"
        else:
            fmt = f"{seconds} seconds"
        return "You can try again in " + fmt

    async def on_command_error(self, ctx, exception):

        if isinstance(exception, discord.ext.commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(str(exception))

        elif isinstance(exception, discord.ext.commands.BadArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(str(exception))

        elif isinstance(exception, discord.ext.commands.CommandNotFound):
            # self.log.error(exception)
            return

        elif isinstance(exception, discord.ext.commands.CheckFailure):
            return
        elif isinstance(exception, discord.Forbidden):
            if can_send(ctx):
                return await ctx.send(
                    "Permission error has been detected. This is not my fault but your fault.\n"
                    "In order for me to work as intended, I require the following permissions\n"
                    "```fix\n"
                    "MANAGE_MESSAGES, MANAGE_ROLES, KICK_MEMBERS, BAN_MEMBERS, CHANGE_NICKNAME, "
                    "MANAGE_NICKNAMES, READ TEXT_CHANNELS & SEE VOICE CHANNELS,SEND MESSAGES, "
                    "EMBED_LINKS, ATTACH_FILES, USE_EXTERNAL_EMOJIS, ADD_REACTIONS, CONNECT, SPEAK```\n"
                    "If you are still receiving this message, Please make sure that my top role is above the roles you want me to configure."
                )
            else:
                try:
                    if can_react(ctx):
                        await ctx.message.add_reaction("❌")
                    return await ctx.author.send(
                        "Permission error has been detected. This is not my fault but your servers fault.\n"
                        "In order for me to work as intended, I require the following permissions\n"
                        "```fix\n"
                        "MANAGE_MESSAGES, MANAGE_ROLES, KICK_MEMBERS, BAN_MEMBERS, CHANGE_NICKNAME, "
                        "MANAGE_NICKNAMES, READ TEXT_CHANNELS & SEE VOICE CHANNELS,SEND MESSAGES, "
                        "EMBED_LINKS, ATTACH_FILES, USE_EXTERNAL_EMOJIS, ADD_REACTIONS, CONNECT, SPEAK```\n"
                        "If you are still receiving this message, Please make sure that my top role is above the roles you want me to configure."
                    )
                except discord.Forbidden:
                    return

        elif isinstance(exception, discord.ext.commands.CommandOnCooldown):
            delta = timedelta(seconds=int(round(exception.retry_after, 0)))
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            if days:
                fmt = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
            elif hours:
                fmt = f"{hours} hours, {minutes} minutes, and {seconds} seconds"
            elif minutes:
                fmt = f"{minutes} minutes and {seconds} seconds"
            else:
                fmt = f"{seconds} seconds"
            return await ctx.send("You can try again in " + fmt)

        elif isinstance(exception, discord.ext.commands.NoPrivateMessage):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                "This command is only allowed in discord servers, sorry!"
            )
        else:
            ctx.command.reset_cooldown(ctx)
            self.sentry.capture_exception(exception)
            embed = self.error_embed(exception)
            if isinstance(ctx.channel, discord.TextChannel):
                try:
                    if can_send(ctx) and can_embed(ctx):
                        return await ctx.send(embed=embed)
                    elif can_send(ctx):
                        return await ctx.send(
                            "Oopsie, I have encountered an error, "
                            "This has been logged and my developers will work on it as fast as possible!\n "
                            "If this continues to persist please contact us at "
                            "https://sheri.bot/support"
                        )
                except (discord.Forbidden, discord.HTTPException):
                    return
            elif isinstance(ctx.channel, discord.DMChannel):
                try:
                    await ctx.author.send(embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    return


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
