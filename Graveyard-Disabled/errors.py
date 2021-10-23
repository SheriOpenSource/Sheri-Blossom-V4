from datetime import timedelta

import discord
from discord.ext import commands

from Checks.bot_checks import can_embed, can_send, can_react


class ErrorHandlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def error_embed(error):
        embed = discord.Embed(
            color=0xDC3545,
            description="<a:bug:474000184901369856> "
                        "Error in processing command! <a:bug:474000184901369856>\n"
                        "```py\n"
                        f"{error}```",
        ).set_image(url="https://dev.sheri.bot/media/command_error.png")
        embed.set_author(
            icon_url="http://myovchev.github.io/sentry-slack/images/logo32.png",
            name="Error, Logged in sentry",
            url="https://sentry.ourmainfra.me/",
        )

        embed.set_footer(
            text="Sheri Blossom, Version: v4.2",
            icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
        )
        return embed

    @staticmethod
    def format_retry_after(retry_after):
        delta = timedelta(seconds=int(round(retry_after, 0)))
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = (
                f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
            )
        elif hours:
            fmt = f"{hours} hours, {minutes} minutes, and {seconds} seconds"
        elif minutes:
            fmt = f"{minutes} minutes and {seconds} seconds"
        else:
            fmt = f"{seconds} seconds"
        return "You can try again in " + fmt

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, discord.ext.commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(str(exception))
        elif isinstance(exception, discord.ext.commands.BadArgument):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(str(exception))
        elif isinstance(exception, discord.ext.commands.CommandNotFound):
            self.bot.log.error(exception)
            return
        elif isinstance(exception, discord.ext.commands.CheckFailure):
            return
        elif isinstance(exception, discord.ext.commands.CommandInvokeError):
            await ctx.send(exception)
        elif isinstance(exception, discord.Forbidden):
            if can_send(ctx):
                return await ctx.send(
                    "Permission error has been detected. This is not my fault but your fault.\n"
                    "In order for me to work as intended, I require the following permissions\n"
                    "```fix\n"
                    "MANAGE_MESSAGES, MANAGE_ROLES, KICK_MEMBERS, BAN_MEMBERS, CHANGE_NICKNAME, "
                    "MANAGE_NICKNAMES, READ TEXT_CHANNELS & SEE VOICE CHANNELS,SEND MESSAGES, "
                    "EMBED_LINKS, ATTACH_FILES, USE_EXTERNAL_EMOJIS, ADD_REACTIONS, CONNECT, SPEAK```\n"
                    "If you are still receiving this message, "
                    "Please make sure that my top role is above the roles you want me to configure."
                )
            else:
                try:
                    if can_react(ctx):
                        await ctx.message.add_reaction("❌")
                    return await ctx.author.send(
                        "Permission error has been detected. This is not my fault but your servers fault.\n"
                        "In order for me to work as intended, I require the following permissions\n"
                        "```fix\n"
                        "MANAGE_MESSAGES, MANAGE_ROLES, KICK_MEMBERS, BAN_MEMBERS, CHANGE_NICKNAME, "
                        "MANAGE_NICKNAMES, READ TEXT_CHANNELS & SEE VOICE CHANNELS,SEND MESSAGES, "
                        "EMBED_LINKS, ATTACH_FILES, USE_EXTERNAL_EMOJIS, ADD_REACTIONS, CONNECT, SPEAK```\n"
                        "If you are still receiving this message, "
                        "Please make sure that my top role is above the roles you want me to configure."
                    )
                except discord.Forbidden:
                    return
        elif isinstance(exception, discord.ext.commands.CommandOnCooldown):
            delta = timedelta(seconds=int(round(exception.retry_after, 0)))
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            if days:
                fmt = f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
            elif hours:
                fmt = f"{hours} hours, {minutes} minutes, and {seconds} seconds"
            elif minutes:
                fmt = f"{minutes} minutes and {seconds} seconds"
            else:
                fmt = f"{seconds} seconds"
            return await ctx.send("You can try again in " + fmt)
        elif isinstance(exception, discord.ext.commands.NoPrivateMessage):
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(
                "This command is only allowed in discord servers, sorry!"
            )
        elif isinstance(exception, discord.ext.commands.CommandError):
            ctx.command.reset_cooldown(ctx)
            self.bot.sentry.capture_exception(exception)
            embed = self.error_embed(exception)
            if isinstance(ctx.channel, discord.TextChannel):
                try:
                    if can_send(ctx) and can_embed(ctx):
                        return await ctx.send(embed=embed)
                    elif can_send(ctx):
                        return await ctx.send(
                            "Oopsie, I have encountered an error, "
                            "This has been logged and my developers will work on it as fast as possible!\n "
                            "If this continues to persist please contact us at "
                            "https://sheri.bot/support"
                        )
                except (discord.Forbidden, discord.HTTPException):
                    return
            elif isinstance(ctx.channel, discord.DMChannel):
                try:
                    await ctx.author.send(embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    return
        else:
            self.bot.sentry.capture_exception(exception)
            self.bot.log.error(exception)
            embed = self.error_embed(exception)
            if isinstance(ctx.channel, discord.TextChannel):
                try:
                    if can_send(ctx) and can_embed(ctx):
                        return await ctx.send(embed=embed)
                    elif can_send(ctx):
                        return await ctx.send(
                            "Oopsie, I have encountered an error, "
                            "This has been logged and my developers will work on it as fast as possible!\n "
                            "If this continues to persist please contact us at "
                            "https://sheri.bot/support"
                        )
                except (discord.Forbidden, discord.HTTPException):
                    return
            elif isinstance(ctx.channel, discord.DMChannel):
                try:
                    await ctx.author.send(embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    return


def setup(bot):
    bot.add_cog(ErrorHandlers(bot))
