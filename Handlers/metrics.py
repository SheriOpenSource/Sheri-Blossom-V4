from discord.ext import commands
from aiohttp import web


BLACKLISTED_EVENTS = ["presence_update"]


class Metrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.app = web.Application(loop=bot.loop)
        self.app.add_routes([web.get("/metrics", self.get_metrics_route)])

        # For cleanup
        self._runner = None

        self.bot.loop.create_task(self.start_app())

        self.events = {}
        self.command_usage = {}

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        if msg.get("op") != 0:
            # Not a dispatch (might be useful to track heartbeats, reconnects, invalid sessions etc. tho)
            return

        event = msg.get("t", "none").lower()
        if event not in BLACKLISTED_EVENTS:
            if event not in self.events.keys():
                self.events[event] = 1
            else:
                self.events[event] += 1

    @commands.Cog.listener()
    async def on_command(self, ctx):
        commands = await ctx.pool.fetch("select * from botsettings_commandcount")
        for command in commands:
            self.command_usage[command["command"].replace(" ", "_")] = command["usage_count"]

    async def get_metrics_route(self, request):
        lines = []

        for event, count in self.events.items():
            lines.append(f"event_counts,bot=sheri,type={event} count={count}i")

        for command, usage in self.command_usage.items():
            lines.append(f"commands_ran,bot=sheri,command={command} count={usage}i")

        lines.append(f"guild_count,bot=sheri count={len(self.bot.guilds)}i")

        return web.Response(text="\n".join(lines))

    def cog_unload(self):
        self.bot.loop.create_task(self.stop_app())

    async def start_app(self):
        self._runner = runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8081)
        await site.start()

    async def stop_app(self):
        if self._runner:
            await self._runner.cleanup()
            self._runner = None


def setup(bot):
    bot.add_cog(Metrics(bot))
