import discord
from discord.ext import commands

from Formats.formats import avatar_check, icon_check, RoleID, RoleID_member

help_text = (
    "To start using self roles with me, you must ensure that I have the following permissions:\n"
    "manage roles, send embeds, send messages."
    "With anybody on discord, I need to be able to access the roles, so please make "
    "sure I am able to tinker with the roles by putting my role on the top of the roles you want self assigned.\n"
    "Now let's get started on learning self roles.\n"
    "Self roles are roles that you set with me that people can self assign by using the "
    "commands ``furiam`` or ``furiamnot``. You can find all the commands and arguments below "
    "needed to make the system work."
)

help_commands = (
    "fur**selfroles|sr list** |- List's the available roles configured by guild(server) admin\n"
    "fur**selfroles|sr add** |- `[R: Manage_Roles]` Add a role to the self role configuration\n"
    "fur**selfroles|sr delete** |- `[R: Manage_roles]` Delete a role from the self role configuration\n"
    "fur**iam|grant rolename**`[see above]` |- Gives the caller the role specified if on configuration or list\n"
    "fur**iamnot|revoke rolename** `[see above]` |- Removes the role specified from the caller."
)

bad_argument_text = (
    "Uh oh, I can't find that role in here, are you sure you spelled it right?\n"
    "Remember that capitalization matters, coolrolename isn't the same to me as CoolRoleName!"
)


class SelfRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    # get's the role name for use in strings (without mentioning them)
    def role_name(self, ctx, role):
        role_name = discord.utils.get(ctx.guild.roles, id=role).name
        if role_name is None:
            role_name = "blank"
        return role_name

    @commands.guild_only()
    @commands.group(aliases=["sr"])
    async def selfroles(self, ctx):
        """Self Role Management"""
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
            embed.add_field(name="Commands", value=help_commands)
            embed.set_footer(text="Murrrrr! 🐾", icon_url=icon_check(ctx.guild))
            return await ctx.channel.send(embed=embed)

    @commands.guild_only()
    @selfroles.group(name="add")
    @commands.has_permissions(manage_roles=True)
    async def _add(self, ctx, *, role: RoleID):
        """add a role to the self assigned system"""

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
                f" this role is already added to the self assignable role list. "
                f'{self.bot.emote["Paws"]}'
            )

        # Check if bot has permissions to manage roles
        if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
            return await ctx.send("🐾 Murr, I need the Manage Roles permission. 🐾")

        # Add role to role list and update value in database
        roles.append(role)
        await self.role_update(roles, ctx.guild.id)
        # {self.bot.mur} self.bot.emote["paws"]
        await ctx.send(
            f'{self.bot.emote["Paws"]} Arf Arf, as requested I have added **{self.role_name(ctx, role)}** '
            f'to the self assignable roles in **{ctx.guild.name}**. {self.bot.emote["Paws"]}'
        )

    # @_add.error
    # async def _add_error(self, ctx, error):
    # if isinstance(error, commands.BadArgument):
    # await ctx.send(bad_argument_text)

    @commands.guild_only()
    @selfroles.group(name="delete")
    @commands.has_permissions(manage_roles=True)
    async def _del(self, ctx, *, role: RoleID):
        """delete a role from the self assigned system"""

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
            return await ctx.send("🐾 Murr, I need the Manage Roles permission. 🐾")

        # Check if role is in role list, remove if so
        if role in roles:
            roles.remove(role)
            await self.role_update(roles, ctx.guild.id)
            return await ctx.send(
                f"🐾 Murr, as requested, I have removed **{self.role_name(ctx, role)}** "
                f"from **{ctx.guild.name}**'s self assignable roles. 🐾"
            )
        else:
            return await ctx.send(
                "🐾 Murr, this role isn't in the self assignable role list. 🐾"
            )

    # @_del.error
    # async def _del_error(self, ctx, error):
    # if isinstance(error, commands.BadArgument):
    # await ctx.send(bad_argument_text)

    @commands.guild_only()
    @commands.command(name="iam", aliases=["grant"])
    async def _give(self, ctx, *, role: RoleID_member):
        """Grants a role from the selfrole system"""

        # Check if bot has Manage Roles permission
        if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
            return await ctx.send("🐾 Murr, I need the Manage Roles permission. 🐾")

        # Get list of self-assign roles for guild
        roles = await self.get_roles(ctx.guild.id)
        if role in roles:
            # Gets necessary role information
            role_get = discord.utils.get(ctx.guild.roles, id=role)
            if role_get is None:
                return
            elif role_get in ctx.author.roles:
                return await ctx.send(
                    "🐾 Murr, you already possess this role at this time. 🐾"
                )
            await ctx.author.add_roles(role_get, reason="Self-assigned removal")
            return await ctx.send(
                f"Done! You now have the {self.role_name(ctx, role)} role"
            )
        else:
            await ctx.send(
                "🐾 Murr, this role isn't in the self assignable role list. 🐾"
            )

        # Check if role was provided, if not ask what role to add
        # if role is None:
        # named_roles = [role.name for role in ctx.guild.roles if role.id in roles]

        # await ctx.send("What role do you want to assign yourself?")

        # def pred(m):
        # return m.channel == ctx.channel and m.author == ctx.author

        # try:
        # role_message = await ctx.bot.wait_for("message", check=pred, timeout=60.0)
        # except asyncio.TimeoutError:
        # return await ctx.send("No worries, you can run the command again when you're ready")

        # if role_message.content in named_roles:
        # role = discord.utils.get(ctx.guild.roles, name=role_message.content)
        # await ctx.author.add_roles(role, reason="Self-assigned")
        # else:
        # return await ctx.send(
        # f"Hmm, I can't give you the **{role_message.clean_content}** role since it either "
        # "doesn't exist or it isn't part of the self-assign roles")

        # Add role if one is passed in arg directly
        # else:
        # if role.id in roles:
        # await ctx.author.add_roles(role, reason="Self-assigned")
        # await ctx.send(f"Done! You now have the {role.name} role")

    # @_give.error
    # async def _give_error(self, ctx, error):
    # if isinstance(error, commands.BadArgument):
    # await ctx.send(bad_argument_text)

    @commands.guild_only()
    @commands.command(name="iamnot", aliases=["revoke"])
    async def _take(self, ctx, *, role: RoleID_member):
        """Revokes a role from the selfrole system"""

        # Check if bot has Manage Roles permission
        if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
            return await ctx.send("🐾 Murr, I need the Manage Roles permission. 🐾")

        # Get list of self-assign roles for guild
        roles = await self.get_roles(ctx.guild.id)
        if role in roles:
            # Gets necessary role information
            role_get = discord.utils.get(ctx.guild.roles, id=role)
            if role_get is None:
                return
            elif role_get not in ctx.author.roles:
                return await ctx.send(
                    "🐾 Murr, you do not possess this role at this time. 🐾"
                )
            await ctx.author.remove_roles(role_get, reason="Self-assigned removal")
            return await ctx.send(
                f"Done! You no longer have the {self.role_name(ctx, role)} role"
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

    # @_take.error
    # async def _take_error(self, ctx, error):
    # if isinstance(error, commands.BadArgument):
    # await ctx.send(bad_argument_text)

    @commands.guild_only()
    @selfroles.command(name="list")
    async def _rlist(self, ctx):
        """shows current self roles in the system."""

        # Check if bot has Manage Roles permission
        if not ctx.channel.permissions_for(ctx.guild.me).manage_roles:
            return await ctx.send("🐾 Murr, I need the Manage Roles permission. 🐾")

        # Get list of self-assign roles for guild
        roles = await self.get_roles(ctx.guild.id)
        if not roles:
            return await ctx.send("There are no self-assign roles for this guild.")

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

        # Add pages of roles to the embed, shouldn't be more than one page unless there are a shitton of
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
    bot.add_cog(SelfRoles(bot))
