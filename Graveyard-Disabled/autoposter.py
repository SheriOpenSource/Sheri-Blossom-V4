import discord
from discord.ext import commands

from Handlers.loops import nsfw_endpoints, sfw_endpoints
from Checks.checks import premium_guild_check

nsfw_endpoint_list = ", ".join(nsfw_endpoints)
sfw_endpoint_list = ", ".join(sfw_endpoints)


class Autoposter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def supported_endpoints():
        all_endpoints = nsfw_endpoints + sfw_endpoints
        supported_noti = (
            f"NSFW Endpoints: {nsfw_endpoint_list}\n\n"
            f"SFW Endpoints: {sfw_endpoint_list}"
        )
        return all_endpoints, supported_noti

    @commands.group(name="autoposter", aliases=["autopost"])
    @commands.check(premium_guild_check)
    async def autoposter_index(self, ctx):
        if ctx.invoked_subcommand is None:
            supported_noti = (
                f"NSFW Endpoints: {nsfw_endpoint_list}\n\n"
                f"SFW Endpoints: {sfw_endpoint_list}"
            )
            embed = discord.Embed(
                color=self.bot.color,
                title="Command Help",
                description="fur**autoposter** - Shows this help file.\n"
                            "fur**autoposter set #channel endpoint** - Set a channel with the designated endpoint\n"
                            "**Example usage**: `furautoposter set #foxes foxes`\n"
                            "fur**autoposter list** -\ Shows configuration..\n"
                            "fur**autoposter enable #channel** -\ enables the autoposter in the channel\n"
                            "fur**autoposter disable #channel** -\ disables the autoposter in the channel",
            )
            embed.add_field(
                name="Supported Endpoints",
                value="```fix\n" f"{supported_noti}\n" f"```",
            )
            await ctx.send(embed=embed)

    @autoposter_index.command(name="set")
    async def autoposter_set(self, ctx, channel: discord.TextChannel, endpoint: str):
        supported_endpoints, supported_notif = self.supported_endpoints()
        if endpoint not in supported_endpoints:
            await ctx.send(
                "The supported values for endpoint are:\n"
                "```fix\n"
                f"{supported_notif}```"
            )
        else:
            async with self.bot.pool.acquire() as db:
                await db.execute(
                    """INSERT INTO botsettings_autoposter (guild_id, channel, endpoint, enabled ) VALUES ($1, $2, $3, $4)""",
                    ctx.guild.id,
                    channel.id,
                    endpoint,
                    True,
                )
            await ctx.send(f"Added {channel.name} with the endpoint {endpoint}.")

    @autoposter_index.command(name="enable")
    async def autoposter_enable(self, ctx, channel: discord.TextChannel):
        async with self.bot.pool.acquire() as db:
            # channels = await db.fetch("SELECT * FROM botsettings_autoposter WHERE guild_id=$1 and enabled=False",
            #                          ctx.guild.id)
            await db.execute(
                "UPDATE botsettings_autoposter SET enabled=True WHERE channel=$1 AND guild_id=$2",
                channel.id,
                ctx.guild.id,
            )
            await ctx.send(f"Set {channel.name} from false to true :)")

    @autoposter_index.command(name="disable")
    async def autoposter_disable(self, ctx, channel: discord.TextChannel):
        async with self.bot.pool.acquire() as db:
            # channels = await db.fetch("SELECT * FROM botsettings_autoposter WHERE guild_id=$1 and enabled=False",
            #                          ctx.guild.id)
            await db.execute(
                "UPDATE botsettings_autoposter SET enabled=False WHERE channel=$1 AND guild_id=$2",
                channel.id,
                ctx.guild.id,
            )
            await ctx.send(f"Set {channel.name} from true to false :)")

    @autoposter_index.command("list")
    async def autoposter_list(self, ctx):
        async with self.bot.pool.acquire() as db:
            channels = await db.fetch(
                "SELECT * FROM botsettings_autoposter WHERE guild_id=$1", ctx.guild.id
            )
            channel_list = ""
            for channel in channels:
                chan = self.bot.get_channel(channel["channel"])
                channel_list += (
                    f"Channel: {chan.name}\n"
                    f"Enabled: {channel['enabled']}\n"
                    f"Endpoint: {channel['endpoint']}\n\n"
                )
            await ctx.send(channel_list)

