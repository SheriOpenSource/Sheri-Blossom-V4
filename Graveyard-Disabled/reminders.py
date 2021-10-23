from discord.ext import commands

from Functions.reminders import Reminders as Reminder
from Functions.text import escape, pagify
from Functions.time import get_relative_delta, parse_time


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(case_insensitive=True)
    async def remind(self, ctx):
        if not ctx.invoked_subcommand:
            commands = ['remind me', 'remind here']
            command_help = ""
            for command in commands:
                comm = self.bot.get_command(command)
                command_help += f"fur**{comm} {comm.signature}**```fix\n{comm.help}```\n"
            await ctx.send(command_help)

    @remind.command(name="me")
    async def remind_me(self, ctx, time: str, *, reminder: str):
        """Reminds You
            Usage: furremind me 1h30 take out the trash = Reminds you in your dms to take out the trash in 1 hour and 30 minutes"""
        if len(reminder) > 1500:
            return await ctx.send_error("That's quite a long reminder... let's slow down a bit!")
        await Reminder(ctx).add(ctx.channel.id, time, reminder)
        # await ctx.send(
        #    f"{ctx.author.mention}, I will remind you about this"
        #    f" {get_relative_delta(parse_time(time), append_small=True, bold_string=True)}"
        # )
        await ctx.send(f"{ctx.author.name}, I will remind you!")

    @remind.command(name="here")
    async def remind_here(self, ctx, time: str, *, reminder: str):
        """Reminds You
            Usage: furremind here 1h30 take out the trash = Reminds you in this channel to take out the trash in 1 hour and 30 minutes"""
        if len(reminder) > 1500:
            return await ctx.send_error("That's quite a long reminder... let's slow down a bit!")
        await Reminder(ctx).add(ctx.channel.id, time, escape(reminder, False, False, False))
        # await ctx.send(
        #    f"{ctx.author.mention}, I will remind you about this"
        #    f" {get_relative_delta(parse_time(time), append_small=True, bold_string=True)}"
        # )
        await ctx.send(f"{ctx.author.name}, I will remind you!")

    @commands.command()
    async def reminders(self, ctx):
        """Lists all the current reminders
            Usage: furreminders"""
        reminders = await Reminder(ctx).list()
        to_send = "**Your reminders:**\n"
        for reminder in reminders:
            if reminder["channel_id"] == ctx.author.id:
                location = "Private Messages"
            else:
                location = f"<#{reminder['channel_id']}>"
            to_send += f"\n**{reminder['id']}**: {location}: \"{reminder['reminder']}\" - {get_relative_delta(reminder['expires'], append_small=True, append_seconds=False)}"
        to_send += f"\n\nRemove a reminder with `{ctx.prefix}delreminder <id>`"
        pages = pagify(to_send)
        for page in pages:
            await ctx.send(page)

    @commands.command(aliases=["delreminder"])
    async def deletereminder(self, ctx, reminder_id: int):
        """Deletes a reminder
            Usage; furdelreminder reminderid"""
        deleted = await Reminder(ctx).delete(reminder_id)
        if deleted == "UPDATE 1":
            return await ctx.send("I have deleted that reminder!")
        await ctx.send_error("Hmm I couldn't seem to find that reminder for you, make sure the id is correct!")


def setup(bot):
    bot.add_cog(Reminders(bot))
