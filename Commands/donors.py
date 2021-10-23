import asyncio

import discord
from discord.ext import commands
from API.API import Retrieval as Get
from Checks.checks import donor_check, is_dev
from Commands.guild_settings import sfw_endpoint_list
from Formats.chat_markdown import box
from Functions.core import send_message, endpoint_checker
from Handlers.loops import nsfw_endpoints, sfw_endpoints

nsfw_endpoints_list = " | ".join(nsfw_endpoints)
sfw_endpoints_list = " | ".join(sfw_endpoints)


class Donors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ####################################################################################################################
    #                               Spam Functions
    ####################################################################################################################
    async def build_image(self, image, report_url):
        embed = discord.Embed(
            color=self.bot.color,
            description=f"Image not loading? **[Click here]({image})**\n"
                        f"Something wrong with the image? **[Report it here]({report_url})**",
        )
        embed.set_image(url=image)
        return embed

    # For the sake of repeating my code I am putting this in a function
    async def generate_spam(self, ctx, endpoint, times: str = None, embed: bool = True):
        # check to see if it is a real number and then make sure it isn't greater than 10
        try:
            if times.isdigit() and not int(times) > 10:
                img_text = ""
                # add image counter
                img_count = 1
                # Let the spamming commence
                img_cache = await Get.main_api_multiple(ctx.bot, endpoint, int(times))
                for img in img_cache:
                    if embed:
                        img_embed = await self.build_image(img['url'], img['report_url'])
                        img_embed.set_footer(
                            text=f"Image {img_count}/{times} |"
                                 f" {endpoint} images | User: {ctx.author}"
                        )
                        await send_message(ctx, embed=img_embed)
                        img_count += 1
                        await asyncio.sleep(3.0)
                    else:
                        img_count += 1
                        img_text += img['url'] + "\n"
                        if img_count == 5:
                            await send_message(ctx, message=img_text)
                            await asyncio.sleep(5.0)
                            img_count = 0
                            img_text = ""
            else:
                return await send_message(ctx, message="Please enter a real number and no more than the number 10!")
        except TypeError:
            return await send_message(ctx, message="Nice try, use a real number without excessive zeros!")

    ####################################################################################################################
    #                               Donor Commands
    ####################################################################################################################

    @commands.command()
    async def donate(self, ctx):
        await ctx.send(
            "Yay, another potential donor!\n"
            "Please follow this URL: <https://patreon.sheri.bot/>"
        )

    @commands.command()
    async def donor(self, ctx, member: discord.User = None):
        if member is None:
            member = ctx.author
        async with self.bot.pool.acquire() as db:
            is_donor = await db.fetchval(
                "SELECT premium FROM botsettings_user WHERE id=$1", member.id
            )
        if is_donor:
            return await ctx.send(
                f"**Yes!** {member.mention} is a donor. Thank you so much for supporting my development! :smile:"
            )
        else:
            return await ctx.send(
                f"Nope, it looks like {member.mention} **is not** a donor."
            )

    @commands.command()
    async def donors(self, ctx):
        """ Pulls the current supporters from the current guild """
        donors_text = ""
        donors = await ctx.pool.fetch("SELECT id FROM botsettings_user WHERE premium='t'")
        async with ctx.channel.typing():
            for donor in donors:
                donors_text += f"{await ctx.bot.fetch_user(donor['id'])}, "
            await ctx.send(donors_text)

    @commands.command(aliases=['nspam'])
    @commands.check(donor_check)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def spam(self, ctx, endpoint: str, times: str = "10"):
        """ Spam current channel with endpoints. """
        '''
        if endpoint not in nsfw_endpoints + sfw_endpoints:
           embed = discord.Embed(color=self.bot.color, title="Premium Spamming Command | furspam") \
              .add_field(name="**SFW Endpoints**", value=box(sfw_endpoints_list, lang='fix'), inline=False)
           if ctx.channel.is_nsfw() is False:
               embed.description = "To spam NSFW endpoints, You need to run this command in NSFW channels."
           else:
               embed.add_field(name="**NSFW Endpoints**", value=box(nsfw_endpoints_list, lang='fix'))
           return await send_message(ctx, embed=embed)

        # if endpoint in nsfw_endpoints and ctx.channel.is_nsfw() is False:
        #   return await ctx.send("You can only run NSFW endpoints in NSFW channels!")
        '''
        if await endpoint_checker(ctx, endpoint):
            if ctx.message.content.endswith('--text') or ctx.message.content.endswith('--url'):
                return await self.generate_spam(ctx, endpoint, times, False)
            await self.generate_spam(ctx, endpoint, times)

    ####################################################################################################################
    #                       Guild Primer
    ####################################################################################################################

    @commands.command(name="pgrant", hidden=True)
    @commands.check(is_dev)
    async def grant(self, ctx, amount, *users: discord.User):
        """Grants Premium Charges..."""
        async with self.bot.pool.acquire() as db:
            for user in users:
                transaction = await db.execute(
                    "UPDATE botsettings_user SET premium_count=$1 WHERE id=$2",
                    int(amount),
                    int(user.id),
                )
        await ctx.send("Done!")

    @commands.command(name="charges")
    async def charges(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        async with self.bot.pool.acquire() as db:
            charges = await db.fetchval(
                "SELECT premium_count FROM botsettings_user WHERE id=$1", user.id
            )
        if user.id == ctx.author.id:
            await ctx.send(f"You currently have {charges:,} guild primers.")
        else:
            await ctx.send(
                f"{ctx.author}, **{user.name}** currently has {charges:,} guild primers."
            )

    @commands.command(name="prime")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def guild_primer(self, ctx):
        async with self.bot.pool.acquire() as db:
            charges = await db.fetchval(
                "SELECT premium_count FROM botsettings_user WHERE id=$1", ctx.author.id
            )
            if charges > 0:
                await ctx.send(
                    "By running this command, you will use one of your premium charges to "
                    "make this server a premium enabled server.\n"
                    "Do you wish to proceed?"
                )

                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author

                try:
                    primer = await ctx.bot.wait_for(
                        "message", timeout=60.0, check=check
                    )
                except asyncio.TimeoutError:
                    return await ctx.send("Timed out")
                if primer.content.lower() == "no":
                    await ctx.send("Got it! I won't prime the server.")
                elif primer.content.lower() == "yes":
                    guild = await db.fetchrow(
                        "SELECT premium, premium_owner_id FROM botsettings_guild WHERE id=$1",
                        ctx.guild.id,
                    )
                    if guild["premium"]:
                        primer_name = self.bot.get_user(guild["premium_owner_id"])
                        return await ctx.send(
                            f"Looks like this server was already primed by **{primer_name}** "
                            f"({guild['premium_owner_id']})!\n"
                            f"Thank you for wanting to support the server anyway!\n"
                            f"It's the thought that counts!"
                        )
                    else:
                        await db.execute(
                            "UPDATE botsettings_guild SET premium=$1, premium_owner_id=$2 WHERE id=$3",
                            True,
                            ctx.author.id,
                            ctx.guild.id,
                        )
                        await db.execute(
                            "UPDATE botsettings_user SET premium_count=$1 WHERE id=$2",
                            charges - 1,
                            ctx.author.id,
                        )
                        await ctx.send(
                            f"Hooray! You have successfully primed {ctx.guild.name}.\n"
                            f"Thank you for your support!"
                        )
            else:
                await ctx.send(
                    "Oops! It looks like you don't have any charges to prime this server with!\n"
                    "If you donated on the $10 tier and have not received a charge, please contact my support team. "
                    "They'll be happy to get things sorted out for you!"
                )

    @commands.command(name="deprimer", aliases=["deprime"])
    async def guild_deprimer(self, ctx):
        guild_info = await self.bot.pool.fetchrow("SELECT premium, premium_owner_id FROM botsettings_guild WHERE id=$1",
                                                  ctx.guild.id)
        if guild_info['premium']:
            if ctx.author.id == guild_info['premium_owner_id']:
                await self.bot.pool.execute("UPDATE botsettings_guild SET premium=$2 WHERE $1",
                                            ctx.guild.id, False)
                await ctx.send("I have removed the premium charge from the server. "
                               "Premium functionality has been disabled.")


def setup(bot):
    bot.add_cog(Donors(bot))
