from datetime import timedelta, datetime, timezone
from random import randint

import discord
from discord.ext import commands

from Checks.bot_checks import can_embed, can_edit_role
from Database.transactions import add_user, add_guild_level
from Formats.formats import avatar_check
from Formats.text import parse_level_vars


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _get_level_xp(n):
        return 5 * (n ** 2) + 50 * n + 100

    @staticmethod
    def _get_level_from_xp(xp):
        remaining_xp = int(xp)
        level = 0
        while remaining_xp >= Levels._get_level_xp(level):
            remaining_xp -= Levels._get_level_xp(level)
            level += 1
        return level

    async def banned_role_or_channel(self, ctx, db):
        record = await db.fetchrow(
            "SELECT no_xp_roles, no_xp_channels FROM botsettings_guild WHERE id=$1",
            ctx.guild.id,
        )
        is_banned = False
        for role in ctx.author.roles:
            if role.id in record["no_xp_roles"]:
                is_banned = True
        if ctx.channel.id in record["no_xp_channels"]:
            is_banned = True
        return is_banned

    @commands.guild_only()
    @commands.command(aliases=["xp", "rank"])
    async def level(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        async with self.bot.pool.acquire() as db:
            if await self.banned_role_or_channel(ctx, db):
                return

            member_info = await self.get_member_info(db, member)

            if can_embed(ctx):
                embed = discord.Embed(title="", color=self.bot.color)
                embed.add_field(
                    name="Guild Level", value=f"{member_info['guild_level']}"
                )
                embed.add_field(
                    name="Guild XP",
                    value=f"{member_info['remaining_guild_xp']:,}/{member_info['guild_level_xp']:,}\n"
                          f"({member_info['guild_xp']:,})",
                )
                embed.set_author(
                    name=member.display_name, icon_url=avatar_check(member)
                )
                embed.set_footer(
                    text="https://Sheri.bot", icon_url=avatar_check(ctx.guild.me)
                )
                embed.set_thumbnail(url=avatar_check(member))
                await ctx.send(embed=embed)

    async def get_member_info(self, db, member):
        guild_xp = await db.fetchval(
            "SELECT xp FROM botsettings_guildlevel WHERE guild_id=$1 AND member_id=$2",
            member.guild.id,
            member.id,
        )
        if guild_xp is None:
            await add_guild_level(self.bot.pool, member.guild, member)
            guild_xp = 0
        member_xp = await db.fetchval(
            "SELECT xp FROM botsettings_user WHERE id=$1", member.id
        )
        guild_level = self._get_level_from_xp(guild_xp)
        global_level = self._get_level_from_xp(member_xp)
        x = 0
        for y in range(0, global_level):
            x += self._get_level_xp(y)
        remaining_global_xp = member_xp - x
        x = 0
        for y in range(0, guild_level):
            x += self._get_level_xp(y)
        remaining_guild_xp = guild_xp - x
        global_level_xp = self._get_level_xp(global_level)
        guild_level_xp = self._get_level_xp(guild_level)

        return {
            "guild_xp": guild_xp,
            "guild_level": guild_level,
            "remaining_guild_xp": remaining_guild_xp,
            "guild_level_xp": guild_level_xp,
            "global_xp": member_xp,
            "global_level": global_level,
            "remaining_global_xp": remaining_global_xp,
            "global_level_xp": global_level_xp,
        }

    async def get_redis_user_info(self, message):
        async with self.bot.redis_pool.get() as r:
            last_added = await r.execute("get", f"{message.author.id}_xp_last_added")
            if last_added:
                last_added = datetime.fromisoformat(last_added.decode("utf-8"))
                guild_xp = await r.execute(
                    "get", f"{message.guild.id}{message.author.id}_xp"
                )
                if not guild_xp:
                    guild_xp = 0
                    await r.execute(
                        "set", f"{message.guild.id}{message.author.id}_xp", 0
                    )
                global_xp = await r.execute("get", f"{message.author.id}_xp")
                if not global_xp:
                    global_xp = 0
                    await r.execute("set", f"{message.author.id}_xp", 0)
                return {
                    "xp_last_added": last_added,
                    "guild_xp": int(guild_xp),
                    "global_xp": int(global_xp),
                }
            else:
                return False

    async def get_pg_user_info(self, message):
        async with self.bot.pool.acquire() as db:
            user_info = await db.fetchrow(
                "SELECT xp_last_added, xp FROM botsettings_user WHERE id=$1",
                message.author.id,
            )
            if user_info is None:
                await add_user(self.bot.pool, message.author)
                last_added = datetime.now(timezone.utc)
                return {"xp_last_added": last_added, "guild_xp": 0, "global_xp": 0}
            else:
                guild_xp = await db.fetchval(
                    "SELECT xp FROM botsettings_guildlevel WHERE member_id=$1 AND guild_id=$2",
                    message.author.id,
                    message.guild.id,
                )
                if guild_xp is None:
                    await add_guild_level(self.bot.pool, message.guild, message.author)
                    guild_xp = 0
                async with self.bot.redis_pool.get() as r:
                    await r.execute(
                        "set",
                        f"{message.author.id}_xp_last_added",
                        user_info["xp_last_added"].isoformat(),
                    )
                    await r.execute(
                        "set", f"{message.guild.id}{message.author.id}_xp", guild_xp
                    )
                    await r.execute("set", f"{message.author.id}_xp", user_info["xp"])
                return {
                    "xp_last_added": user_info["xp_last_added"],
                    "guild_xp": guild_xp,
                    "global_xp": user_info["xp"],
                }

    async def update_xp(self, message, user_info, add_xp):
        async with self.bot.pool.acquire() as db:
            await db.execute(
                "UPDATE botsettings_user SET xp=$1, xp_last_added=$2 WHERE id=$3",
                user_info["global_xp"] + add_xp,
                datetime.now(timezone.utc),
                message.author.id,
            )
            await db.execute(
                "UPDATE botsettings_guildlevel SET xp=$1 WHERE guild_id=$2 AND member_id=$3",
                user_info["guild_xp"] + add_xp,
                message.guild.id,
                message.author.id,
            )
        async with self.bot.redis_pool.get() as r:
            await r.execute(
                "set",
                f"{message.guild.id}{message.author.id}_xp",
                user_info["guild_xp"] + add_xp,
            )
            await r.execute(
                "set", f"{message.author.id}_xp", user_info["global_xp"] + add_xp
            )
            await r.execute(
                "set",
                f"{message.author.id}_xp_last_added",
                datetime.now(timezone.utc).isoformat(),
            )

    @commands.group(name="levelroles", aliases=["levelrole, lvlrole, lvlroles"])
    async def levelroles(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send(
                "Commands\n"
                "furlevelrole <add|delete|list>\n"
                "Usage: furlevelrole add 5 somekindofdiscordrole"
            )

    @levelroles.command()
    @commands.has_permissions(manage_guild=True)
    async def add(self, ctx, level, role: discord.Role):
        async with self.bot.pool.acquire() as db:
            existing = await db.fetchval(
                "SELECT role FROM botsettings_levelrole WHERE guild_id=$1 AND level=$2",
                ctx.guild.id,
                int(level),
            )
            if existing:
                existing_role = ctx.guild.get_role(existing)
                return await ctx.send(
                    f"You already have a role for level {level}, it's {existing_role.name}! "
                    "Delete that first if you want to replace it."
                )
            await db.execute(
                "INSERT INTO botsettings_levelrole (guild_id, level, role) VALUES ($1, $2, $3)",
                ctx.guild.id,
                int(level),
                role.id,
            )
            await ctx.send(
                f"Done! Members who reach level {level} and up will now get the {role.name} role."
            )

    @levelroles.command()
    @commands.has_permissions(manage_guild=True)
    async def delete(self, ctx, level):
        try:
            int(level)
        except ValueError:
            return await ctx.send(
                "You have to give the level **number** of the role. If you need that info, do `furlevelroles list`!"
            )
        
        async with self.bot.pool.acquire() as db:
            existing = await db.fetchval(
                "SELECT role FROM botsettings_levelrole WHERE guild_id=$1 AND level=$2",
                ctx.guild.id,
                int(level),
            )
            if existing:

                def pred(m):
                    return m.author == ctx.author

                await ctx.send(
                    f"Are you sure you want to delete the level {level} role reward?\n`Yes` or `No`"
                )
                while True:
                    answer = await self.bot.wait_for("message", check=pred)

                    if answer:
                        if answer.content.lower() == "no":
                            return await ctx.send("Got it, we'll keep it then.")

                        elif answer.content.lower() == "yes":
                            await db.execute(
                                "DELETE FROM botsettings_levelrole WHERE guild_id=$1 AND level=$2",
                                ctx.guild.id,
                                int(level),
                            )
                            await ctx.send(
                                f"Done! You can now add a new role to give at level {level} if you'd like."
                            )

                            break
                        else:
                            return await ctx.send("Invalid response! Try again")

    @levelroles.command()
    @commands.has_permissions(manage_guild=True)
    async def list(self, ctx):
        async with self.bot.pool.acquire() as db:
            level_roles = await db.fetch(
                "SELECT level, role FROM botsettings_levelrole WHERE guild_id=$1",
                ctx.guild.id,
            )
            if level_roles:
                paginator = commands.Paginator()
                paginator.add_line("**LEVEL - ROLE**")
                for row in level_roles:
                    role = ctx.guild.get_role(row["role"])
                    if not role:
                        role = "Deleted Role (replace me!)"
                    else:
                        role = role.name
                    paginator.add_line(f"{row['level']} - {role}")
                for page in paginator.pages:
                    await ctx.send(page)
            else:
                await ctx.send("This server doesn't have any level roles set up!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetallguildlevels(self, ctx):
        def pred(m):
            return m.author == ctx.author

        await ctx.send("Are you sure? **This cannot be undone!**")
        answer = await self.bot.wait_for('message', check=pred)
        if not answer.content.lower() == 'yes':
            return await ctx.send("Okay, cancelling")
        await ctx.send("Are you REALLY SURE?")
        answer = await self.bot.wait_for('message', check=pred)
        if not answer.content.lower() == 'yes':
            return await ctx.send("Okay, cancelling")
        await ctx.send("Okay, deleting all level data. Give me a moment...")
        async with ctx.channel.typing():
            async with self.bot.pool.acquire() as db:
                msg = await db.execute("DELETE FROM botsettings_guildlevel WHERE guild_id=$1", ctx.guild.id)
        await ctx.send(f"{msg}\nDone! Guild levels are reset. Everybody is back to level 0 with no XP.")

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.guild is not None:
                if message.author.bot:
                    return
                ctx = await self.bot.get_context(message)

                # Get info from Redis, or the PostgresQL DB / defaults if not in Redis
                try:
                    user_info = await self.get_redis_user_info(message)
                    if not user_info:
                        user_info = await self.get_pg_user_info(message)
                except Exception as e:
                    self.bot.sentry.capture_exception(e)
                    raise Exception(e)

                # Check if it's been over 2 minutes since last XP given, then proceed
                now = datetime.now(timezone.utc)
                last_added = user_info["xp_last_added"]
                try:
                    if now > last_added + timedelta(minutes=+1):
                        add_xp = randint(10, 20)
                        current_guild_level = self._get_level_from_xp(user_info["guild_xp"])
                        await self.update_xp(message, user_info, add_xp)
                        new_guild_level = self._get_level_from_xp(
                            user_info["guild_xp"] + add_xp
                        )

                        # Check if user has leveled up
                        if new_guild_level > current_guild_level:
                            async with self.bot.pool.acquire() as db:
                                guild_info = await db.fetchrow(
                                    "SELECT levels_message, levels_announce FROM "
                                    "botsettings_guild WHERE id=$1",
                                    message.guild.id,
                                )
                                if not guild_info:
                                    return

                                try:
                                    _ = message.author.guild
                                except AttributeError:
                                    return
                                
                                formatted_message = await parse_level_vars(
                                    message.author,
                                    new_guild_level,
                                    guild_info["levels_message"],
                                )

                                # Role level rewards check
                                guild_level_roles = await db.fetch(
                                    "SELECT level, role FROM botsettings_levelrole WHERE guild_id=$1",
                                    ctx.guild.id,
                                )
                                applicable_roles = []
                                for row in guild_level_roles:
                                    if row["level"] <= new_guild_level:
                                        try:                                            
                                            level_role = ctx.guild.get_role(row["role"])
                                            applicable_roles.append(level_role)
                                        except Exception as e:
                                            await ctx.guild.owner.send(
                                                f"Uh oh! I tried to give {ctx.author} a role for"
                                                f"leveling up, but it didn't work!(\n\n"
                                                f"Please double-check your level roles\n\n"
                                                f"Role ID: {row['role']} (level {row['level']}"
                                            )
                                            pass
                                try:
                                    await ctx.author.add_roles(
                                        *applicable_roles,
                                        reason="Level {new_guild_level} reward",
                                    )
                                except (discord.errors.Forbidden, AttributeError):
                                    pass
                                if guild_info["levels_announce"] and formatted_message:
                                    try:
                                        await ctx.send(formatted_message, delete_after=10)
                                    except discord.errors.Forbidden:
                                        pass
                except TypeError as e:
                    self.bot.sentry.capture_exception(e)
                    await self.update_xp(message, user_info, 0)
        except Exception as e:
            self.bot.sentry.capture_exception(e)


def setup(bot):
    bot.add_cog(Levels(bot))
