import discord
from discord.ext import commands

from Checks import checks
from Checks.bot_checks import can_embed, can_send
from Checks.checks import premium_guild_check
from Database.custom_prefix import Prefixes
from Formats.formats import RoleID, avatar_check, icon_check, RoleID_member
from Formats.text import parse_level_vars
from Functions import errors
from Functions.core import commands_help
from Handlers.loops import nsfw_endpoints, sfw_endpoints

nsfw_endpoint_list = ", ".join(nsfw_endpoints)
sfw_endpoint_list = ", ".join(sfw_endpoints)
help_text = (
    "To start using self roles with me, you must ensure that I have the following permissions:\n"
    "`Manage Roles`, `Embed Links`, and `Send Messages`. "
    "As is the case with any bot assigning and unassigning roles, I need to be able "
    "to reach those roles, so please make "
    "sure I can do that by placing my role (or any other role you've assigned to me) "
    "above the roles you wish to make self-assignable."
)
help_text_2 = (
    "Self roles (also called 'self-assignable roles') are roles you set with me which "
    "members can then self assign by using the "
    "commands ``furiam`` or ``furiamnot``. I'll also list all of the commands relating "
    "to self-assignable roles for you below."
)

help_commands = (
    "fur**selfroles|sr list** : List's the available roles configured by guild(server) admin\n"
    "fur**selfroles|sr add roleName** : `[Requires 'Manage Roles']` Add a role to the self role configuration\n"
    "fur**selfroles|sr delete roleName** : `[Requires 'Manage Roles']` "
    "Deletes a role from the self role configuration\n"
    "fur**iam|grant roleName**`[see above]` : Gives the caller the role specified if on configuration or list\n"
    "fur**iamnot|revoke roleName** `[see above]` : Removes the role specified from the caller.\n"
    "\n"
    "*Please note that `roleName` is only a placeholder and is meant to be "
    "__replaced by the name of whatever role you're working with!__*"
)

bad_argument_text = (
    "Uh oh, I can't find that role! Are you sure you spelled it correctly?\n"
    "Remember that capitalization matters! `CoolRoleName` isn't the same as `coolrolename`!"
)


