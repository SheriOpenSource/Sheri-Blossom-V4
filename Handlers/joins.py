from datetime import datetime

import discord
from discord.ext import commands
from sentry_sdk import capture_exception

from Database.transactions import add_guild, add_user
from Formats.formats import avatar_check, icon_check
from Formats.text import parse_welcome_vars
from Functions.dehoist import dehoist
from Functions.logging import Logging
from Lines.custom_emotes import logging_emotes


class Joins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    async def handle_exception(self, guild_info, member, role_list, e):
        if guild_info["moderation_channel"]:
            await self.bot.get_channel(guild_info["moderation_channel"]).send(
                f"Error when adding roles ({', '.join([role.name for role in role_list])}) to {member}:\n{e}"
            )
        else:
            try:
                await member.guild.owner.send(
                    f"Error when adding roles ({', '.join([role.name for role in role_list])}) "
                    f"to {member} in {member.guild.name}:\n{e}"
                )
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.bot.is_ready():
            return
        try:
            # Invite tracker
            # async with self.bot.pool.acquire() as db:
            #     stored_invites = await db.execute("SELECT * FROM botsettings_invite WHERE guild_id=$1", member.guild.id)
            # invite_used = None
            # for invite in stored_invites:
            #     guild_invite = await self.bot.fetch_invite(invite, with_counts=False)
            #     if guild_invite.uses != invite.uses:
            #         invite_used = guild_invite
            #
            # if invite_used:
            #     await invite_tracker(db, invite_used)  # Move to within acquire() block before turning back on
            invite_used = False
            member_channel = None
            # Base info
            channel = None
            async with self.bot.pool.acquire() as db:
                # Add user to database first and foremost
                await add_user(db, member)
                guild_info = await db.fetchrow(
                    "SELECT * FROM botsettings_guild WHERE id=$1", member.guild.id)
                if guild_info is not None:
                    # Auto Role - Members
                    role_list = None
                    if guild_info["autoroles_enabled"]:
                        auto_roles = guild_info["autoroles"]
                        role_list = [
                            role for role in member.guild.roles if role.id in auto_roles
                        ]
                        try:
                            if not member.bot:
                                await member.add_roles(
                                    *role_list, reason="Autoroles added on join"
                                )
                        except (discord.Forbidden, discord.HTTPException) as e:
                            await self.handle_exception(guild_info, member, role_list, e)

                    # Auto Role - Bots
                    if member.bot:
                        if guild_info["botautorole_enabled"]:
                            if not guild_info["botautorole"]:
                                return

                            try:
                                role = member.guild.get_role(guild_info["botautorole"])
                                await member.add_roles(
                                    role, reason="Autoroles added on join"
                                )
                            except (discord.Forbidden, discord.HTTPException) as e:
                                await self.handle_exception(
                                    guild_info, member, role_list, e
                                )

                    # Persistent roles
                    if guild_info["persistent_roles_enabled"]:
                        try:
                            previous_roles = await db.fetchval(
                                """SELECT roles FROM botsettings_guildroles WHERE
                                                               guild_id=$1 AND member_id=$2""",
                                member.guild.id,
                                member.id,
                            )
                            if previous_roles:
                                roles_to_add = []
                                roles_to_delete = False
                                for role_id in previous_roles:
                                    role = member.guild.get_role(role_id)
                                    if role:
                                        if role.name != "@everyone":
                                            roles_to_add.append(role)
                                    else:
                                        roles_to_delete = True
                                if roles_to_add:
                                    await member.add_roles(
                                        *roles_to_add, reason="Persistent roles"
                                    )
                                if roles_to_delete:
                                    await db.execute(
                                        """UPDATE botsettings_guildroles SET roles=$3 WHERE guild_id=$1 AND member_id=$2""",
                                        member.guild.id,
                                        member.id,
                                        [role.id for role in roles_to_add],
                                    )
                        except discord.Forbidden:
                            pass
                        except Exception as e:
                            self.bot.sentry.capture_execption(e)

                    # Welcomer
                    # if guild_info["welcome_join_enabled"]:
                    text = guild_info["welcome_message"]
                    text = await parse_welcome_vars(text, member, member.guild)
                    if text:
                        embed = guild_info['welcome_leave_embed']
                        channel = self.bot.get_channel(guild_info["welcome_channel"])
                        if embed:
                            if channel:
                                embed = discord.Embed(color=discord.Colour.green(),
                                                      description=text, title=f"Welcome {member.display_name}!")
                                embed.set_author(name=member.guild.name, icon_url=icon_check(member.guild))
                                embed.set_thumbnail(url=avatar_check(member))
                                await channel.send(embed=embed)
                        elif channel:
                            await channel.send(text)

                    # Logs
                    guild_data = await Logging.log_channel(self, "member_channel", member.guild)
                    log_channel = guild_data[0]
                    embed_enabled = guild_data[1]
                    if log_channel:
                        description = (
                            f"Username: **{str(member)}**\n"
                            f"Display Name: **{member.display_name}**\n"
                            f"User ID: **{member.id}**\n"
                            f"Bot: **{member.bot}**\n"
                            f"Created At: **{member.created_at.strftime('%A, %B %d %Y @ %H:%M:%S %p')}**\n"
                            f"Joined Server: **{datetime.utcnow().strftime('%A, %B %d %Y @ %H:%M:%S %p')}**"
                        )
                        if embed_enabled:
                            embed = discord.Embed(
                                title="A member has joined!",
                                timestamp=datetime.utcnow(),
                                description=description,
                            )
                            if invite_used:
                                embed.add_field(
                                    name="Invited by",
                                    value=invite_used.inviter,
                                    inline=False,
                                )
                                embed.add_field(
                                    name="Using invite", value=invite_used.url, inline=False
                                )
                            embed.set_author(
                                name=member.display_name, icon_url=avatar_check(member)
                            )
                            embed.set_thumbnail(url=avatar_check(member))
                            await log_channel.send(embed=embed)
                        else:
                            await log_channel.send(
                                content=f"{logging_emotes['memberjoin']} {'🤖' if member.bot else '👤'}"
                                        f"**{member}**(``{member.id}``) has joined the server.\n"
                            )

                # Dehoist and Anti Zalgo in names
                await dehoist(self, member, guild_info)
        except (AttributeError, discord.HTTPException, discord.Forbidden):
            return
        except Exception as e:
            capture_exception(e)
            print(e)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.bot.counter["guild_join"] += 1
        home = self.bot.get_guild(346892627108560901)
        channel = home.get_channel(612293479577681971)
        async with self.bot.pool.acquire() as db:
            await add_user(
                db, guild.owner
            )  # Adding owner first so add_guild doesn't fail
            for member in guild.members:
                await add_user(db, member)
            await add_guild(db, guild)

            # async with self.session as session:
            #    webhook = discord.Webhook.from_url(
            #        "https://discordapp.com/api/webhooks/612293509856362526/QRE-G9IXFPQPfWvAa4SNiF-me2aGl_RmrH0KqDJxjlscNeOHCnI9NHoTp8epvuw_uk3D",
            #        adapter=discord.AsyncWebhookAdapter(session),
            #    )

            # Embed in Sheri Discord
            member_members = len([member for member in guild.members if not member.bot])
            bot_members = len([member for member in guild.members if member.bot])
            bot_percentage = round(bot_members / guild.member_count * 100)

            embed = discord.Embed(
                title="Joined a guild",
                timestamp=datetime.utcnow(),
                color=self.bot.success_color,
            )

            embed.add_field(
                name="Guild info",
                value=f"**Name:** {guild.name}\n"
                      f"**ID:** {guild.id}\n"
                      f"**Owner:** {guild.owner.mention} ({guild.owner})\n"
                      f"**Users | Bots:** {member_members:,} | {bot_members:,} ({bot_percentage}% bots)",
                inline=False,
            )

            embed.add_field(
                name="Bot stats",
                value=f"**Guilds:** {len(self.bot.guilds):,}\n"
                      f"**Users:** {len(set(self.bot.users)):,}",
                inline=False,
            )
            embed.set_thumbnail(url=icon_check(guild))
            try:
                print(f"[Guilds] - Joined {guild.name}(Owner: {guild.owner}).")
            except ValueError as e:
                capture_exception(e)
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Joins(bot))
