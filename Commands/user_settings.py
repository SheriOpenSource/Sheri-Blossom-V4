import discord
from discord.ext import commands
from Functions.core import commands_help

from Formats.formats import avatar_check


class User_settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="usrsettings", aliases=['usrsetting', 'usrset', 'usersettings', 'usersetting'])
    async def usrsettings_index(self, ctx):
        if ctx.invoked_subcommand is None:
            await commands_help(ctx, ['usrsettings view',
                                      'usrsettings dmcatch',
                                      'usrsettings gender',
                                      'usrsettings orientation'], "furusrsettings")

    @usrsettings_index.command(name='view', aliases=['show', 'information'])
    async def usrsettings_view(self, ctx):
        """Shows the current settings"""
        user_data = await ctx.pool.fetchrow(
            f"SELECT animal_catch_dm, gender, orientation FROM botsettings_user WHERE id={ctx.author.id}")
        feature_on = "<:onswitch:451849951044042802>"
        feature_off = "<:offswitch:451849936531750913>"
        embed = discord.Embed(color=self.bot.color, title=f"{ctx.author.display_name}'s Settings",
                              description=f"Catching DMS: {feature_on if user_data['animal_catch_dm'] else feature_off}\n"
                                          f"Gender: ``{user_data['gender']}``\n"
                                          f"Orientation: ``{user_data['orientation']}``")
        embed.set_thumbnail(url=avatar_check(ctx.author))
        await ctx.send(embed=embed)

    @usrsettings_index.command(name="dmcatch")
    async def usrsettings_catch(self, ctx, toggle: bool):
        """Enables catches being sent to your dms"""
        if toggle:
            await ctx.pool.execute(f"UPDATE botsettings_user SET animal_catch_dm='t' WHERE id={ctx.author.id}")
            await ctx.send("Done <:Sheri_thumpup:604843094869016586>")
        else:
            await ctx.pool.execute(f"UPDATE botsettings_user SET animal_catch_dm='f' WHERE id={ctx.author.id}")
            await ctx.send("Done <:Sheri_thumpup:604843094869016586>")

    @usrsettings_index.command(name="gender")
    async def usrsettings_gender(self, ctx, *, gender: str):
        """Sets your gender in the settings"""
        genders = ["male",
                   "female",
                   "genderfluid",
                   "agender",
                   "non-binary",
                   "transgender",
                   "trangender male",
                   "transgender female"]
        if gender.lower() not in genders:
            return await ctx.send(
                f"``{gender}`` is not a valid gender. The current valid genders are: {', '.join(genders)}")
        await ctx.pool.execute(f"UPDATE botsettings_user SET gender=$1 WHERE id={ctx.author.id}",
                               gender.capitalize())
        await ctx.send("Done <:Sheri_thumpup:604843094869016586>")

    @usrsettings_index.command(name="orientation")
    async def usrsettings_orientation(self, ctx, *, orientation: str):
        """Sets your orientation in the settings"""
        genders = ["asexual",
                   "bisexual",
                   "gay",
                   "lesbian",
                   "pansexual",
                   "straight",
                   "aromantic",
                   ]
        if orientation.lower() not in genders:
            return await ctx.send(
                f"``{orientation}`` is not a valid orientation. The current valid orientations are: {', '.join(genders)}")
        await ctx.pool.execute(f"UPDATE botsettings_user SET orientation=$1 WHERE id={ctx.author.id}",
                               orientation.capitalize())
        await ctx.send("Done <:Sheri_thumpup:604843094869016586>")


def setup(bot):
    bot.add_cog(User_settings(bot))
