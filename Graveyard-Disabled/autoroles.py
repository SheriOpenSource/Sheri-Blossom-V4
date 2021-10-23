import discord
from discord.ext import commands


class Autoroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx):
        pass

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, role: discord.Role):
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
                    f"{role.name} has been added to the autorole list for this guild."
                )

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, role: discord.Role):
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
                    f"{role.name} has been removed from the autorole list for this guild."
                )
            else:
                return await ctx.send("That role isn't in the autorole list!")

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def list(self, ctx):
        async with self.bot.pool.acquire() as db:
            autorole_list = await db.fetchval(
                "SELECT autoroles FROM botsettings_guild WHERE id=$1", ctx.guild.id
            )
            mapped_list = [role for role in ctx.guild.roles if role.id in autorole_list]
            return await ctx.send(
                f"Autoroles for this guild are:\n{', '.join([role.name for role in mapped_list])}"
            )

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def bot(self, ctx, role: discord.Role):
        async with self.bot.pool.acquire() as db:
            await db.execute(
                "UPDATE botsettings_guild SET botautorole=$1 WHERE id=$2",
                role.id,
                ctx.guild.id,
            )
            return await ctx.send(f"Bot autorole has been set to {role.name}")

    @autorole.command()
    @commands.has_permissions(administrator=True)
    async def toggle(self, ctx, what, state):
        command_error_text = (
            "Whoops! I didn't understand that, use this format:\n"
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
            f"Done! {what.title()} autoroles are now {'enabled' if state is True else 'disabled'}"
        )


def setup(bot):
    bot.add_cog(Autoroles(bot))
