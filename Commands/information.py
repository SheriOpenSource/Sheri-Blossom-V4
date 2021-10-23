import asyncio
import datetime
import os
import platform
import sys
import time

import discord
import distro
import psutil
import speedtest
from discord.ext import commands

from API.ExAPI import External_Retrieval
from Checks.bot_checks import can_send, can_embed, can_external_react, send_message
from Formats.chat_markdown import bold
from Formats.chat_markdown import uptime_status
from Formats.formats import avatar_check
from Functions.core import get_command_stats, get_general_stats
from Lines.custom_emotes import get as Get_emote, CustomEmotes


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _get_level_from_xp(xp):
        remaining_xp = int(xp)
        level = 0
        while remaining_xp >= Information._get_level_xp(level):
            remaining_xp -= Information._get_level_xp(level)
            level += 1
        return level

    @staticmethod
    def _get_level_xp(n):
        return 5 * (n ** 2) + 50 * n + 100

    def convert_to_id_list(self, guild, id):
        output = [staff.id for staff in self.bot.get_guild(guild).get_role(id).members]
        return output

    @commands.command(name="guildcount", aliases=["servercount"])
    async def retrieve_guild_count_and_members(self, ctx):
        users = len([member for member in self.bot.users if not member.bot])
        bots = len([member for member in self.bot.users if member.bot])
        guilds = len(self.bot.guilds)
        embed = discord.Embed(
            color=self.bot.color, title="General Statistics",
            description=f"**{Get_emote['sheri emotes']['commands']}[Commands](https://sheri.bot/commands) "
                        f"{Get_emote['sheri emotes']['api']}[API](https://sheri.bot/api/) "
                        f"{Get_emote['sheri emotes']['link']}[Website](https://sheri.bot/)\n"
                        f"🏥[ Support](https://invite.sheri.bot/) "
                        f"{Get_emote['statuses']['online']}[Status](https://status.sheri.bot/) "
                        f"{Get_emote['sheri emotes']['book']}[Lore](https://status.sheri.bot/)**",
        ).set_thumbnail(url=avatar_check(self.bot.user))
        embed.add_field(
            name="**Statistics**",
            value=f"```diff\n"
                  f"+ Servers: {guilds:,}\n"
                  f"+ Members: {users:,}\n"
                  f"- Bots: {bots:,}```"
        )
        embed.add_field(
            name="**Activity**",
            value=await get_general_stats(ctx, (
                'messages_seen', 'guild_join', 'guild_leave', '@everyones_seen', '@here_seen', 'commands_processed'))
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def staff(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        user_data = await ctx.pool.fetchrow(
            f"SELECT owner, developer, vip, premium, support FROM botsettings_user WHERE id={member.id}"
        )
        
        # Need to make a list for now due to lack of DB access. It ain't clean but it'll work.
        guardian_ids = []
        
        if can_external_react(ctx):
            information_emoji = CustomEmotes.get_emote(False)['sheri customs']['info']
        else:
            information_emoji = 'ℹ'
        if member.id == 139800365393510400:
            embed = discord.Embed(title="My Master~",
                                  description=f"<@139800365393510400> is my creator! He came up with the "
                                              f"idea of making me! ❤",
                                  color=self.bot.color)
            embed.set_thumbnail(url=avatar_check(user=member))
            embed.set_image(url="https://sheri.bot/media/badges/waspybadge.png")
            embed.set_author(name="Staff Checker", icon_url=avatar_check(self.bot.user))
            return await send_message(ctx, message=f"{information_emoji} | {bold(member)} "
                                                   f"is a member of my staff team!",
                                      embed=embed)
        if user_data['owner']:
            embed = discord.Embed(color=self.bot.color, title="My Senior Developer",
                                  description=f"{bold(member)} is one of my lead developers. "
                                              f"They are among the more experienced members of my development team! "
                                              f"You can count on them to fix tricky issues! "
                                              f"Thank you for keeping me running smoothly developer!")
            embed.set_thumbnail(url=avatar_check(user=member))
            embed.set_image(url="https://sheri.bot/media/badges/developerbadge.png")
            embed.set_author(name="Staff Checker", icon_url=avatar_check(self.bot.user))
            return await send_message(ctx, message=f"{information_emoji} | {bold(member)} "
                                                   f"is a member of my staff team!",
                                      embed=embed)
        if user_data['developer']:
            embed = discord.Embed(color=self.bot.color, title="My Developer",
                                  description=f"{bold(member)} is a very important staff member. "
                                              f"They ensure that my features are built well and run smoothly! "
                                              f"Thank you for keeping me running smoothly developer!")
            embed.set_thumbnail(url=avatar_check(user=member))
            embed.set_image(url="https://sheri.bot/media/badges/developerbadge.png")
            embed.set_author(name="Staff Checker", icon_url=avatar_check(self.bot.user))
            return await send_message(ctx, message=f"{information_emoji} | {bold(member)} "
                                                   f"is a member of my staff team!",
                                      embed=embed)
        if user_data['support']:
            embed = discord.Embed(color=self.bot.color, title="Support Agent",
                                  description=f"Run into an issue using me? {bold(member)} is a member of my support "
                                              f"team! They are here to save the "
                                              f"day and answer any questions you may have!")
            embed.set_thumbnail(url=avatar_check(user=member))
            embed.set_image(url="https://sheri.bot/media/badges/supportbadge.png")
            embed.set_author(name="Staff Checker", icon_url=avatar_check(self.bot.user))
            return await send_message(ctx, message=f"{information_emoji} | {bold(member)} "
                                                   f"is a member of my staff team!",
                                      embed=embed)

        if user_data['premium']:
            embed = discord.Embed(color=self.bot.color, title="Donor",
                                  description=f"{bold(member)} has donated to keep me running! Without their support,"
                                              " I wouldn't be online today!")
            embed.set_thumbnail(url=avatar_check(user=member))
            embed.set_image(url="https://sheri.bot/media/badges/premiumbadge.png")
            embed.set_author(name="Staff Checker", icon_url=avatar_check(self.bot.user))
            return await send_message(ctx, message=f"{information_emoji} | {bold(member)} "
                                                   f"is not a member of my staff team.",
                                      embed=embed)
        
        if member.id in guardian_ids:
             embed = discord.Embed(color=self.bot.color, title="API Guardian",
                                   description=f"{bold(member)} is a dedicated guardian of my API! They are "
                                               f"non-staff users who have gone above and beyond to help keep my API "
                                               f"nice and clean by reporting a large amount of unsuitable content. "
                                               f"These people deserve a salute for all their hard work.")
             embed.set_thumbnail(url=avatar_check(user=member))
             embed.set_author(name="Staff Checker", icon_url=avatar_check(self.bot.user))
             return await send_message(ctx, message=f"{information_emoji} | {bold(member)} "
                                                    f"is not a member of my staff team.",
                                                    embed=embed)

        if user_data['vip']:
            embed = discord.Embed(color=self.bot.color, title="VIP",
                                  description=f"{bold(member)} is a VIP to my community!")
            embed.set_thumbnail(url=avatar_check(user=member))
            embed.set_image(url="https://sheri.bot/media/badges/vipbadge.png")
            embed.set_author(name="Staff Checker", icon_url=avatar_check(self.bot.user))
            return await send_message(ctx, message=f"{information_emoji} | {bold(member)} "
                                                   f"is not a member of my staff team.",
                                      embed=embed)
        embed = discord.Embed(color=self.bot.color, title="User",
                              description=f"{bold(member)} is an ordinary user; but users are very important! You"
                                          " make me what i am today. Thank you so much! ❤❤")
        embed.set_thumbnail(url=avatar_check(user=member))
        embed.set_image(url="https://sheri.bot/media/badges/freebadge.png")
        embed.set_author(name="Staff Checker", icon_url=avatar_check(self.bot.user))
        return await send_message(ctx, message=f"{information_emoji} | {bold(member)} "
                                               f"is not a member of my staff team.",
                                  embed=embed)

    @commands.command(aliases=["joinme", "join", "botinvite"])
    async def invite(self, ctx):
        """ Invite me to your server """
        users = len([member for member in self.bot.users if not member.bot])
        guilds = len(self.bot.guilds)
        embed = discord.Embed(
            color=self.bot.color,
            description="**Dashboard: [https://sheri.bot/settings](https://sheri.bot/settings)\n"
                        "Support Server: [https://invite.sheri.bot](https://invite.sheri.bot/)\n"
                        "Commands: [https://sheri.bot/commands](https://sheri.bot/commands)\n"
                        "Bot Invite: [https://bot.sheri.bot](https://bot.sheri.bot/)\n"
                        "Service Status: [https://status.sheri.bot](https://status.sheri.bot)**",
        )
        embed.set_image(url="https://dev.sheri.bot/media/invite_me.png")
        await ctx.send(
            f"Currently serving ``{guilds:,}`` servers and ``{users:,}`` discord members.\n",
            embed=embed,
        )

    @commands.command(name="info")
    async def info(self, ctx):

        embed = discord.Embed(
            color=self.bot.color,
            description=f"**<:discord:452074758964772865> "
                        f"Support Server: [invite.sheri.bot](https://invite.sheri.bot/)\n"
                        f"<:bot:372826993596825602> Bot Invite: [bot.sheri.bot](https://bot.sheri.bot/)\n"
                        f"<:twitter:452074739419185162> "
                        f"Twitter: [@SheriBotOffical](https://twitter.com/SheriBotOffical)\n"
                        "Biography\n"
                        "```fix\n"
                        "According to my lore on https://sheri.bot/lore, I have experienced all "
                        "types of pain and I understand that pain will always hurt, and there is "
                        "nothing you can do about it except push on and become the best you can be "
                        "with what you have. Pain is life's teacher, and with every breath you take,"
                        " you take one step to relieving that pain. I trust my family to always "
                        "help me push on, and become who I was meant to be.```**",
        )
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        misc_info = (
            f"**<:python3:463355015227113473> Python ``{python_version}``\n"
            f"<:discord:452074758964772865> Discord.py ``{discord.__version__}``**"
        )
        embed.add_field(name="Programmed With", value=misc_info, inline=True)
        embed.add_field(
            name="Currently Serving",
            value=f"**Users: ``{len([member for member in self.bot.users if not member.bot]):,}``\n"
                  f"Servers: ``{len(self.bot.guilds):,}``**",
            inline=True,
        )
        embed.add_field(
            name="Statistics",
            value=f"**Uptime: ``{self.get_bot_uptime()}``\n"
                  f"Messages Seen: ``{self.bot.counter['messages_seen']:,}``\n"
                  f"Commands Processed: ``{self.bot.counter['commands_processed']:,}``\n"
                  f"@everyone Seen: ``{self.bot.counter['@everyones_seen']:,}``\n"
                  f"@here Seen: ``{self.bot.counter['@here_seen']:,}``**",
            inline=True,
        )
        embed.set_footer(text="The best furry bot on Discord!")
        await ctx.send(embed=embed)

    @commands.command(aliases=["sys"])
    async def system(self, ctx):
        """Shows Service Information"""
        if can_external_react(ctx):
            loading = "<a:PAW:451853616878452749> Loading system stats..."
            await ctx.send(loading, delete_after=3)
            await asyncio.sleep(3)
            distribution = distro.name(pretty=True)
            embed = discord.Embed(
                color=self.bot.color,
                title="<:pulse:451852158468358145> System Statistics",
                description=f"**System - `{platform.system()}`\n"
                            f"Distribution - `{distribution}`\n"
                            f"Machine - `{platform.machine()}`\n"
                            f"Version - `{platform.version()}`\n"
                            f"Cores - `{os.cpu_count()}`**",
            )
            embed.set_author(name=self.bot.user.name, icon_url=avatar_check(self.bot.user))
            embed.set_thumbnail(url=avatar_check(self.bot.user))
            cpu_percentage = await self.bot.loop.run_in_executor(None, psutil.cpu_percent)
            embed.add_field(name="<:cpu:451852158078287881> **CPU Utilization**",
                            value=f"<:blank:645426904878284802>{cpu_percentage}%")
            memory = await self.bot.loop.run_in_executor(None, psutil.virtual_memory)
            embed.add_field(
                name="<:Ram:451849971201736704> **Memory Usage**",
                value=f"<:blank:645426904878284802>"
                      f"{round(memory.used / 1048576, 2):,}/{round(memory.total / 1048576, 2):,}\n"
                      f"<:blank:645426904878284802> MB ({memory.percent}% Used)",
            )
            stats = await ctx.send(embed=embed)
            s = speedtest.Speedtest()
            best_server = await self.bot.loop.run_in_executor(None, s.get_best_server)
            embed.add_field(
                name="<a:spinnytealpaw:608728799982387200> **Running Internet Speed Test...**",
                value=f"**SpeedTest Server Host: "
                      f"[{best_server['sponsor']}]({best_server['url']})** at ``{best_server['name']}``",
                inline=False)
            await stats.edit(embed=embed)
            embed.remove_field(2)
            dl_speed = await self.bot.loop.run_in_executor(None, s.download)
            ul_speed = await self.bot.loop.run_in_executor(None, s.upload)
            embed.add_field(
                name="<:SheriDown:650710886813794334> **Download Speed**",
                value=f"<:blank:645426904878284802>**`{round(dl_speed / 1048576, 2)}`** MB/S",
                inline=False)
            embed.add_field(
                name="<:SheriUp:650710886800949248> **Upload Speed**",
                value=f"<:blank:645426904878284802>**`{round(ul_speed / 1048576, 2)}`** MB/S",
                inline=False)
            await stats.edit(embed=embed)
        else:
            await ctx.send("This command uses custom emojis to make the command prettier."
                           " Please allow me to use external emojis~")

    @commands.command()
    async def pinfo(self, ctx):
        """dev info"""
        process = psutil.Process()
        cpu_usage = psutil.cpu_percent()
        mem_v = process.memory_percent()
        mem_v_mb = int(process.memory_full_info().uss) / 1024 / 1024
        threads = process.num_threads()
        io_reads = process.io_counters().read_count
        io_writes = process.io_counters().write_count
        t1 = time.perf_counter()
        async with ctx.channel.typing():
            t2 = time.perf_counter()
        msg = "➠ Uptime: **{}** \n➠ Ping : **{}**ms \n➠ Shard count : **{}** \n".format(
            self.get_bot_uptime(brief=True),
            str(round((t2 - t1), 3) * 1000),
            self.bot.shard_count,
        )
        msg += "➠ CPU: **{0:.1f}%**\n➠ Memory: **{1:.0f}MB ({2:.1f}%)**\n➠ " \
               "Threads: **{3}**\n➠ IO:\nTotal reads: **{4}**\nTotal writes: **{5}**\n".format(
                    cpu_usage, mem_v_mb, mem_v, threads, io_reads, io_writes
                )

        em = discord.Embed(color=self.bot.color)
        em.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
        em.add_field(
            name="Process info",
            value=f"**➠ Uptime: ``{self.get_bot_uptime(brief=True)}``\n"
                  f"➠ Ping: ``{str(round((t2 - t1), 3) * 1000)}ms``\n"
                  f"➠ Shard count: ``{self.bot.shard_count}``\n"
                  f"➠ CPU: ``{cpu_usage:.1f}``%\n"
                  f"➠ Memory: ``{mem_v_mb:,.0f} Mb ({mem_v:.1f})%``\n"
                  f"➠ Threads: ``{threads}``\n"
                  f"➠ IO:\n - Total reads: ``{io_reads:,}`` reads\n - Total writes: ``{io_writes:,}`` writes**",
        )
        em.set_footer(text="Requested by {}".format(str(ctx.message.author)))
        await ctx.channel.send(embed=em)

    def get_bot_uptime(self, *, brief=False):
        # Stolen from owner.py - Courtesy of Danny
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                fmt = "{d} days, {h} hours, {m} minutes, and {s} seconds"
            else:
                fmt = "{h} hours, {m} minutes, and {s} seconds"
        else:
            fmt = "{h} H - {m} M - {s} S"
            if days:
                fmt = "{d} D - " + fmt

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    def _size(self, num):
        for unit in ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
            if abs(num) < 1024.0:
                return "{0:.1f}{1}".format(num, unit)
            num /= 1024.0
        return "{0:.1f}{1}".format(num, "YB")

    @staticmethod
    async def current_time():
        time = datetime.datetime.now()
        fmt = "[ %I:%M:%S ] %B, %d %Y"
        return time.strftime(fmt)

    @commands.command(name="metrics")
    async def server_metrics(self, ctx):
        """Shows some general server and member metrics"""
        data = {
            "Bot Members": len([users for users in self.bot.users if users.bot]),
            "Human Members": len([users for users in self.bot.users if not users.bot]),
            "Total Members": len(self.bot.users),
            "Emojis": len(self.bot.emojis),
            "50": len([guild for guild in self.bot.guilds if len(guild.members) >= 50]),
            "300": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 300]
            ),
            "500": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 500]
            ),
            "750": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 750]
            ),
            "1,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 1000]
            ),
            "1,750": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 1750]
            ),
            "2,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 2000]
            ),
            "2,750": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 2750]
            ),
            "3,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 3000]
            ),
            "3,750": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 3750]
            ),
            "4,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 4000]
            ),
            "4,750": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 4750]
            ),
            "5,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 5000]
            ),
            "5,750": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 5750]
            ),
            "6,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 6000]
            ),
            "6,750": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 6750]
            ),
            "7,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 7000]
            ),
            "7,750": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 7750]
            ),
            "8,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) > 8000]
            ),
            "8,750": len(
                [guild for guild in self.bot.guilds if len(guild.members) >= 8750]
            ),
            "9,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) > 9000]
            ),
            "9,750": len(
                [guild for guild in self.bot.guilds if len(guild.members) > 9750]
            ),
            "10,000": len(
                [guild for guild in self.bot.guilds if len(guild.members) > 10000]
            ),
        }
        embed = discord.Embed(
            color=self.bot.color,
            title="Sheri Metrics",
            description="These metrics indicate how many servers have a member count equal "
                        "to or greater than a given threshold.",
        )
        embed.add_field(
            name="Small Servers",
            value=f"**50: `{data['50']:,}`\n"
                  f"300: `{data['300']:,}`\n"
                  f"500: `{data['500']:,}`\n"
                  f"750: `{data['750']:,}`**",
        )
        embed.add_field(
            name="Medium Servers",
            value=f"**1,000: `{data['1,000']:,}`\n"
                  f"1,750: `{data['1,750']:,}`\n"
                  f"2,000: `{data['2,000']:,}`\n"
                  f"2,750: `{data['2,750']:,}`**",
        )
        embed.add_field(
            name="Large Servers",
            value=f"**3,000: `{data['3,000']:,}`\n"
                  f"3,750: `{data['3,750']:,}`\n"
                  f"4,000: `{data['4,000']:,}`\n"
                  f"4,750: `{data['4,750']:,}`\n"
                  f"5,000: `{data['5,000']:,}`**\n",
        )
        embed.add_field(
            name="Super Servers",
            value=f"**5,750: `{data['5,750']:,}`\n"
                  f"6,000: `{data['6,000']:,}`\n"
                  f"6,750: `{data['6,750']:,}`\n"
                  f"7,000: `{data['7,000']:,}`\n"
                  f"7,750: `{data['7,750']:,}`**",
        )
        embed.add_field(
            name="Gigantic Servers",
            value=f"**8,000: `{data['8,000']:,}`\n"
                  f"8,750: `{data['8,750']:,}`\n"
                  f"9,000: `{data['9,000']:,}`\n"
                  f"9,750: `{data['9,750']:,}`\n"
                  f"10,000: `{data['10,000']:,}`**",
        )
        embed.add_field(
            name="Member Metrics",
            value=f"Human Members: **{data['Human Members']:,}**\n"
                  f"Bot Members: **{data['Bot Members']:,}**\n"
                  f"Total Members: **{(data['Total Members']):,}**",
        )
        embed.add_field(name="Misc Metrics", value=f"Emojis: {data['Emojis']:,}")
        embed.set_footer(
            icon_url=self.bot.footer_emote,
            text=await self.current_time()
                 + f" EST - Server Metrics requested by {ctx.author}",
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.group(name='leaderboard', aliases=['lb'])
    async def leaderboard_index(self, ctx):
        pass

    @leaderboard_index.command(name="guild", aliases=['server'])
    async def leaderboard_server(self, ctx):
        emojis = {
            1: "🏆",
            2: ":two:",
            3: ":three:",
            4: ":four:",
            5: ":five:",
            6: ":six:",
            7: ":seven:",
            8: ":eight:",
            9: ":nine:",
            10: "🔟"
        }

        async with self.bot.pool.acquire() as db:
            rows = await db.fetch(
                "SELECT member_id, xp FROM botsettings_guildlevel WHERE guild_id=$1 "
                "ORDER BY xp DESC LIMIT 10",
                ctx.guild.id
            )
            msg = "<:blank:622079028886503455>`Level`: `Xp`: `Mention` `Name`\n"
            index = 0
            for row in rows:
                member = await self.bot.fetch_user(row['member_id'])
                mention = True if member in ctx.guild.members else False
                level = self._get_level_from_xp(row['xp'])
                index += 1
                msg += f"{emojis[index]} `{level:,}` `{row['xp']:,}`:{' ' + member.mention if mention else ''} `[{member}]`\n"
            em = discord.Embed(description=msg, color=self.bot.color)
            em.set_author(name="Leaderboard!")
            em.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=em)

    @commands.command(name='uptime')
    async def uptime(self, ctx):
        """Shows the uptime statistics from uptime robot"""
        payload = "api_key=ur731346-2cee21104475e3156100e7de" \
                  "&monitors=782580493-782805086-783247648-782572191-783565899" \
                  "&all_time_uptime_ratio=1&all_time_uptime_durations=1&response_times=1"
        url = "https://api.uptimerobot.com/v2/getMonitors"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }
        async with self.bot.session.post(url=url, data=payload, headers=headers) as resp:
            content = await resp.json()

        embed = discord.Embed(color=self.bot.color, title="Uptime Robot Statistics",
                              description="For a more graphical view, visit https://status.sheri.bot/")

        for x in content['monitors']:
            embed.add_field(name=f"{uptime_status(x['status'])}**{x['friendly_name']}**",
                            value=f"Uptime ratio: {x['all_time_uptime_ratio']}%", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='stats')
    async def command_stats(self, ctx):
        sfw_social = await get_command_stats(
            ctx, (
                "hug", 'cuddle', 'pounce', 'kiss', 'lick', 'nuzzle', 'pat',
                'boop', 'pickup', 'ship', 'insult', 'kill', 'hold', 'marry'
            )
        )
        generic_info = await get_command_stats(ctx, ('messages_seen', 'commands_processed'))
        animals = await get_command_stats(
            ctx, (
                'husky', 'wolf', 'fox', 'bunny', 'meow', 'panda', 'panda red', 'pig',
                'raccoon', 'woof', 'duck', 'koala', 'birb', 'snep', 'sadcat', 'turkey', 'cat'
            )
        )
        misc_sfw_images = await get_command_stats(
            ctx, ('mur', 'nature', 'neko sfw', 'neko gif', 'neko kitsune', 'e921')
        )
        memes = await get_command_stats(ctx, ('fedora', 'jail', 'dab'))
        embed = discord.Embed(color=ctx.color, title="Command Statistics",
                              description=f"{generic_info}")
        if ctx.channel.is_nsfw():
            nsfw_social = await get_command_stats(
                ctx, (
                    'bang', 'bulge', 'cocksize', 'finger', 'ncuddle', 'nhold', 'nhug', 'seduce',
                    'nkiss', 'nlick', 'npickup', 'smash', 'spank', 'suck', 'tease'
                )
            )
            embed.add_field(name="**NSFW Social commands**",
                            value=f"{nsfw_social}", inline=True)
        embed.add_field(name="**Animal Commands**",
                        value=f"{animals}", inline=True)
        embed.add_field(name="**Social Commands**",
                        value=f"{sfw_social}", inline=True)
        embed.add_field(name="**Meme Commands**", value=memes, inline=True)
        if ctx.channel.is_nsfw():
            misc_nsfw_images = await get_command_stats(
                ctx, (
                    'yiff', 'gif', 'trap', 'snp', 'pussy', 'preg', 'npokemon', 'neko ngif', 'neko nsfw', 'ncomic',
                    'lesbian', 'gay', "e621", 'nsend futa', 'nsend gay', 'nsend lesbian', 'nsend solo', 'nsend yiff',
                    'futa', 'femboy', 'dp', 'dick', 'cuntboy', 'bisexual', "cumflation", 'nsend femboy'
                )
            )
            embed.add_field(name="**Misc NSFW Image Commands**", value=f"{misc_nsfw_images}", inline=True)
        embed.add_field(name="**Misc SFW Image Commands**",
                        value=f"{misc_sfw_images}")
        await ctx.send(embed=embed,
                       content=f"<:information_sheri:648192172629426177> | Here is the statistics {ctx.author}")

    # @commands.command(name='steam')
    # async def steam(self, ctx, user: str):
    #    request = await External_Retrieval.alexflipnote_api(self.bot, f"steam/user/{user}")
    #    embed = discord.Embed(color=embed_color(),
    #                          title=request['profile'['username']])
    #    await send_message(ctx, embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
