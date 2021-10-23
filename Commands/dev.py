import os
import urllib
import discord
import ujson
from dateutil.relativedelta import *
from discord.ext import commands
from API.API import Retrieval as Sheri_Get
from Checks.checks import is_dev as authorized
from Formats.formats import avatar_check
from Handlers.loops import nsfw_endpoints, sfw_endpoints

nsfw_endpoint_list = ", ".join(nsfw_endpoints)
sfw_endpoint_list = ", ".join(sfw_endpoints)


def cooldown(time1, time2):
    delta = relativedelta(time1, time2)
    return delta


class The_Core():
    def __init__(self):
        self.cmd = []
        self.count = []
        self.last = None


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cmd = {}

    def get_cmdlist(self):
        if 1 in self.cmd:
            return self.cmd[1]
        else:
            self.cmd[1] = The_Core()
            return self.cmd[1]

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        core = self.get_cmdlist()
        ban_cmd = ["reload", "load", "unload", "update", "cmdlist"]

        if ctx.valid:
            if not str(ctx.command) in core.cmd:
                if str(ctx.command) not in ban_cmd:
                    core.cmd.append(str(ctx.command))
                    core.count.append(1)
                    core.last = str(ctx.command)
            else:
                if str(ctx.command) not in ban_cmd:
                    dex = core.cmd.index(f"{str(ctx.command)}")
                    core.count[dex] += 1
                    core.last = str(ctx.command)

    @staticmethod
    async def manage_mention_role(ctx, action):
        mention_role = discord.utils.get(ctx.guild.roles, id=483762828562530304)
        if action:
            await mention_role.edit(mentionable=True, reason="Announcement")
            members = len(
                [
                    member
                    for member in mention_role.members and ctx.channel.members
                    if not member.bot
                ]
            )
            return members
        else:
            await mention_role.edit(mentionable=False, reason="Announcement Completed")

    # for the sake of repeating code, i will build the initial embed in a function and extend from there.
    def build_announcement_embed(self, ctx, description: str):
        embed = discord.Embed(color=self.bot.color, description=description).set_author(
            name=ctx.author, icon_url=avatar_check(ctx.author)
        )
        embed.set_thumbnail(url=avatar_check(self.bot.user))
        return embed

    @commands.command(name="cmdlist")
    # @commands.check(authorized)
    async def cmd_list(self, ctx):
        core = self.get_cmdlist()
        cmds = core.cmd
        count = core.count
        i = 0
        z = 0
        count, cmds = (list(t) for t in zip(*sorted(zip(count, cmds), reverse=True)))

        most_used_cmds = cmds[0]
        uses = count[0]

        cmd_list = ""

        for x in cmds:
            if len(cmds) < 20:
                cmd_list += f"[{x}]"
                cmd_list += f"[{count[i]}]\n"
                z += 1
            else:
                threshold = count[i]
                if threshold >= 15:
                    z += 1
                    cmd_list += f"[{x}]"
                    cmd_list += f"[{count[i]:,}]\n"
                if z > 25:
                    break
            i += 1

        post = discord.Embed()
        post.title = "Sheri Live Commands Counts:"
        post.description = f"Most Used: {most_used_cmds}({uses:,})\nLast Cmd Ran: {core.last}"
        post.add_field(name=f"The Top {z}", value=f"```md\n{cmd_list}```")

        await ctx.send(embed=post)

    @commands.group(name="announce")
    @commands.check(authorized)
    async def announce_index(self, ctx):
        if not ctx.invoked_subcommand:
            return await ctx.send("Improve your spelling.")

    @announce_index.command(name="update")
    async def announce_update(self, ctx, *, message: str = None):
        announce_channel = self.bot.get_channel(631740774156861440)
        sheri_members = len([member for member in self.bot.users if not member.bot])
        emotes = [
            ":Sheri_thumpup:604843094869016586",
            ":Sheri_thumpdown:604843094583541774",
            ":SheriLove:592375692956663808",
            ":WaspyLove:592369937062821901",
        ]
        msg = await ctx.send(
            "Attempting to make mention role mentionable for announcement and sending announcement..."
        )

        # Make mention role mentionable and get the total members that will be mentioned.
        members = await self.manage_mention_role(ctx, True)

        # Build the announcement embed
        embed = self.build_announcement_embed(ctx, message)
        embed.set_footer(text="Click or tap below if you like/dislike the update.")
        embed.add_field(name="Members Mentioned", value=f"``{members:,}`` members!")
        embed.add_field(
            name="Sheri Statistics",
            value=f"Server count ``{len(self.bot.guilds):,}``\n"
                  f"Member Count ``{sheri_members:,}``",
        )
        announcement = await announce_channel.send(
            embed=embed,
            content="<@&483762828562530304>, A new update has been posted. Read below!",
        )
        await self.manage_mention_role(ctx, False)
        await msg.edit(content="Announcement posted!")
        for x in emotes:
            await announcement.add_reaction(x)

    @commands.command()
    @commands.check(authorized)
    async def walkie(self, ctx, *, coggie: str):
        if coggie.lower() == "list":
            post = "List of Command Cogs:\n"
            for extension in os.listdir("Commands"):
                if extension.endswith(".py"):
                    post += f"{extension}\n"

            await ctx.send(post)
        else:
            cog = self.bot.get_cog(coggie)

            if cog is None:
                await ctx.send("Invalid Cog")
            else:
                post = ""

                for apple in cog.walk_commands():
                    post += str(apple)
                    post += "\n"

                await ctx.send(post)

    @commands.command()
    async def cmdinfo(self, ctx, *, cmd: str):
        the_cmd = self.bot.get_command(cmd)

        if the_cmd is None:
            await ctx.send("No command found")
        else:
            cmd_stat = self.get_cmdlist()

            aliases = the_cmd.aliases
            name = the_cmd.name
            cog = the_cmd.cog_name
            the_args = the_cmd.clean_params
            the_checks = the_cmd.checks
            # the_defaults = the_cmd.__defaults__
            post = f"{name} info:\n" f"Aliases: {aliases}\n" f"Cog: {cog}\n\n"
            post += f"Args&Variables: {dict(the_args)}\n\n"
            post += f"Checks Req: {the_checks}"
            if cmd in cmd_stat.cmd:
                dex = cmd_stat.cmd.index(cmd)
                times = cmd_stat.count[dex]

                post += f"\n**Used: `{times}` times.**"

            await ctx.send(post)

    @commands.command(name="resetdaily")
    @commands.check(authorized)
    async def reset_daily(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        async with ctx.bot.pool.acquire() as db:
            await db.execute("UPDATE botsettings_user SET next_daily=$1 WHERE id=$2",
                             None, user.id)

        await ctx.send("Daily cooldown successfully reset!")

    async def create_welcome_image(
            self, author, guild, count, color: int, background: str, fmt: int
    ):
        member, avatar = author, avatar_check(author)
        guild_name, color = (
            urllib.parse.quote(str(guild.name)),
            hex(color).split("x")[-1],
        )
        url = (
            f"https://ourmainfra.me/api/v2/welcomer/?avatar={avatar}&user_name={member}"
            f"&guild_name={guild_name}&member_count={count}&color={color}"
        )
        if background and background != "Transparent":
            url += f"&background={background}"
        if fmt:
            url += f"&type={fmt}"
        headers = {"Authorization": os.environ["MAINFRAME_API_KEY"]}
        async with self.bot.session.get(url, headers=headers) as resp:
            if resp.status == 200:
                image = await resp.read()
                with open("welcome.png", "wb") as f:
                    f.write(image)
                    file = discord.File("welcome.png")
                    img = "attachment://welcome.png"
                    return file, img
            else:
                error = await resp.json()
                return print(error)

    @commands.command()
    @commands.check(authorized)
    async def rules(self, ctx):
        beginning = "We are NOT responsible for what actions you do on this platform.\n " \
                    "This includes, breaking Discord's TOS.\n" \
                    "If you have any questions or concerns, please contact a staff member.\n" \
                    "You **WILL** follow the guidelines discord has set.\n - " \
                    "Failure to follow discord's community guidelines will result in a instant report of the incident" \
                    "to discord's Trust and Safety team.\n" \
                    "<https://discordapp.com/terms>\n" \
                    "<https://discordapp.com/guidelines>\n**"

        general = "**Be wholesome and use common sense!**\n" \
                  " - Treat others with kindness and respect. Harassment will not be tolerated in our server!\n" \
                  "**Do not spam or shitpost outside of meme or image channels!**\n" \
                  " - Please just keep things in their respective channels such as. Spam in spam & Memes in memes.\n" \
                  "**No hate speech/imagery (racism, sexism, etc.) at all.**\n" \
                  " - This also extends to using hate imagery as your PFP as well (for example, the Nazi logo)." \
                  " Slurs (such as the hard er word) are also INSTANT bannable offenses, so don't use them.\n" \
                  "**Keep conversations relevant to the channel!**\n - " \
                  "If the conversation drifts too far from the channel's purpose, " \
                  "please move it to the appropriate channel!" \
                  " Messages and images should be kept applicable to the given topic or channel." \
                  "**The usage of self-bots, alternate accounts & overall, anything " \
                  "that causes API abuse are a ban offense.**\n" \
                  " - Includes OTHER programs as well that have access to perform" \
                  " actions via the API of any kind are forbidden on this server!"

        nsfw = "Do not solicit, pester, or harass anyone who posts in " \
               "<#492504749468418068> or <#492503815107641364> for " \
               "content on the server or in DMs.\n" \
               " We take the comfortability of our members very seriously, and there will be no tolerance " \
               "of any harmful behavior.\n" \
               "Infractions are as follows:\n" \
               "First infraction: A warning will be issued.\n" \
               "Second infraction: Removal of access to th@e above channels.\n" \
               "Third infraction: A permanent ban will be issued.\n" \
               "Please notify staff of any concerning behavior.We want to ensure the server remains " \
               "a friendly and welcoming place for everyone.\n" \
               "**Keep NSFW content outside of sfw channels.**\n" \
               "-| If you have to ask, “Is this NSFW?”, then it probably is (depending, on the content.)",
        support = "**Keep all non-support conversations OUTSIDE of the support channels**"

        staff = "**Admin and Moderators have the final verdict rules!**\n" \
                "-| Mutes, Kicks, and Bans are entirely up to staff discretion. " \
                "Arguing with staff is probably a waste of " \
                "your time. We reserve the right to ban for anything we forgot to list here.\n" \
                "-| (Staff also reserve the right to investigate you for any suspicion of being underage.)\n" \
                "**Do not ask for a position!**\n" \
                "-| Positions are earned here. Asking for one will result in a low chance " \
                "of getting it and you even might getting kicked",

        partners = "**Partnership Requirements**\n" \
                   "-| 250 Members excluding bots.\n" \
                   "-| Have Sheri in your server.\n" \
                   "-| NSFW locked behind a verification system, can be locked with Sheri.\n" \
                   "-| Active Community.\n" \
                   "-| Decently Moderated Server - Staff that can actually keep the servers clean.\n" \
                   "-| Exceptions can be made through @Waspyeh#0615 but nobody else.\n" \
                   "**No advertising! Do not link invites to other servers, or shill your server.**\n" \
                   "-|If you are caught doing this, you will be punished!.",

        await ctx.send(beginning)
        await ctx.send(general)
        await ctx.send(nsfw)
        await ctx.send(support)
        await ctx.send(partners)
        await ctx.send(staff)

    @commands.command(name="error")
    async def com_error(self, ctx):
        raise discord.Forbidden

    @commands.command(description="List all modules on the bot")
    async def modules(self, ctx):
        cog_list, cogs_loaded, cogs_unloaded = [], "```diff\n+\t", ""
        event_list, events_loaded, events_unloaded = [], "```diff\n+\t", ""
        cogs, events = [], []
        bot_cogs = {}
        em = discord.Embed(color=self.bot.color)
        em.set_author(name="Bot modules:")
        em.set_thumbnail(url=self.bot.user.avatar_url)
        paths = ["Commands", "Handlers"]
        for path in paths:
            for file in os.listdir(path):
                if not file.endswith(".py"):
                    pass
                else:
                    if path == paths[0]:
                        cog_list.append(file[:-3])
                    else:
                        event_list.append(file[:-3])
        for name, obj in self.bot.cogs.items():
            if "Commands" in str(obj):
                cogs.append(name)
            else:
                events.append(name)
        bot_cogs["cogs"] = cogs
        bot_cogs["events"] = events
        for k, v in bot_cogs.items():
            if k == "cogs":
                for cog in v:
                    if cog.lower() in cog_list:
                        cog_list.remove(cog.lower())
            else:
                for event in v:
                    if event.lower() in event_list:
                        event_list.remove(event.lower())

        cogs_loaded += ", ".join(bot_cogs["cogs"])
        cogs_unloaded += ", ".join(cog_list)
        events_loaded += ", ".join(bot_cogs["events"])
        events_unloaded += ", ".join(event_list)
        cogs_loaded += f"\n-\t{cogs_unloaded}```" if cogs_unloaded else "```"
        events_loaded += f"\n-\t{events_unloaded}```" if events_unloaded else "```"
        em.add_field(name="Cogs:", value=cogs_loaded)
        em.add_field(name="Events:", value=events_loaded)

        await ctx.send(embed=em)

    @commands.command(name="say", pass_context=True)
    @commands.check(authorized)
    async def say(self, ctx, *, msg: commands.clean_content):
        await ctx.message.delete()
        await ctx.send(msg)

    async def send_embed(self, ctx, img):
        embed = discord.Embed(
            color=self.bot.color,
            description=f"Image not loading? [Image Link]({img['url']})\n"
                        f"Something wrong with the image? Report it [here]({img['report_url']})")
        embed.set_image(url=img['url'])
        embed.set_footer(text=f"Image sent by {ctx.author.name}")

    async def send_multiple_dm(self, ctx, endpoint, know: str, *users: discord.Member):
        if len(users) >= 3:
            user_names = []
            for user in users:
                user_names.append(user.name)
            user_names = ", ".join(user_names)
        else:
            return await ctx.send("You can only send up to 3 users.")
        msg = await ctx.send(f"Attempting to send {know} to **{user_names}**...")
        home = self.bot.get_guild(346892627108560901)
        check_mark = discord.utils.get(home.emojis, name="mhm")
        error_mark = discord.utils.get(home.emojis, name="error")
        if endpoint in sfw_endpoints:
            results = []
            for user in users:
                img = await Sheri_Get.main_api(self.bot, endpoint)
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"Image not loading? [Image Link]({img['url']})\n"
                                f"Something wrong with the image? Report it [here]({img['report_url']})")
                embed.set_image(url=img['url'])
                embed.set_footer(text=f"Image sent by {ctx.author.name}")
                try:
                    await user.send(embed=embed)
                    results.append(f"{check_mark} {user.name}")
                except discord.Forbidden:
                    results.append(f"{error_mark} {user.name}")
            await msg.edit(content=f"{ctx.author.name}, I have sent {know} to {', '.join(results)}.\n"
                                   f"{check_mark} Success {error_mark} Error")

    async def send_dm(self, ctx, endpoint, know: str, user):
        home = self.bot.get_guild(346892627108560901)
        check_mark = discord.utils.get(home.emojis, name="mhm")
        error_mark = discord.utils.get(home.emojis, name="error")
        img = await Sheri_Get.main_api(self.bot, endpoint)
        img_embed = discord.Embed(
            color=self.bot.color,
            description=f"Image not loading? [Image Link]({img['url']})\n"
                        f"Something wrong with the image? Report it [here]({img['report_url']})")
        img_embed.set_image(url=img['url'])
        img_embed.set_footer(text=f"Image sent by {ctx.author.name}")
        emojis = [check_mark, error_mark]
        if endpoint in nsfw_endpoints:
            def check(m):
                return (m.channel == ctx.author.dm_channel and
                        m.author == ctx.author)

    @commands.command(name="twitch")
    async def twitch_testing(self, ctx):
        from Handlers.presence import twitch
        twitch_req = await ctx.bot.session.get(twitch['stream url'], headers=twitch['headers'])
        response = await twitch_req.json()
        if response['data']:
            await ctx.send(response['data'][0]['viewer_count'])
        else:
            await ctx.send("False")

    @commands.command(name='test')
    async def testing(self, ctx):
        await ctx.send("Lol test")

    @staticmethod
    async def load_registration_roles(ctx):
        guild_data = await ctx.pool.fetchrow(
            'select registration_roles from botsettings_guild where id=$1',
            ctx.guild.id)
        guild_data_roles = ujson.loads(guild_data['registration_roles'])
        # Roles has not been added :V
        if guild_data_roles == {}:
            await Dev.add_registration_roles(ctx)
            return Dev.load_registration_roles(ctx)
        reg_roles = {}
        for rolename, roleid in guild_data_roles.items():
            guild_role = ctx.guild.get_role(roleid)
            if guild_role is None:
                return await ctx.send("There has been an error in retrieving roles. Did you delete one of them? "
                                      "Contact support at https://discord.gg/sheri to get this resolved.")
            reg_roles[rolename] = guild_role
        return reg_roles

    @staticmethod
    async def add_registration_roles(ctx):
        guild_data = await ctx.pool.fetchrow(
            f"select registration_nsfw from botsettings_guild where id={ctx.guild.id}")
        role_dict = dict()
        guild_roles = ctx.guild.roles
        if guild_data['registration_nsfw']:
            roles = nsfw_sfw_roles
        else:
            roles = sfw_roles
        for role in roles:
            for guild_role in guild_roles:
                if guild_role.name == role:
                    role_dict[role] = guild_role.id
        await ctx.pool.execute(f"update botsettings_guild set registration_roles=$1 where id=$2",
                               ujson.dumps(role_dict), ctx.guild.id)

    @staticmethod
    async def registration_output(ctx):
        reg_output = await ctx.pool.fetchval('select registration_output from botsettings_guild where id=$1',
                                             ctx.guild.id)
        try:
            channel = ctx.guild.get_channel(reg_output)
            if channel is None:
                await ctx.send("The channel you selected for registration output is non existent")
                return None
            else:
                return channel
        except discord.NotFound:
            await ctx.send("The channel you selected for registration output is non existent")
            return None


def setup(bot):
    bot.add_cog(Dev(bot))
