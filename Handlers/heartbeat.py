from discord.ext import tasks, commands
import aiohttp

heartbeat_url = "https://heartbeat.uptimerobot.com/m783565899-758277c12b36c419f6d7f4875143b3d67db4ff00"


class Heartbeat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.heartbeat.start()

    def cog_unload(self):
        self.heartbeat.stop()

    @tasks.loop(minutes=1)
    async def heartbeat(self):
        try:
            self.bot.log.info("[UptimeRobot HeartBeat] - Sending heartbeat Request")
            req = await self.bot.session.get(heartbeat_url)
            try:
                response = await req.json()
            except aiohttp.ContentTypeError:
                return
            
            self.bot.log.info(
                f"[UptimeRobot Heartbeat] - UptimeRobot says: {response['msg']}"
            )
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @heartbeat.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Heartbeat(bot))
