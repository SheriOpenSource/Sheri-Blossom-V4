import contextlib
import importlib
import inspect
import io
import os
import re
import subprocess
import textwrap
import time
import traceback
from io import BytesIO

import aiohttp
import discord
import psutil
import requests
from discord.ext import commands

from Checks.bot_checks import can_embed, can_send
from Checks.checks import is_owner, is_dev
from Formats.formats import pagify, avatar_check
from Functions.core import commands_help

ENV = {
    "contextlib": contextlib,
    "inspect": inspect,
    "io": io,
    "os": os,
    "re": re,
    "textwrap": textwrap,
    "time": time,
    "traceback": traceback,
    "BytesIO": BytesIO,
    "discord": discord,
    "psutil": psutil
}


async def on_command_error(ctx, self, exception):
    if isinstance(exception, commands.NoPrivateMessage):  # line in question.
        await ctx.author.send("\N{WARNING SIGN} Sorry that command can't be ran in private messages!")


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())
        self.env = ENV
        self.stdout = io.StringIO()
        self.main_guild = 346892627108560901
        self.vip_role = 455064679845330945
        self.dev_role = 418538906057965574
        self.support_role = 491694625355202564

    async def _eval(self, ctx, code):
        if code == "exit()":
            self.env = ENV
            return await ctx.send(f"```Reset history!```")
        if "config/config.yml" in code:
            return await ctx.send_error("You cannot write to the config, please use `bot.config()` to read it.")

        env = {
            "message": ctx.message,
            "author": ctx.author,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "ctx": ctx,
            "self": self,
            "bot": self.bot
        }

        self.env.update(env)

        _code = \
            f"""
async def func():
    try:
        with contextlib.redirect_stdout(self.stdout):
{textwrap.indent(code, '            ')}
        if '_' in locals():
            if inspect.isawaitable(_):
                _ = await _
            return _
    finally:
        self.env.update(locals())
            """

        start = time.time()
        try:
            exec(_code, self.env)
            func = self.env['func']
            res = await func()

        except:
            res = traceback.format_exc()

        end = time.time()
        out, embed = self._format(code, res)
        try:
            await ctx.send(f"```py\n{out}\n\nTime to execute: {round((end - start) * 1000, 3)}ms```", embed=embed)
        except discord.HTTPException:
            data = BytesIO(out.encode('utf-8'))
            await ctx.send(content=f"The result was a bit too long.. so here is a text file instead 🎁",
                           file=discord.File(data, filename=f'Result.txt'))

    def _format(self, inp, out):
        self.env["_"] = out

        res = ""

        # Erase temp input we made
        if inp.startswith("_ = "):
            inp = inp[4:]

        lines = [l for l in inp.split("\n") if l.strip()]
        if len(lines) != 1:
            lines += [""]

        # Create the input dialog
        for i, line in enumerate(lines):
            s = ">>> " if i == 0 else "... "

            if i == len(lines) - 2:
                if line.startswith("return"):
                    line = line[6:].strip()

            res += s + line + "\n"

        self.stdout.seek(0)
        text = self.stdout.read()
        self.stdout.close()
        self.stdout = io.StringIO()

        if text:
            res += text + "\n"

        if not out:
            # No output, return the input statement
            return res, None

        if isinstance(out, discord.Embed):
            # We made an embed? Send that as embed
            res += "<Embed>"
            res = (res, out)

        else:
            # Add the output
            res += str(out)
            res = (res, None)

        return res

    @commands.group(name="ping")
    async def ping(self, ctx):
        """Gets my ping to discord."""
        if ctx.invoked_subcommand is None:
            if not isinstance(ctx.channel, discord.DMChannel):
                t1 = time.perf_counter()
                async with ctx.channel.typing():
                    t2 = time.perf_counter()
                    shard = ctx.guild.shard_id
                    shard_latency = round(self.bot.latencies[int(shard)][1] * 1000)
                    bot_ping = str(round((t2 - t1) * 1000))
                    e = discord.Embed(color=self.bot.color, title="Ping Analyzer v2.0",
                                      description=f"Your server is on shard {shard}\n"
                                                  f"Bot latency: `{bot_ping}ms`\n"
                                                  f"Shard Latency: `{str(shard_latency)}ms`\n"
                                                  f"To view the latency from all shards,"
                                                  f" run the command ``furping all``")
                    e.set_thumbnail(url=avatar_check(self.bot.user))

                    if can_embed(ctx) and can_send(ctx):
                        await ctx.send(embed=e)
                    else:
                        await ctx.send(
                            f"Your server is on shard {shard}\n"
                            f"Bot latency: `{bot_ping:,}ms`\n"
                            f"Shard Latency: `{str(shard_latency):,}ms`")

    @commands.command()
    async def shard(self, ctx):
        """Shard info."""
        await ctx.trigger_typing()
        shard = ctx.message.guild.shard_id
        em = discord.Embed(
            title="Your Server is on shard: ",
            description="{}/{}".format(shard, self.bot.shard_count),
            color=self.bot.color,
        )
        await ctx.channel.send(embed=em)

    @ping.command(name="all", aliases=["shards"])
    async def ping_all(self, ctx):
        """Get all the pings for all shards."""
        await ctx.trigger_typing()
        latencies = self.bot.latencies
        msg = ""
        for shard, ping_t in latencies:
            msg += "**Shard** [{}/{}] = {}ms\n".format(
                shard + 1, len(latencies), round(ping_t * 1000)
            )
        for page in pagify(msg):
            embed = discord.Embed(color=self.bot.color, description=page,
                                  title="Ping Analyzer 2.0")
            embed.set_footer(
                text="Ping, Pong, Ping, Pong, Does it ever end?",
                icon_url=self.bot.footer_emote,
            )
            if can_embed(ctx):
                await ctx.send(embed=embed)
            else:
                await ctx.send(msg)

    # TODO Use less duplication in the code
    # TODO Breakdown the dict and get each value
    # converted to a discord object and then rebuild another dict with their object as the value.
    @commands.command()
    async def credits(self, ctx):
        contributors = {
            "kanin": 173237945149423619,
            "tom": 248294452307689473,
            "callidus": 247745860979392512,
            "waspy": 139800365393510400,
            "iderp": 159074350350336000,
            "cumm": 157986705968726016,
            "talvi": 109682420030128128,
            "ava": 197953896096727041,
            "ryden": 318044130796109825,
            "music2": 154497072148643840,
            "atoro": 83006253919375360,
        }
        contributions = {
            "83006253919375360": "Helped with a lot of issues/problems with sheri"
                                 "and corrected them and rebuilt sheri.bot from scratch again."
        }

    @commands.command(name="getinf")
    async def getinf(self, ctx):
        async with self.bot.pool.acquire() as db:
            guild_info = await db.fetchrow(
                "SELECT * FROM botsettings_guild WHERE id=$1", ctx.guild.id
            )
            await ctx.send(guild_info)

    ####################################################################################################################
    #       Developer Commands
    ####################################################################################################################

    @commands.command(aliases=['update'], hidden=True)
    @commands.check(is_dev)
    async def pull(self, ctx):
        """ Updates the bot from GitHub [pull request]. """
        msg = await ctx.send(
            "<a:lewding:468520251789934612>"
            " Pulling the latest from Github please wait. "
            "<a:lewding:468520251789934612>"
        )
        func = "git pull".replace("`", "").split()

        command_run = subprocess.Popen(
            func, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output = command_run.stdout.read().decode()
        paged = pagify(output)
        for page in paged:
            desc = "```fix\n{0}```".format(page)
            message = (
                    "Update was successful! Here is the output from the update.\n" + desc
            )
            await ctx.send(content=message)

    @commands.command(hidden=True)
    @commands.check(is_owner)
    async def sendfile(self, ctx, user: discord.Member, path: str):
        """Sends a file through haste.ourmainfra.me"""
        url = "https://haste.ourmainfra.me/"
        with open(path, "r") as f:
            data = f.read().encode("utf-8")

        headers = {
            "Accept": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{url}documents", headers=headers, data=data) as resp:
                json = await resp.json()
                await user.send(
                    f"{ctx.author} has told me to send this to you:\n"
                    + url
                    + json["key"]
                )
        await ctx.send("Task completed master~")

    @commands.command(name="debug", hidden=True)
    @commands.check(is_dev)
    async def debug(self, ctx: commands.Context, *, code: str):
        """ Evaluates code. """
        await ctx.trigger_typing()
        code = code.strip("` ")
        python = "```py\n{}\n```"

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "message": ctx.message,
            "guild": ctx.message.guild,
            "channel": ctx.message.channel,
            "author": ctx.message.author,
        }

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(python.format(type(e).__name__ + ": " + str(e)))
            return
        if len(str(result)) >= 1900:
            data = BytesIO(str(result).encode("utf-8"))
            return await ctx.send(
                content=f"The result was a bit too long.. so here is a text file instead 🎁",
                file=discord.File(data, filename=f"Result.txt"),
            )
        await ctx.send(python.format(result))

    @commands.check(is_dev)
    @commands.command(hidden=True, description="Evaluate code in a REPL like environment")
    async def eval(self, ctx, *, code: str):
        """ {"user": ["bot_owner"], "bot": []} """
        code = code.strip("`")
        if code.startswith("py\n"):
            code = "\n".join(code.split("\n")[1:])

        if not re.search(  # Check if it's an expression
                r"^(return|import|for|while|def|class|"
                r"from|exit|[a-zA-Z0-9]+\s*=)",
                code, re.M) and len(code.split("\n")) == 1:
            code = "_ = " + code

        await self._eval(ctx, code)

    @commands.check(is_owner)
    @commands.group(hidden=True)
    async def sql(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    @sql.command(name="execute")
    async def sql_execute(self, ctx, *, query: str):
        query = query.strip("`")
        if query.startswith("sql\n"):
            query = "\n".join(query.split("\n")[1:])

        command = await self.bot.pool.execute(query)
        await ctx.send(f"```py\n{command}```")

    @sql.command(name="fetch")
    async def sql_fetch(self, ctx, *, query: str):
        query = query.strip("`")
        if query.startswith("sql\n"):
            query = "\n".join(query.split("\n")[1:])

        command = await self.bot.pool.fetch(query)
        await ctx.send(f"```py\n{command}```")

    @commands.check(is_dev)
    @commands.group(name="handler", aliases=['h', 'handle'])
    async def handle_mod(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @handle_mod.command(name='l')
    async def handle_load(self, ctx, cog: str):
        """Loads a handler cog"""
        try:
            self.bot.load_extension(f"Handlers.{cog}")
            await ctx.send(f"Successfully reloaded {cog} master!")
        except Exception as e:
            await ctx.send(
                f"I failed to reload {cog} master~\n"
                f"The error I encountered was ``{e}``.\n"
                f"Cause: {e.__cause__}\n"
                f"Context: {e.__context__}\n"
                f"Traceback: {traceback.print_tb(e.__traceback__)}"
            )

    @handle_mod.command(name='u')
    async def handler_unload(self, ctx, cog: str):
        """Unloads a handler cog"""
        try:
            self.bot.unload_extension(f"Handlers.{cog}")
            await ctx.send(f"Successfully unloaded {cog} master!")
        except Exception as e:
            await ctx.send(
                f"I failed to reload {cog} master~\n"
                f"The error I encountered was ``{e}``.\n"
                f"Cause: {e.__cause__}\n"
                f"Context: {e.__context__}\n"
                f"Traceback: {traceback.print_tb(e.__traceback__)}"
            )

    @handle_mod.command(name='r')
    async def handler_reload(self, ctx, cog: str):
        """Reloads a handler cog"""
        try:
            self.bot.reload_extension(f"Handlers.{cog}")
            await ctx.send(f"Successfully reloaded {cog} master!")
        except Exception as e:
            await ctx.send(
                f"I failed to reload {cog} master~\n"
                f"The error I encountered was ``{e}``.\n"
                f"Cause: {e.__cause__}\n"
                f"Context: {e.__context__}\n"
                f"Traceback: {traceback.print_tb(e.__traceback__)}"
            )

    @commands.check(is_dev)
    @commands.group(name='funcr')
    async def function_index(self, ctx):
        if not ctx.invoked_subcommand:
            await commands_help(ctx, ["funcr function", "funcr line", "funcr api"], "furfuncr")

    @function_index.command(name="function")
    async def function_reload(self, ctx, file: str):
        """Reloads a function import"""
        try:
            mod = importlib.import_module(f"Functions.{file}")
            importlib.reload(mod)
            await ctx.send(f"Successfully reloaded {file} master!")
        except Exception as e:
            await ctx.send(
                f"I failed to reload {file} master~\n"
                f"The error I encountered was ``{e}``.\n"
                f"Cause: {e.__cause__}\n"
                f"Context: {e.__context__}\n"
                f"Traceback: {traceback.print_tb(e.__traceback__)}"
            )

    @function_index.command(name="line", aliases=["lines"])
    async def lines_reload(self, ctx, file: str):
        """Reloads a line import"""
        try:
            mod = importlib.import_module(f"Lines.{file}")
            importlib.reload(mod)
            await ctx.send(f"Successfully reloaded {file} master!")
        except Exception as e:
            await ctx.send(
                f"I failed to reload {file} master~\n"
                f"The error I encountered was ``{e}``.\n"
                f"Cause: {e.__cause__}\n"
                f"Context: {e.__context__}\n"
                f"Traceback: {traceback.print_tb(e.__traceback__)}"
            )

    @function_index.command(name="api")
    async def api_reload(self, ctx, file: str):
        """Reloads an api file"""
        try:
            mod = importlib.import_module(f"API.{file}")
            importlib.reload(mod)
            await ctx.send(f"Successfully reloaded {file} master!")
        except Exception as e:
            await ctx.send(
                f"I failed to reload {file} master~\n"
                f"The error I encountered was ``{e}``.\n"
                f"Cause: {e.__cause__}\n"
                f"Context: {e.__context__}\n"
                f"Traceback: {traceback.print_tb(e.__traceback__)}"
            )

    @commands.check(is_dev)
    @commands.group(name="cmd", aliases=['c', 'cm'], hidden=True)
    async def cmd_mod(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @cmd_mod.command(name='l')
    async def command_load(self, ctx, cog: str):
        """Loads a command cog"""
        try:
            self.bot.load_extension(f"Commands.{cog}")
            await ctx.send(f"Successfully loaded {cog} master!")
        except Exception as e:
            await ctx.send(
                f"I failed to reload {cog} master~\n"
                f"The error I encountered was ``{e}``.\n"
                f"Cause: {e.__cause__}\n"
                f"Context: {e.__context__}\n"
                f"Traceback: {traceback.print_tb(e.__traceback__)}"
            )

    @cmd_mod.command(name='u')
    async def command_unload(self, ctx, cog: str):
        """ Unloads a command cog """
        try:
            self.bot.unload_extension(f"Commands.{cog}")
            await ctx.send(f"Successfully unloaded {cog} master!")
        except Exception as e:
            await ctx.send(
                f"I failed to reload {cog} master~\n"
                f"The error I encountered was ``{e}``.\n"
                f"Cause: {e.__cause__}\n"
                f"Context: {e.__context__}\n"
                f"Traceback: {traceback.print_tb(e.__traceback__)}"
            )

    @cmd_mod.command(name='r')
    async def commands_reload(self, ctx, cog: str):
        """ Reloads a command cog """
        extension = f"Commands.{cog}"
        try:
            self.bot.reload_extension(extension)
            await ctx.send(f"Successfully reloaded {cog} master!")
        except Exception as e:
            await ctx.send(
                f"I failed to reload {cog} master~\n"
                f"The error I encountered was ``{e}``.\n"
                f"Cause: {e.__cause__}\n"
                f"Context: {e.__context__}\n"
                f"Traceback: {traceback.print_tb(e.__traceback__)}"
            )

    @commands.group(name='devs')
    async def developers(self, ctx):
        pass

    @developers.command(name='add')
    @commands.check(is_owner)
    async def dev_add(self, ctx, developer: discord.Member):
        await ctx.send(f"Attempting to add {developer.display_name} as a developer...")
        await ctx.pool.execute("UPDATE botsettings_user SET developer=$1 WHERE id=$2",
                               True, developer.id)
        await ctx.send("Completed master :)")

    @developers.command(name="list")
    @commands.check(is_owner)
    async def dev_list(self, ctx):
        await ctx.send("Fetching all the developers.....")
        dev_list = await ctx.pool.fetch("SELECT id FROM botsettings_user WHERE developer='t'")
        developers = ""
        for member in dev_list:
            user = self.bot.get_user(member['id'])
            developers += f"**`{user}`**({user.id})\n"
        await ctx.send(embed=discord.Embed(color=self.bot.color, description=developers))

    @developers.command(name="remove")
    @commands.check(is_owner)
    async def dev_remove(self, ctx, developer: discord.Member):
        await ctx.send(f"Attempting to remove {developer.display_name} as a developer...")
        await ctx.pool.execute("UPDATE botsettings_user SET developer=$1 WHERE id=$2",
                               False, developer.id)
        await ctx.send("Completed master :)")

    @commands.command(name='sync')
    @commands.check(is_dev)
    async def sync_shit(self, ctx):
        vip_members = self.bot.get_guild(self.main_guild).get_role(self.vip_role).members
        developers = self.bot.get_guild(self.main_guild).get_role(self.dev_role).members
        support = self.bot.get_guild(self.main_guild).get_role(self.support_role).members
        for member in vip_members:
            await ctx.pool.execute("UPDATE botsettings_user SET vip=$1 WHERE id=$2", True, member.id)
        for member in developers:
            await ctx.pool.execute("UPDATE botsettings_user SET developer=$1 WHERE id=$2", True, member.id)
        for member in support:
            await ctx.pool.execute(f"UPDATE botsettings_user SET support='t' WHERE id={member.id}")
        await ctx.send("Done?")


def setup(bot):
    bot.add_cog(Core(bot))
