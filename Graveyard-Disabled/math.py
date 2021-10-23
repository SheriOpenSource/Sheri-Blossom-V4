from discord.ext import commands


# NOTE: These are expressions that can be used in exp parameter
# i.e: "sqrt(25)"
# Do Not Remove if you want in Scientific Math!
###################################################################
###################################################################

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="math", aliases=["cal"])
    async def mathx(self, ctx, *, exp: str = None):
        if ctx.invoked_subcommand is None:
            if exp is None:
                await ctx.send("No expression provided")
            else:
                problem = list(exp)

                if "^" in problem:
                    problem = [s.replace("^", "**") for s in problem]
                if "!" in problem:
                    problem = [s.replace("!", "factorial") for s in problem]
                if "x" in problem or "X" in problem:
                    problem = [s.replace("x", "*") for s in problem]
                    problem = [s.replace("X", "*") for s in problem]

                exp = "".join(problem)

                x = eval(exp)

                await ctx.send(f"**```ini\n[{x}]```**")

    @mathx.error
    async def mathx_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            return await ctx.send("Error or Can't divide by 0")


def setup(bot):
    bot.add_cog(Math(bot))
