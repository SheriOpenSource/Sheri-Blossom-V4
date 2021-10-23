from dataclasses import dataclass
from datetime import datetime, timedelta

import discord

from Functions.ctx import CustomContext
from Functions.time import parse_time


@dataclass
class Reminders:
    ctx: CustomContext

    async def add(self, location: int, expires: str, reminder: str):
        ctx = self.ctx
        expires_timestamp = parse_time(expires)
        if not expires:
            return await ctx.send("Please use a valid time format, like '30m'")
        await ctx.pool.execute("""INSERT INTO botsettings_reminders (user_id, channel_id, expires, expired, reminder)
                                VALUES ($1, $2, $3, 'f', $4)""",
                               ctx.author.id,
                               location,
                               expires_timestamp,
                               reminder
                               )

    @staticmethod
    async def check(bot):
        reminders = await bot.pool.fetch(
            "SELECT * FROM botsettings_reminders WHERE NOT expired AND expires <= now()"
        )
        bot.log.info(f"[Reminders Manager] - Gathered {len(reminders)} and checking if they expired.")
        for reminder in reminders:
            bot.log.info(f"[Reminders Manager] - Reminder #{reminder['id']} expired")
            await bot.pool.execute("UPDATE botsettings_reminders SET expired=True WHERE id=$1", reminder["id"])
            author = bot.get_user(reminder["user_id"])
            channel = bot.get_channel(reminder["channel_id"])
            to_send = f"**Reminder** {author.mention}: {reminder['reminder']}"
            if channel:
                try:
                    return await channel.send(to_send)
                except (discord.Forbidden, discord.HTTPException):
                    to_send += "\n*Failed to send to channel*"
            try:
                await author.send(to_send)
            except (discord.Forbidden, discord.HTTPException):
                return

    async def list(self):
        ctx = self.ctx
        reminders = await ctx.pool.fetch(
            "SELECT * FROM botsettings_reminders WHERE NOT expired AND user_id=$1",
            ctx.author.id
        )
        return reminders

    async def delete(self, reminder_id: int):
        ctx = self.ctx
        deleted = await ctx.pool.execute(
            "UPDATE botsettings_reminders SET expired=null WHERE id=$1 AND user_id=$2",
            reminder_id,
            ctx.author.id
        )
        return deleted
