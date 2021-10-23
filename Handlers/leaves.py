from datetime import datetime

import discord
from discord.ext import commands

from Database.transactions import update_persistent_roles
from Formats.formats import avatar_check, icon_check
from Functions.logging import Logging
from Lines.custom_emotes import logging_emotes


class Leaves(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not self.bot.is_ready():
            return
        try:
            await update_persistent_roles(self.bot.pool, member)
            guild_data = await Logging.log_channel(self, "member_channel", member.guild)
            log_channel = guild_data[0]
            embed_enabled = guild_data[1]
            if log_channel:
                description = (
                    f"Username: **{member}**\n"
                    f"Display Name: **{member.display_name}**\n"
                    f"User ID: **{member.id}**\n"
                )
                if embed_enabled:
                    embed = discord.Embed(
                        title="A member has Left!",
                        timestamp=datetime.utcnow(),
                        description=description,
                    )
                    embed.set_author(
                        name=member.display_name, icon_url=avatar_check(member)
                    )
                    embed.set_thumbnail(url=avatar_check(member))
                    await log_channel.send(embed=embed)
                else:
                    await log_channel.send(
                        content=f"{logging_emotes['memberleave']} {'🤖' if member.bot else '👤'}"
                                f"**{member}**(``{member.id}``) has left the server.\n"
                    )
        except (AttributeError, discord.HTTPException, discord.Forbidden):
            return
        except Exception as e:
            self.bot.sentry.capture_exception(e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if not self.bot.is_ready():
            return
        self.bot.counter["guild_leave"] += 1
        home = self.bot.get_guild(346892627108560901)
        channel = home.get_channel(612293479577681971)
        # async with self.session as session:
        # webhook = discord.Webhook.from_url(
        #   "https://discordapp.com/api/webhooks/612293509856362526/QRE-G9IXFPQPfWvAa4SNiF-me2aGl_RmrH0KqDJxjlscNeOHCnI9NHoTp8epvuw_uk3D",
        #    adapter=discord.AsyncWebhookAdapter(session),
        # )
        # Embed in Sheri Discord
        member_members = len([member for member in guild.members if not member.bot])
        bot_members = len([member for member in guild.members if member.bot])
        bot_percentage = round(bot_members / guild.member_count * 100)

        embed = discord.Embed(
            title="Left a guild",
            timestamp=datetime.utcnow(),
            color=self.bot.danger_color,
        )
        embed.add_field(
            name="Guild info",
            value=f"**Name:** {guild.name}\n"
                  f"**ID:** {guild.id}\n"
                  f"**Owner:** {guild.owner.mention} ({guild.owner})\n"
                  f"**Users | Bots:** {member_members} | {bot_members} ({bot_percentage}% bots)",
            inline=False,
        )
        embed.add_field(
            name="Bot stats",
            value=f"**Guilds:** {len(self.bot.guilds)}\n"
                  f"**Users:** {len(set(self.bot.users))}",
            inline=False,
        )
        embed.set_thumbnail(url=icon_check(guild))
        try:
            print(f"[Guilds] - Left {guild.name}(Owner: {guild.owner}).")
        except ValueError as e:
            self.bot.sentry.capture_exception(e)
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Leaves(bot))