class Guild_settings(commands.Cog):
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

    @commands.guild_only()
    @commands.group(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Passed in Setup")

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @setup.command(name="muterole")
    async def setup_mute(self, ctx):
        async with self.bot.pool.acquire() as db:
            mute_role_id = await db.fetchval(
                "SELECT mute_role FROM botsettings_guild WHERE id=$1", ctx.guild.id
            )
            if not mute_role_id:
                return await ctx.send(
                    "Looks like this server doesn't have a mute role set. "
                    "No worries; it's an easy fix! Head to <https://sheri.bot/settings>, select this server, "
                    "go into the `Moderation` tab, select a mute role, then run this command again."
                )
        mute_role = ctx.guild.get_role(mute_role_id)
        has_errors = False
        await ctx.send("Attempting to automaticly setup the mute role.")
        for channel in ctx.guild.channels:
            try:
                if channel.type == discord.ChannelType.text:
                    await channel.set_permissions(mute_role, send_messages=False)
                elif channel.type == discord.ChannelType.voice:
                    await channel.set_permissions(mute_role, speak=False)
            except Exception as e:
                await ctx.send(
                    f"Could not set permissions for {mute_role} in {channel}:\n{e}"
                )
                has_errors = True
        message = (
            f"Done! I have set the correct permissions for {mute_role} in all channels"
        )
        if has_errors:
            message += " except those with errors I've mentioned above. Enjoy!"
        await ctx.send(message)

    ####################################################################################################################
    #                               Prefix Commands
    ####################################################################################################################

    @commands.guild_only()
    @checks.admin()
    @commands.group(description="Prefix management", invoke_without_command=True)
    async def prefix(self, ctx):
        if not ctx.invoked_subcommand:
            prefixes = await Prefixes(ctx).list()
            if can_embed(ctx):
                embed = discord.Embed(
                    color=self.bot.color,
                    title="Custom Prefixes",
                    description=prefixes
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(
                    f"The available prefixes are:\n" f"{prefixes}"
                )

    @prefix.command(name='add')
    async def prefix_add(self, ctx, prefix: str):
        try:
            await Prefixes(ctx, prefix).add()
        except errors.PrefixTooLong:
            return await ctx.send_error(
                "That prefix is too long! Prefixes must be no more than 10 characters in length. "
                "Anything longer than that is just plain silly~!"
            )
        except errors.TooManyPrefixes:
            return await ctx.send_error(
                "Huh? It looks like this guild already has 10 custom prefixes. "
                "Why do you need so many? Remove some before adding more."
            )
        except errors.DuplicatePrefix:
            return await ctx.send_error(
                "This prefix already exists here or is one of my default prefixes!"
            )
        await ctx.send(
            embed=discord.Embed(
                color=self.bot.color,
                description=f"Understood. I'll start listening for `{prefix}`! "
                            f"Including that prefix, here's how you can summon me:\n{await Prefixes(ctx).list()}"
            ).set_author(name=f"Prefix added in {ctx.guild.name}")
        )

    @prefix.command(name='remove')
    async def prefix_remove(self, ctx, prefix: str):
        try:
            await Prefixes(ctx, prefix).remove()
        except errors.PrefixNotFound:
            await ctx.send("I can't find that prefix! Double check that you've entered it correctly and try again.")
        await ctx.send(
            embed=discord.Embed(
                color=self.bot.color,
                description=f"Got it! I won't listen for `{prefix}` anymore. "
                            f"You can still use these prefixes to get my attention:\n{await Prefixes(ctx).list()}"
            ).set_author(name=f"Prefix removed in {ctx.guild.name}")
        )

    ####################################################################################################################
    #                               Level Config Commands
    ####################################################################################################################

    @commands.guild_only()
    @commands.group(name="lvlset", aliases=["levelset"])
    async def level_settings(self, ctx):
        if ctx.invoked_subcommand is None:
            await commands_help(ctx, ['lvlset toggle', 'lvlset levelmessage'], "furlvlset")

    @level_settings.command(name='toggle')
    async def level_settings_toggle(self, ctx):
        """ Toggles if level announcements should be done. """
        async with self.bot.pool.acquire() as db:
            current_value = await db.fetchval(
                "SELECT levels_announce FROM botsettings_guild WHERE id=$1",
                ctx.guild.id,
            )
            await db.execute(
                "UPDATE botsettings_guild SET levels_announce=NOT levels_announce WHERE id=$1",
                ctx.guild.id,
            )
            await ctx.send(
                f"Done! Level up notifications are now "
                f"{'enabled' if current_value is False else 'disabled'} for this server."
            )

    @level_settings.command(name="levelmessage", aliases=["levelmsg", "lvlmsg"])
    async def level_settings_message(self, ctx, *, message):
        """ Sets the level message """
        parsable = await parse_level_vars(ctx.author, 1, message)
        if parsable:
            async with self.bot.pool.acquire() as db:
                await db.execute(
                    "UPDATE botsettings_guild SET levels_message=$1 WHERE id=$2",
                    message,
                    ctx.guild.id,
                )
                return await ctx.send(
                    "Got it! Here's what the level up message will look like:\n"
                    f"{parsable}"
                )
        else:
            return await ctx.send(
                "Oops! Looks like there was a formatting error! Only the following variables "
                "can be used:\n{member}, {name}, {displayname}, {mention}, {guild}, {level}"
            )

    ####################################################################################################################
    #                               Auto roles command
    ####################################################################################################################
    @commands.group()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx):
        if ctx.invoked_subcommand is None:
            await commands_help(ctx,
                                ['autorole add',
                                 'autorole remove',
                                 'autorole list',
                                 'autorole bot',
                                 'autorole toggle'],
                                "furautorole"
                                )

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, role: discord.Role):
        """ Adds a role to be auto assigned when a user joins. """
        async with self.bot.pool.acquire() as db:
            autorole_list = await db.fetchval(
                "SELECT autoroles FROM botsettings_guild WHERE id=$1", ctx.guild.id
            )
            if role.id in autorole_list:
                return await ctx.send("That role is already in the autorole list!")
            else:
                autorole_list.append(role.id)
                await db.execute(
                    "UPDATE botsettings_guild SET autoroles=$1 WHERE id=$2",
                    autorole_list,
                    ctx.guild.id,
                )
                return await ctx.send(
                    f"Done! I'll automatically give {role.name} to members as they join this server."
                )

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, role: discord.Role):
        """ Removes a role from the auto assignment when a user joins. """
        async with self.bot.pool.acquire() as db:
            autorole_list = await db.fetchval(
                "SELECT autoroles FROM botsettings_guild WHERE id=$1", ctx.guild.id
            )
            if role.id in autorole_list:
                autorole_list.remove(role.id)
                await db.execute(
                    "UPDATE botsettings_guild SET autoroles=$1 WHERE id=$2",
                    autorole_list,
                    ctx.guild.id,
                )
                return await ctx.send(
                    f"Got it! I'll stop giving {role.name} to new members."
                )
            else:
                return await ctx.send("I can't find that role! Make sure it's spelled correctly!")

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def list(self, ctx):
        """ Lists the current roles configured to be added. """
        async with self.bot.pool.acquire() as db:
            autorole_list = await db.fetchval(
                "SELECT autoroles FROM botsettings_guild WHERE id=$1", ctx.guild.id
            )
            mapped_list = [role for role in ctx.guild.roles if role.id in autorole_list]
            return await ctx.send(
                f"Here are the roles I'll give to members as they join the server:\n{', '.join([role.name for role in mapped_list])}"
            )

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def bot(self, ctx, role: discord.Role):
        """ Sets the auto assigned role to a bot member that joins. """
        async with self.bot.pool.acquire() as db:
            await db.execute(
                "UPDATE botsettings_guild SET botautorole=$1 WHERE id=$2",
                role.id,
                ctx.guild.id,
            )
            return await ctx.send(f"Beep-boop! I'll make sure bots get {role.name} when you add them to the server!")

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def toggle(self, ctx, what, state):
        """ Toggles the autorole on/off """
        command_error_text = (
            "Whoops! I didn't understand that! Be sure to use this format:\n"
            "autorole toggle <user | bot | all> <on | off>"
        )
        if state.lower() == "on":
            state = True
        elif state.lower() == "off":
            state = False
        else:
            return await ctx.send(command_error_text)
        if what.lower() not in ["user", "bot", "all", "both"]:
            return await ctx.send(command_error_text)
        async with self.bot.pool.acquire() as db:
            if what.lower() in ["user", "all", "both"]:
                await db.execute(
                    "UPDATE botsettings_guild SET autoroles_enabled=$1 WHERE id=$2",
                    state,
                    ctx.guild.id,
                )
            if what.lower() in ["bot", "all", "both"]:
                await db.execute(
                    "UPDATE botsettings_guild SET botautorole_enabled=$1 WHERE id=$2",
                    state,
                    ctx.guild.id,
                )
        await ctx.send(
            f"Done! {what.title()} autoroles are now {'enabled' if state is True else 'disabled'}."
        )

    ####################################################################################################################
    #                               AutoPoster Config
    ####################################################################################################################

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
                            "fur**autoposter list** - Shows configuration..\n"
                            "fur**autoposter enable #channel** - enables the autoposter in the channel\n"
                            "fur**autoposter disable #channel** - disables the autoposter in the channel",
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
                    "INSERT INTO botsettings_autoposter (guild_id, channel, endpoint, enabled ) "
                    "VALUES ($1, $2, $3, $4)",
                    ctx.guild.id,
                    channel.id,
                    endpoint,
                    True,
                )
            await ctx.send(f"Added {channel.mention} with the endpoint {endpoint}.")

    @autoposter_index.command(name="enable")
    async def autoposter_enable(self, ctx, channel: discord.TextChannel):
        async with self.bot.pool.acquire() as db:
            await db.execute(
                "UPDATE botsettings_autoposter SET enabled=True WHERE channel=$1 AND guild_id=$2",
                channel.id,
                ctx.guild.id,
            )
            await ctx.send(f"Set {channel.name} from false to true :)")

    @autoposter_index.command(name="disable")
    async def autoposter_disable(self, ctx, channel: discord.TextChannel):
        async with self.bot.pool.acquire() as db:
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
                if chan is None:
                    continue
                channel_list += f"{chan.mention} | Enabled?: ``{channel['enabled']}`` | Content: ``{channel['endpoint']}``\n"
            if can_embed(ctx):
                embed = discord.Embed(color=self.bot.color, title="Autoposter", description=channel_list)
                return await ctx.send(embed=embed)
            await ctx.send(channel_list)

    ####################################################################################################################
    #                               Smash or Pass Config
    ####################################################################################################################
    @commands.group(name="autosnp", aliases=["autosmashnpass"])
    @commands.check(premium_guild_check)
    async def smash_n_pass_config(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=self.bot.color,
                description="fur**autosnp set #channel endpoint role** - Sets the channel to be smash or pass auto\n"
                            "- Role argument can be empty\n"
                            "**Example usage:** `furautosnp set #auto-gay gay SmashPass`\n"
                            "fur**autosnp role channel, enabled, role** - "
                            "Changes the role if role is presented in the arguments and enables/disables role pinging\n"
                            "- Role argument can be empty\n"
                            "\n"
                            "**Supported endpoints include:**\n"
                            "```fix\n"
                            "bang, bisexual, nboop, nbound, nbulge, cuntboy, dick, "
                            "finger, nfuta, gay, gif, ngroup, nkiss, lesbian, nlick, pussy, "
                            "nseduce, nsolo, nspank, suck, ntease, ntrap, yiff\n"
                            "```",
            )
            await ctx.send(embed=embed)

    @smash_n_pass_config.command(name="set")
    @commands.has_permissions(manage_channels=True)
    async def smash_n_pass_config_set(
            self,
            ctx,
            channel: discord.TextChannel,
            endpoint: str,
            *,
            role: discord.Role = None,
    ):
        try:
            async with self.bot.pool.acquire() as db:
                channels = await db.fetch(
                    "SELECT channel FROM botsettings_smashnpass where guild_id=$1",
                    ctx.guild.id,
                )
                if role is None:
                    if endpoint in nsfw_endpoints:
                        if channel.id not in channels:
                            await db.execute(
                                "INSERT INTO botsettings_smashnpass "
                                "(guild_id, channel, endpoint, enabled, role, role_enabled) "
                                "VALUES ($1, $2, $3, $4, $5, $6)",
                                ctx.guild.id,
                                channel.id,
                                endpoint,
                                True,
                                None,
                                False,
                            )
                            await ctx.send(
                                f"Added {channel.mention} with endpoint {endpoint} without role mention."
                            )
                            embed = discord.Embed(
                                color=self.bot.color,
                                title="Auto Smash n Pass",
                                description="If you are reading this message, Then all checks have passed.\n"
                                            "I will now attempt to post smash n passes every 12 hours! I hope you enjoy",
                            )
                            if can_embed(ctx) and channel.is_nsfw():
                                await channel.send(embed=embed)
                            else:
                                try:
                                    await ctx.author.send(
                                        "It appears that some of the permission checks have "
                                        "failed and the channel isn't marked as NSFW.\n"
                                        "I require the following permissions to work.\n"
                                        "```fix\n"
                                        "MANAGE_CHANNELS, SEND_MESSAGES, EMBED_LINKS, ADD_REACTIONS```"
                                    )
                                except discord.Forbidden:
                                    if can_send(ctx):
                                        await ctx.send(
                                            "It appears that some of the permission checks have failed.\n"
                                            "I require the following permissions to work.\n"
                                            "```fix\n"
                                            "Manage Channel, Send Messages, Embed Links, Add Reactions```"
                                        )

                        else:
                            return await ctx.send(
                                "Looks like smash n pass has already been set on this channel! "
                                "You can only set one smash n pass per channel!"
                            )
                    else:
                        await ctx.send(
                            f"Endpoint `{endpoint}` is not supported. Supported endpoints include:\n"
                            "```fix\n"
                            "bang, bisexual, nboop, nbound, nbulge, cuntboy, dick, "
                            "finger, nfuta, gay, gif, ngroup, nkiss, lesbian, nlick, "
                            "pussy, nseduce, nsolo, nspank, suck, ntease, ntrap, yiff\n"
                            "```"
                        )
                else:
                    if endpoint in nsfw_endpoints:
                        if channel not in channels:
                            await db.execute(
                                "INSERT INTO botsettings_smashnpass "
                                "(guild_id, channel, endpoint, enabled, role, role_enabled)"
                                " VALUES ($1, $2, $3, $4, $5, $6)",
                                ctx.guild.id,
                                channel.id,
                                endpoint,
                                True,
                                role.id,
                                True,
                            )
                            await ctx.send(
                                f"Added {channel.mention} with endpoint {endpoint} "
                                f"with the role {role.mention} to mention."
                            )
                        else:
                            return await ctx.send(
                                "Looks like smash n pass has already been set on this channel! "
                                "You can only set one smash n pass per channel!"
                            )
                    else:
                        await ctx.send(f"Endpoint {endpoint} is not supported.")
        except discord.Forbidden:
            await ctx.send(
                "I can't find that channel! Make sure I can read messages in that channel..\n"
                "**Please also make sure I have the following permissions in the desired channel:**\n"
                "```fix\n"
                "Manage Channel, Send Messages, Embed Links, Add Reactions```"
            )

    @smash_n_pass_config.command(name="role")
    async def smash_n_pass_role_config(
            self, ctx, channel: discord.TextChannel, enabled, role: discord.Role = None
    ):
        async with self.bot.pool.acquire() as db:
            channels = await db.fetch(
                "SELECT channel FROM botsettings_smashnpass WHERE guild_id=$1",
                ctx.guild.id,
            )
            if channel in channels:
                if enabled and role:
                    await db.execute(
                        "UPDATE botsettings_smashnpass SET role=$1, role_enabled=$2 WHERE channel=$3",
                        role.id,
                        True,
                        channel.id,
                    )
                    await ctx.send(
                        f"Okay, I have set {role.mention} as the role for "
                        f"pings and have enabled role pings for {channel.mention}!"
                    )
                else:
                    await db.execute(
                        "UPDATE botsettings_smashnpass SET role=$1, role_enabled=$2, WHERE channel=$3",
                        role.id,
                        True,
                        channel.id,
                    )
                    await ctx.send(
                        f"Okay, I have set {role.mention} as the role for "
                        f"pings and have disabled role pings for {channel.mention}!"
                    )
                if enabled and not role:
                    await db.execute(
                        "UPDATE botsettings_smashnpass SET role_enabled=$1 WHERE channel=$2",
                        True,
                        channel.id,
                    )
                    await ctx.send(f"I have enabled role pings for {channel.mention}.")
                else:
                    await db.execute(
                        "UPDATE botsettings_smashnpass SET role_enabled=$1 WHERE channel=$2",
                        False,
                        channel.id,
                    )
                    await ctx.send(f"I have disabled role pings for {channel.mention}.")
            else:
                await ctx.send(
                    "Looks like the channel isn't a smash or pass auto, or you have not configured it. "
                    "Please use `furautosnp set`!"
                )

    ####################################################################################################################
    #                               React Roles
    ####################################################################################################################
    @commands.command(aliases=["reactroles"])
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def reactrole(
            self,
            ctx,
            channel: discord.TextChannel,
            message_id: int,
            emoji: str,
            *,
            role: RoleID,
    ):
        if "<a" in emoji:
            r = emoji.replace("<a", "").replace(">", "")
            r = r.replace(":", "").replace(":", "")
            emoji_name = "".join("" if c.isdigit() else c for c in r)
        elif "<" in emoji:
            r = emoji.replace("<", "").replace(">", "")
            r = r.replace(":", "").replace(":", "")
            emoji_name = "".join("" if c.isdigit() else c for c in r)
        else:
            emoji_name = emoji.replace(":", "").replace(":", "")
            # if "<" in emoji:
            # emoji_name = emoji.replace("<", "").replace(">", "")
            # else:
            # emoji_name = emoji.replace(":", "")
        try:
            channel = ctx.guild.get_channel(channel.id)
            message = await channel.fetch_message(message_id)
            await message.add_reaction(emoji)
        except discord.NotFound:
            url = "https://support.discordapp.com/hc/en-us/articles/" \
                  "206346498-Where-can-I-find-my-User-Server-Message-ID-"
            return await ctx.send(
                "Are you sure that the message ID is a indeed a message ID? Please double check and try again.\n"
                f"See {url} if you are unsure how to get a message ID."
            )
        except discord.HTTPException:
            return await ctx.send(
                "Looks like I ran into some trouble! Make sure the emoji exists! "
                "If you're using a custom emoji, I need to be in whatever server that emoji came from."
            )

        async with ctx.bot.pool.acquire() as db:
            check_combo = await db.fetchrow(
                "SELECT * FROM botsettings_reactroles WHERE guild_id = $1 AND channel_id = $2 "
                "AND message_id = $3 AND role_id = $4 AND emoji_id = $5",
                ctx.guild.id,
                channel.id,
                message_id,
                role,
                emoji_name,
            )
            rx = discord.utils.get(ctx.guild.roles, id=role)
            if check_combo:
                await db.execute(
                    "DELETE FROM botsettings_reactroles WHERE guild_id = $1 "
                    "AND channel_id = $2 AND message_id = $3 AND role_id = $4 AND emoji_id = $5",
                    ctx.guild.id,
                    channel.id,
                    message_id,
                    role,
                    emoji_name,
                )
                return await ctx.send(
                    f"Alrighty! **{rx.name}** and {emoji} have been removed from message ``{message_id}``."
                )
            else:
                await db.execute(
                    "INSERT INTO botsettings_reactroles (guild_id, channel_id, message_id, role_id, emoji_id) "
                    "VALUES ($1, $2, $3, $4, $5)",
                    ctx.guild.id,
                    channel.id,
                    message_id,
                    role,
                    emoji_name,
                )
                await ctx.send(
                    f"Done! I've set **{rx.name}** as a reaction role with the emoji {emoji} on message ``{message_id}``."
                )

    ###################################################################################################################
    #                           Self Roles Configuration
    ###################################################################################################################
    async def get_roles(self, guild_id):
        async with self.bot.pool.acquire() as db:
            roles = await db.fetchval(
                "SELECT selfroles FROM botsettings_guild WHERE id=$1", guild_id
            )
        return roles if roles else []

    async def role_update(self, roles, guild_id):
        async with self.bot.pool.acquire() as db:
            await db.execute(
                "UPDATE botsettings_guild SET selfroles=$1 WHERE id=$2", roles, guild_id
            )

    def role_name(self, ctx, role):
        role_name = discord.utils.get(ctx.guild.roles, id=role).name
        if role_name is None:
            role_name = "blank"
        return role_name

    @commands.guild_only()
    @commands.group(aliases=["sr"])
    async def selfroles(self, ctx):
        """ Self Role Management """
        if ctx.invoked_subcommand is None:
            msg = (
                "**Description:** Self Roles adding and removing\n"
                "**Cooldown:** 3 seconds\n"
                f"**Usage:** fur**selfroles** [subcommand]\n"
                f"**Example:** fur**selfroles** add @CoolRole"
            )
            embed = discord.Embed(color=self.bot.color, description=msg)
            embed.set_author(
                name="Self Roles System", icon_url=avatar_check(self.bot.user)
            )
            embed.add_field(name="How to use", value=help_text)
            embed.add_field(name="Learning Self Roles", value=help_text_2, inline=False)
            embed.add_field(name="Commands", value=help_commands)
            embed.set_footer(text="Murrrrr! 🐾", icon_url=icon_check(ctx.guild))
            return await ctx.channel.send(embed=embed)

    @commands.guild_only()
    @selfroles.group(name="add")
    @commands.has_permissions(manage_roles=True)
    async def _add(self, ctx, *, role: RoleID):
        """ Add a role to the self assigned system """

        # Check if the user didn't pass in a role in the args
        # if role is None:
        # return await ctx.send(
        # "I'm sorry, I can't find the role you want me to add.\n"
        # "Maybe check your spelling?\n"
        # "Note: Currently Case Sensitive.")

        # Get list of self-assign roles for guild
        roles = await self.get_roles(ctx.guild.id)

        # Check if role is already in the list
        if role in roles:
            return await ctx.send(
                f'{self.bot.emote["Paws"]} M-Murr!,'
                f" this role is already in the self assignable role list. "
                f'{self.bot.emote["Paws"]}'
            )

        # Check if bot has permissions to manage roles
        if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
            return await ctx.send("🐾 Murr, I need the `Manage Roles` permission to do that! 🐾")

        # Add role to role list and update value in database
        roles.append(role)
        await self.role_update(roles, ctx.guild.id)
        # {self.bot.mur} self.bot.emote["paws"]
        await ctx.send(
            f'{self.bot.emote["Paws"]} Arf Arf~! As requested, I\'ve added **{self.role_name(ctx, role)}** '
            f'to {ctx.guild.name}\'s self assignable roles list. {self.bot.emote["Paws"]}'
        )

    @commands.guild_only()
    @selfroles.group(name="delete")
    @commands.has_permissions(manage_roles=True)
    async def _del(self, ctx, *, role: RoleID):
        """ Delete a role from the self assigned system """

        # Check if the user didn't pass in a role in the args
        # if role is None:
        # return await ctx.send(
        # "I'm sorry, I can't find the role you want me to delete.\n"
        # "Maybe check your spelling?\n"
        # "Note: Currently Case Sensitive.")

        # Get list of self-assign roles for guild
        roles = await self.get_roles(ctx.guild.id)

        # Check if bot has Manage Roles permission
        if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
            return await ctx.send("🐾 Murr, I need the `Manage Roles` permission before I can do that. 🐾")

        # Check if role is in role list, remove if so
        if role in roles:
            roles.remove(role)
            await self.role_update(roles, ctx.guild.id)
            return await ctx.send(
                f"🐾 Murr, as requested, I\'ve removed **{self.role_name(ctx, role)}** "
                f"from **{ctx.guild.name}**'s self assignable roles. 🐾"
            )
        else:
            return await ctx.send(
                "🐾 Oop, this role isn't in the self assignable role list! 🐾"
            )

    @commands.guild_only()
    @commands.command(name="iam", aliases=["grant"])
    async def _give(self, ctx, *, role: RoleID_member):
        """ Grants a role from the self-role system """

        # Check if bot has Manage Roles permission
        if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
            return await ctx.send(
                "🐾 Hey! I need the `Manage Roles permission` before I can assign roles to members! 🐾")

        # Get list of self-assign roles for guild
        roles = await self.get_roles(ctx.guild.id)
        if role in roles:
            # Gets necessary role information
            role_get = discord.utils.get(ctx.guild.roles, id=role)
            if role_get is None:
                return
            elif role_get in ctx.author.roles:
                return await ctx.send(
                    "🐾 Looks like you already have this role. 🐾"
                )
            try:
                await ctx.author.add_roles(role_get, reason="Self-assigned removal")
            except discord.Forbidden as e:
                return await ctx.send(f"{e}")
            return await ctx.send(
                f"Done! You now have the {self.role_name(ctx, role)} role."
            )
        else:
            await ctx.send(
                "🐾 Murr, this role isn't in the self assignable role list. Add it with `fursr add`! 🐾"
            )

    @commands.guild_only()
    @commands.command(name="iamnot", aliases=["revoke"])
    async def _take(self, ctx, *, role: RoleID_member):
        """ Revokes a role from the self-role system """

        # Check if bot has Manage Roles permission
        if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
            return await ctx.send(
                "🐾 Murr, I need the `Manage Roles` permission before I can remove roles from members! 🐾")

        # Get list of self-assign roles for guild
        roles = await self.get_roles(ctx.guild.id)
        if role in roles:
            # Gets necessary role information
            role_get = discord.utils.get(ctx.guild.roles, id=role)
            if role_get is None:
                return
            elif role_get not in ctx.author.roles:
                return await ctx.send(
                    "🐾 Murr, you don't have this role. 🐾"
                )
            await ctx.author.remove_roles(role_get, reason="Self-assigned removal")
            return await ctx.send(
                f"Done! I've removed {self.role_name(ctx, role)} from you. Are you feeling any lighter?"
            )
        else:
            await ctx.send(
                "🐾 Murr, this role isn't in the self assignable role list. 🐾"
            )
        # Check if role was provided, if not ask what role to remove
        # if role is None:
        # named_roles = [role.name for role in ctx.guild.roles if role.id in roles]

        # await ctx.send("What role do you want to remove from yourself?")

        # def pred(m):
        # return m.author == ctx.author and m.channel == ctx.channel

        # try:
        # role_message = await ctx.bot.wait_for("message", check=pred, timeout=60.0)
        # except asyncio.TimeoutError:
        # return await ctx.send("No worries, you can run the command again when you're ready")

        # if role_message.content in named_roles:
        # role = discord.utils.get(ctx.guild.roles, name=role_message.content)
        # await ctx.author.remove_roles(role, reason="Self-assigned")
        # return await ctx.send(f"Done! You no longer have the {role.name} role")
        # else:
        # return await ctx.send(f"Hmm, I can't remove the **{role_message.clean_content}** role since it either "
        # "doesn't exist or it isn't part of the self-assign roles")

        # Remove role if one is passed in arg directly
        # else:

    @commands.guild_only()
    @selfroles.command(name="list")
    async def _rlist(self, ctx):
        """ Shows current self roles in the system. """

        # Check if bot has Manage Roles permission
        # if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
        #    return await ctx.send("🐾 Murr, I need the Manage Roles permission. 🐾")

        # Get list of self-assign roles for guild
        roles = await self.get_roles(ctx.guild.id)
        if not roles:
            return await ctx.send("This is a pretty short list! A whopping 0 roles! Maybe you should add some.")

        # Format roles into paginated messages
        role_message = commands.Paginator(prefix="", suffix="", max_size=1024)
        role_message.add_line(
            f"**Self-Assignable Roles for {ctx.guild.name}:**", empty=True
        )
        for role in roles:
            guild_role = ctx.guild.get_role(role)
            if guild_role:
                members = len(
                    [
                        member
                        for member in ctx.guild.members
                        if guild_role in member.roles
                    ]
                )
                role_message.add_line(
                    f'{guild_role.mention} ({members} member{"" if members == 1 else "s"})'
                )
            else:
                roles.remove(role)
                await self.role_update(roles, ctx.guild.id)

        # Format the embed with basic info
        embed = discord.Embed(color=self.bot.color, description="Self-Assignable Roles")
        embed.set_author(name=ctx.guild.name, icon_url=icon_check(ctx.guild))
        embed.set_thumbnail(url=avatar_check(self.bot.user))
        embed.set_footer(
            text="To add a role to yourself: **furiam**\n"
                 "To remove a role from yourself: **furiamnot**"
        )

        # Add pages of roles to the embed, shouldn't be more than one page unless there are a shit ton of
        # self-assignable roles in a guild
        page_number = 1
        for page in role_message.pages:
            if len(role_message.pages) > 1:
                embed.add_field(
                    name=f"Roles ({page_number} of {len(role_message.pages)})",
                    value=page,
                    inline=False,
                )
            else:
                embed.add_field(name=f"Roles", value=page, inline=False)

        # Finally, send the embed
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Guild_settings(bot))
