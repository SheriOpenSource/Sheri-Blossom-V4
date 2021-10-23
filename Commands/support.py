import discord
from discord.ext import commands

from Formats.chat_markdown import bold

recievers = [
    493308716427509761,
    83006253919375360,
    139800365393510400,
    106511913222955008,
    406707961214402568,
]


class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ####################################################################################################################
    #                                       Reporting Commands                                                         #
    ####################################################################################################################

    @commands.group(name="report")
    async def report_index(self, ctx):
        """Report things to my devs"""
        if ctx.invoked_subcommand is None:
            em = discord.Embed(
                color=self.bot.color,
                description="Report something that is off or needs attention\n"
                            "content, bug, support, suggestion",
            )
            await ctx.send(embed=em)

    @report_index.command(name="content")
    async def content_report(self, ctx, url: str = None, *, reason: str = None):
        """Report Some images that accidentally slipped through our fingers."""
        if url is None:
            return await ctx.send(
                "Please provide me with the url of the image you want to report"
            )
        if reason is None:
            return await ctx.send(
                "Please provide me with the reason for reporting this image to us."
            )
        if ctx.confirm:
            url_split = url.split("/")
            name = url_split[-1]
            embed = discord.Embed(
                color=self.bot.color, title="Content report", description=reason
            )
            embed.add_field(
                name="Additional information",
                value=f"Server: {bold(ctx.guild.name)}({ctx.guild.id})\n"
                      f"Server Owner: {bold(ctx.guild.owner)}({ctx.guild.owner.id})\n"
                      f"Reporter: {bold(ctx.author)}({ctx.author.id})\n"
                      f"Channel: {bold('#' + ctx.channel.name)}({ctx.channel.id})\n"
                      f"File Name: {bold(name)}\n"
                      f"URL: {bold(url)}",
            )
            for x in recievers:
                user = self.bot.get_user(x)
                try:
                    await user.send(embed=embed)
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    return await ctx.send(
                        "You must insert a URL "
                        "followed by the reason for reporting. Your message has not been sent."
                    )
            await ctx.send(
                "Thank you for you report! We deeply appreciate your efforts to help improve me! "
                "Want to see updates or say hello to the people who make me run?\n"
                f"Consider joining our server located here {bold('<https://invite.sheri.bot/>')}"
            )

    @report_index.command(name="bug")
    async def bug_report(self, ctx, *, reason: str = None):
        """Report bugs"""
        if reason is None:
            return await ctx.send(
                "Please provide me with a reason/statement "
                "for reporting this and try to be detailed as possible."
            )
        embed = discord.Embed(
            color=self.bot.color, title="Bug Report", description=reason
        )
        embed.add_field(
            name="Additional Information",
            value=f"Server: {bold(ctx.guild.name)}({ctx.guild.id})\n"
                  f"Server Owner: {bold(ctx.guild.owner)}({ctx.guild.owner.id})\n"
                  f"Reporter: {bold(ctx.author)}({ctx.author.id})\n"
                  f"Channel: {bold('#' + ctx.channel.name)}({ctx.channel.id})\n",
        )

        for x in recievers:
            user = self.bot.get_user(x)
            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                return await ctx.send(
                    "You must insert a URL "
                    "followed by the reason for reporting. Your message has not been sent."
                )
        await ctx.send(
            "Thank you for helping making me better! "
            "Want to see updates and or meet/hangout with the people who make me run?\n"
            f"Consider joining out server located here {bold('<https://invite.sheri.bot/>')}"
        )

    @report_index.command(name="respond", hidden=True)
    async def respond(self, ctx, user_id: str, *, message: str):
        """Respond to people."""
        guild = self.bot.get_guild(346892627108560901)
        authorized_users = [
            member.id
            for member in discord.utils.get(guild.roles, id=692569963042439208).members
        ]
        if ctx.author.id in authorized_users:
            if ctx.guild.id == guild.id:
                staff_member = ctx.author
                if user_id.isdigit():
                    user_id = self.bot.get_user(int(user_id))
                else:
                    return await ctx.send("Must be a valid user id.")
                embed = discord.Embed(
                    color=self.bot.color, title="Staff Response", description=message
                )
                embed.set_author(name=staff_member, icon_url=staff_member.avatar_url)
                embed.set_thumbnail(url=self.bot.user.avatar_url)
                embed.add_field(
                    name="Thank you.",
                    value="For further support or assistance, or reporting bugs, "
                          "please join our support server located [here](https://invite.sheri.bot/)",
                )
                embed.set_footer(text="<3")
                await user_id.send(embed=embed)
                await ctx.send(f"Successfully sent the message to **{user_id}**")
            else:
                await ctx.send("Only allowed to be used on our support server.")
        else:
            await ctx.send("Haha You're funny. This is a **STAFF ONLY** Command.")

    @commands.command(name="troubleshoot")
    async def permissions(self, ctx):
        await ctx.send(
            "Please follow these steps before requesting more help.\n"
            "It appears that your problem evolves around permission misconfiguration.\n"
            "In order for sheri to work, eaither give her full administrator permissions or the following permissions\n"
            "```fix\n"
            "MANAGE_MESSAGES, MANAGE_ROLES, KICK_MEMBERS, BAN_MEMBERS, CHANGE_NICKNAME,"
            " MANAGE_NICKNAMES, READ TEXT_CHANNELS & SEE VOICE CHANNELS,"
            "SEND MESSAGES, EMBED_LINKS, ATTACH_FILES, USE_EXTERNAL_EMOJIS, ADD_REACTIONS, CONNECT, SPEAK```\n"
            "If you are still having a problem, You need to ensure that sheri can modify the roles that YOU configure.\n"
            "https://waspy.sheri.bot/LNPC - Sheri's Main Role is The Real Queen. See how it is above all the roles she manages on our support server?\n"
            "If you still have problems please mention staff after this."
        )


def setup(bot):
    bot.add_cog(Support(bot))