'''
    @tasks.loop(minutes=10)
    async def auto_poster(self):
        try:
            # Begin the loop
            # Define the postgres pool
            async with self.bot.pool.acquire() as db:
                # grab all the channels where enabled is true
                channels = await db.fetch(
                    "SELECT * FROM botsettings_autoposter WHERE enabled=True"
                )
                # Count the channels
                chan_amount = len(channels)
                # Display the amount of channels in console
                self.bot.log.info(
                    f"[Auto Poster][Start][Channels: {chan_amount}] - 10 minutes is up, time to spam :D"
                )
                # Begin going through each channel
                times_posted = 1
                for channel in channels:

                    try:
                        guild_db = await db.fetchrow(
                            "select premium, premium_owner_id from botsettings_guild where id=$1",
                            channel['guild_id'])
                        api = await Retrieval.main_api(self.bot, channel["endpoint"])
                        try:
                            url = api["url"]
                        except KeyError:
                            return
                        else:
                            pass

                        try:
                            report = api["report_url"]
                        except KeyError:
                            return
                        else:
                            pass

                        # Build the embed
                        embed = discord.Embed(color=self.bot.color,
                                              description=f"**Image not loading? [Click Me]({url})\n"
                                                          f"Something Wrong? [Report it]({report})**", ).set_image(
                            url=api["url"])
                        # IF the guild is premium server, then post
                        if guild_db[0]:
                            # get the guild
                            guild = self.bot.get_guild(id=channel["guild_id"])
                            # Check to see if the endpoint is NSFW or not.
                            if channel["endpoint"] in nsfw_endpoints:
                                chan = guild.get_channel(channel["channel"])
                                # Ensure the channel stays nsfw and if it isn't nsfw, change it
                                if chan.is_nsfw():
                                    # Send the embed
                                    await chan.send(embed=embed)
                                    self.bot.log.info(
                                        f"[Auto Poster][Times: {times_posted}] Posted an NSFW {channel['endpoint']} in "
                                        f"[{guild.name}](#{chan.name})"
                                    )
                                    times_posted += 1
                                else:
                                    try:
                                        # Make channel nsfw
                                        await chan.edit(
                                            nsfw=True,
                                            reason="[ Auto Poster ] Endpoint is NSFW",
                                        )
                                    # Seriously, someone needs to create a book called discord permissions for dummies.
                                    except discord.Forbidden:
                                        self.bot.log.info(
                                            "[ Auto Poster] - Lol, Someone doesn't know how to discord.
                                             Time to bug the shit outta them."
                                        )
                                        primer = self.bot.get_user(guild_db[1])
                                        if primer.id == 139800365393510400:
                                            pass
                                        if primer in guild.members:
                                            # Log there was an permission error in console
                                            # and attempt to send it to the primer and guild owner
                                            self.bot.log.info(
                                                "[ Auto Poster] - Lol, Someone doesn't know how to discord.
                                                 Time to bug the shit outta them."
                                            )
                                            # Get the primer user
                                            primer = self.bot.get_user(guild_db[1])
                                            # Send the message in dm
                                        try:
                                            await primer.send(
                                                f"Hey, Just informing you that {chan.mention} is configured with an NSFW
                                                 endpoint and I can not make the channel NSFW. "
                                                f"Please fix this!"
                                            )

                                            await guild.owner.send(
                                                f"Hey, Just informing you that {chan.mention} is configured with an NSFW
                                                 endpoint and I can not make the channel NSFW. "
                                                f"Please fix this!"
                                            )
                                            # Why do you have to block a bot?
                                        except discord.Forbidden:
                                            pass

                            if channel["endpoint"] in sfw_endpoints:
                                chan = guild.get_channel(channel["channel"])
                                await chan.send(embed=embed)
                                self.bot.log.info(
                                    f"[Auto Poster][Times: {times_posted}] Posted an SFW {channel['endpoint']} in "
                                    f"[{guild.name}](#{chan.name})"
                                )
                                times_posted += 1

                    except (discord.Forbidden, discord.NotFound, AttributeError):
                        await self.bot.pool.execute("UPDATE botsettings_autoposter SET enabled='f' WHERE channel=$1",
                                                    channel['channel'])
                        continue

                await self.bot.get_guild(346892627108560901).get_channel(651774871763812392).send(f"I have completed "
                                                                                                  f"auto posting on "
                                                                                                  f"date logic. "
                                                                                                  f"Total images "
                                                                                                  f"posted: "
                                                                                                  f"{times_posted}")
                await self.bot.log.info('[Auto Poster][End] - Waiting 10 minutes before starting again')

        except Exception as e:
            self.bot.log.info(f"[Auto Poster] An error has occurred. {e}")
            self.bot.sentry.capture_exception(e)
        # hastag discord permissions for dummies pls
        except discord.Forbidden:
            # Log there was an permission error in console
            # and attempt to send it to the primer and guild owner
            self.bot.log.info(
                "[ Auto Poster] - Lol, Someone doesn't know how to discord. Time to bug the shit outta them."
            )
            primer = self.bot.get_user(guild_db[1])
            self.bot.log.info(
                "[ Auto Poster] - Lol, Someone doesn't know how to discord. Time to bug the shit outta them."
            )
            try:
                await primer.send(
                    f"Hey, Just informing you that {chan.mention} is configured for auto posting but I am unable to send messages/embed messages there! "
                    f"Please fix this!"
                )
                await guild.owner.send(
                    f"Hey, Just informing you that {chan.mention} is configured for auto posting but I am unable to send messages/embed messages there! "
                    f"Please fix this!"
                )
            # Why would you block a bot?
            except discord.Forbidden:
                pass
    '''

def setup(bot):
    bot.add_cog(Autoposter(bot))
