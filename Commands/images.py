import asyncio
import random

import discord
from discord.ext import commands

from API.API import Retrieval as Sheri_Get
from API.ExAPI import External_Retrieval as Get
from API.e621 import e6_search
from Checks.bot_checks import check_nsfw, can_send, can_embed, can_react
from Checks.checks import donor_check
from Formats.formats import avatar_check
from Functions.core import commands_help, send_message
from Functions.dm_sending import send_dm
from Functions.images import ImgFunc
from Functions.reactions import upvote_downvote_reactions
from Handlers.loops import nsfw_endpoints, sfw_endpoints
from Lines.custom_emotes import get as emote
from Lines.valid_endpoints import Endpoints

nsfw_endpoint_list = ", ".join(nsfw_endpoints)
sfw_endpoint_list = ", ".join(sfw_endpoints)


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    async def create_neko_image(self, ctx, endpoint):
        image = await Get.neko_api(self.bot, endpoint)
        embed = discord.Embed(
            color=self.bot.color, description=f"**[Image Link]({image['url']})**"
        )
        embed.set_author(name="nekos.life", url="https://nekos.life")
        embed.set_footer(
            text="If there's an issue with any image, please take it up with the provider."
        )
        embed.set_image(url=image["url"])
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            pass

    async def create_alex_image(self, ctx, endpoint):
        image = await Get.alexflipnote_api(self.bot, endpoint)
        embed = discord.Embed(
            color=self.bot.color, description=f"**[Image Link]({image['file']})**"
        )
        embed.set_author(name="alexflipnote.dev", url="https://alexflipnote.dev")
        embed.set_footer(
            text="If there's an issue with any image, please take it up with the provider."
        )
        embed.set_image(url=image["file"])
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            pass

    async def create_random_image(self, ctx, endpoint):
        image = await Get.some_random_api_img(self.bot, endpoint)
        embed = discord.Embed(
            color=self.bot.color, description=f"**[Image Link]({image['link']})**"
        )
        embed.set_author(
            name="https://some-random-api.ml/", url=" https://some-random-api.ml/"
        )
        embed.set_footer(
            text="If there's an issue with any image, please take it up with the provider."
        )
        embed.set_image(url=image["link"])
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            pass

    async def create_bb_image(self, ctx, endpoint):
        image = await Get.boob_api(self.bot, endpoint)
        embed = discord.Embed(
            color=self.bot.color, description=f"**[Image Link]({image['url']})**"
        )
        embed.set_author(name="boob.bot", url="https://boob.bot")
        embed.set_footer(
            text="If there's an issue with any image, please take it up with the provider."
        )
        embed.set_image(url=image["url"])
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            pass

    async def build_dm_image(self, ctx, endpoint, member: discord.Member):
        image = await Sheri_Get.main_api(self.bot, endpoint)
        embed = discord.Embed(
            color=self.bot.color,
            description=f"No image? **[Click Here]({image['url']})**\n"
                        f"Something wrong with the image? Report it **[Here]({image['report_url']})**\n"
                        f"{image['report_url']}",
        )
        embed.set_image(url=image["url"])
        embed.set_author(name=ctx.author, icon_url=avatar_check(ctx.author))
        try:
            await member.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(
                "Oh no! It looks like they've disallowed DMs from server members, or they may have blocked me :("
            )

    async def send_dm(self, ctx, nsfw, endpoint, member: discord.Member):
        if member.bot:
            return await ctx.send(
                "Sorry, I can't process this command with bots. "
                "Please mention a user instead."
            )

        options = ["yes", "no"]
        send_embed = discord.Embed(
            color=self.bot.color,
            description=f"{ctx.author.mention} is trying to send you an image.",
        )
        send_embed.set_thumbnail(url=avatar_check(ctx.author))
        send_embed.set_author(
            name=f"Endpoint: {endpoint}", icon_url=avatar_check(self.bot.user)
        )
        send_embed.set_footer(
            text="Sheri is proudly powered by: https://furhost.net | Bot Version: v4.3"
        )
        msg = await ctx.send(f"{emote['sheri emotes']['Paws']} Please wait...")
        if nsfw:
            send_embed.add_field(
                name="Image is NSFW",
                value="Do you accept the image?\n"
                      "Valid responses are: ``Yes``, ``No``",
            )
            try:
                await member.send(embed=send_embed)
            except discord.Forbidden:
                return await ctx.send(
                    "I think they have me blocked or are not accepting DMs"
                )
        else:
            send_embed.add_field(
                name="Image is SFW",
                value="Do you accept the image?\n"
                      "Valid responses are: ``Yes``, ``No``",
            )
            try:
                await member.send(embed=send_embed)
            except discord.Forbidden:
                return await ctx.send(
                    "I think they have me blocked or are not accepting DMs"
                )

        def check(m):
            return isinstance(m.channel, discord.DMChannel) and m.author == member

        try:
            response = await ctx.bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            if msg:
                await msg.delete()
            await ctx.send(
                f"I think they are ignoring me or not even there. I tried {ctx.author.name}!"
            )
            return await member.send(
                "You didn't respond in time therefore, you will not receive the image."
            )
        if response.content.lower() not in options:
            try:
                await member.send("You need to tell me yes or no.")
            except discord.Forbidden:
                return await ctx.send(
                    "I think they have me blocked or are not accepting DMs"
                )
        if response.content.lower() == "yes":
            await msg.delete()
            await ctx.send(f"Good job {ctx.author.mention}!")
            await self.build_dm_image(ctx, endpoint, member)
        if response.content.lower() == "no":
            await msg.delete()
            try:
                await member.send(
                    f"Alright, Thank you! Informing {ctx.author.name} now."
                )
            except discord.Forbidden:
                return await ctx.send(
                    "I think they have me blocked or are not accepting DMs"
                )
            await ctx.send(
                content=f"I'm sorry, I tried to deliver {endpoint}, unfortunately they rejected it."
            )

    ####################################################################################################################
    #                               Nekos <3~
    ####################################################################################################################

    @commands.group(name="neko", aliases=["nyaa"])
    async def neko_neko(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send("Please choose from: gif, kitsune, ngif, nsfw, sfw.")

    @neko_neko.command(name="nsfw")
    @commands.check(check_nsfw)
    async def neko_nsfw(self, ctx):
        await self.create_neko_image(ctx, "lewd")

    @neko_neko.command(name="ngif")
    @commands.check(check_nsfw)
    async def neko_ngif(self, ctx):
        await self.create_neko_image(ctx, "nsfw_neko_gif")

    @neko_neko.command(name="sfw")
    async def neko_sfw(self, ctx):
        await self.create_neko_image(ctx, "neko")

    @neko_neko.command(name="gif")
    async def neko_gif(self, ctx):
        await self.create_neko_image(ctx, "ngif")

    @neko_neko.command(name="kitsune")
    async def neko_kitsune(self, ctx):
        await self.create_neko_image(ctx, "fox_girl")

    ####################################################################################################################
    #                               Boobs <3~
    ####################################################################################################################

    @commands.group(name="bb", aliases=["newds", "nudes"])
    @commands.guild_only()
    async def boob_bot(self, ctx):
        if not ctx.invoked_subcommand:
            embed = discord.Embed(color=self.bot.color)
            embed.add_field(
                name="Valid Commands",
                value="bb 4k\n"
                      "bb anal\n"
                      "bb ass\n"
                      "bb bdsm\n"
                      "bb blowjob\n"
                      "bb boobs\n"
                      "bb bottomless\n"
                      "bb dpgirls\n"
                      "bb gay\n"
                      "bb gif\n"
                      "bb lesbian\n"
                      "bb penis\n"
                      "bb pussy\n"
                      "bb red\n"
                      "bb traps\n",
            )
            await ctx.send(embed=embed)

    @boob_bot.command(name="pussy")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_pussy(self, ctx):
        await self.create_bb_image(ctx, "pussy")

    @boob_bot.command(name="boobs")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_boobs(self, ctx):
        await self.create_bb_image(ctx, "boobs")

    @boob_bot.command(name="traps")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_traps(self, ctx):
        await self.create_bb_image(ctx, "traps")

    @boob_bot.command(name="4k")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_4k(self, ctx):
        await self.create_bb_image(ctx, "4k")

    @boob_bot.command(name="red")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_red(self, ctx):
        await self.create_bb_image(ctx, "red")

    @boob_bot.command(name="gif")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_gif(self, ctx):
        await self.create_bb_image(ctx, "Gifs")

    @boob_bot.command(name="lesbian")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_lesbian(self, ctx):
        await self.create_bb_image(ctx, "lesbians")

    @boob_bot.command(name="dpgirls")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_dbgirls(self, ctx):
        await self.create_bb_image(ctx, "dpgirls")

    @boob_bot.command(name="blowjob")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_blowjob(self, ctx):
        await self.create_bb_image(ctx, "blowjob")

    @boob_bot.command(name="bdsm")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_bdsm(self, ctx):
        await self.create_bb_image(ctx, "bdsm")

    @boob_bot.command(name="ass")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_ass(self, ctx):
        await self.create_bb_image(ctx, "ass")

    @boob_bot.command(name="anal")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_anal(self, ctx):
        await self.create_bb_image(ctx, "Gifs")

    @boob_bot.command(name="gay")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_gay(self, ctx):
        await self.create_bb_image(ctx, "gay")

    @boob_bot.command(name="bottomless")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_bottomless(self, ctx):
        await self.create_bb_image(ctx, "bottomless")

    @boob_bot.command(name="penis")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bb_penis(self, ctx):
        await self.create_bb_image(ctx, "penis")

    ####################################################################################################################
    #                               Murrrrr <3~
    ####################################################################################################################

    @commands.command()
    @commands.guild_only()
    async def mur(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'mur')

    @commands.command(aliases=['beans', 'paw'])
    @commands.guild_only()
    async def paws(self, ctx):
        await ImgFunc.sheri_image(self, ctx, 'paws')

    @commands.command(aliases=['maw'])
    @commands.check(check_nsfw)
    @commands.guild_only()
    async def maws(self, ctx):
        await ImgFunc.sheri_image(self, ctx, 'maws')

    ####################################################################################################################
    #                               Yiff <3~
    ####################################################################################################################
    @commands.group(name="yiff", aliases=["lewd", "yiffy"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def yiff(self, ctx):
        if not ctx.invoked_subcommand:
            # noinspection PyCallByClass
            await ImgFunc.sheri_image(self, ctx, 'yiff')

    @commands.command(name="yiffmas")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def yiffmas(self, ctx):
        if not ctx.invoked_subcommand:
            # noinspection PyCallByClass
            await ImgFunc.sheri_image(self, ctx, "christmas")

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bound(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'nbound')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def hug(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'nhug')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def lick(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'nlick')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def cuddle(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'ncuddle')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def kiss(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'nkiss')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def hold(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'nhold')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bang(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'bang')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def suck(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'suck')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def finger(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'finger')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def tease(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'ntease')

    @yiff.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def group(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'ngroup')

    ####################################################################################################################
    #                               Furries <3~
    ####################################################################################################################

    @commands.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def gif(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'gif')

    @commands.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def brony(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'nbrony')

    @commands.command(aliases=['pregnant'])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def preg(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'pregnant')

    @commands.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def gay(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'gay')

    @commands.command(aliases=["femboi", "femboye"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def femboy(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'nfemboy')

    @commands.command(name="dualsuck", aliases=["69"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def dualsuck(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, '69')

    @commands.command(name ="tentacles")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def tentacles(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'tentacles')


    @commands.command(name="dp", aliases=['doublepenetration'])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def doublep(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'dp')

    @commands.command(aliases=["dicks"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def dick(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'dick')

    @commands.command(aliases=["vagina"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def pussy(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'pussy')

    @commands.command(aliases=['boobs'])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def boob(self, ctx):
        """Shows Boobies"""
        await ImgFunc.sheri_image(self, ctx, 'boob')

    @commands.command(aliases=["booty, butt"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def ass(self, ctx):
        """Shows booties"""
        await ImgFunc.sheri_image(self, ctx, 'booty')

    @commands.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def lesbian(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'lesbian')

    @commands.command(aliases=["bi"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def bisexual(self, ctx):
        # noinspection PyCallByClass
        endpoints = ['fsolo', 'msolo', 'ftease', 'mtease', 'fseduce', 'mseduce']
        await ImgFunc.sheri_image(self, ctx, random.choice(endpoints))

    @commands.command(aliases=["futas"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def futa(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'nfuta')

    @commands.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def solo(self, ctx, option: str = 'r'):
        """Returns solo images"""
        options = ['r', 'f', 'm']
        if option not in options:
            if can_send(ctx):
                return await ctx.send("That isn't a valid option. The currently acceptable options are```fix\n"
                                      "f: Female | m: Male | r: random```")
        if option == 'f':
            await ImgFunc.sheri_image(self, ctx, 'fsolo')
        if option == 'm':
            await ImgFunc.sheri_image(self, ctx, 'msolo')
        if option == "r":
            endpoints = ['fsolo', 'msolo', 'nsolo']
            await ImgFunc.sheri_image(self, ctx, random.choice(endpoints))

    @commands.command(aliases=["comic"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def ncomic(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'ncomics')

    @commands.command(aliases=["npokeporn"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def npokemon(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'npokemon')

    @commands.command(aliases=["traps"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def trap(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'ntrap')

    @commands.command(aliases=["cuntboi", "cuntboye"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def cuntboy(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'cuntboy')

    @commands.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def fcreampie(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'fcreampie')

    @commands.command()
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def mcreampie(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'mcreampie')

    @commands.command(aliases=["cuminflation"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def cumflation(self, ctx):
        await ImgFunc.sheri_image(self, ctx, "cumflation")

    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(name="snp")
    async def snp(self, ctx, channel: discord.TextChannel = None, endpoint: str = None):
        if channel is None:
            channel = ctx.channel
        if channel.is_nsfw():
            sheri_api = None
            if endpoint is None:
                sheri_api = await Sheri_Get.main_api(self.bot, "yiff")
            elif endpoint in nsfw_endpoints and not None:
                if endpoint:
                    sheri_api = await Sheri_Get.main_api(self.bot, endpoint)
            else:
                return await ctx.send(
                    "Whoops! That's an invalid endpoint. Valid endpoints are:\n"
                    "```fix\n"
                    f"{', '.join(nsfw_endpoints)}```"
                )
            embed = discord.Embed(
                color=self.bot.color,
                title="Smash or Pass?",
                description="React with a <:Upvote:523277460624769025> for smash\n"
                            "React with a <:Downvote:523277460637351951> for pass",
            )
            embed.set_image(url=sheri_api["url"])
            msg = await channel.send(embed=embed)
            await upvote_downvote_reactions(channel, msg)
        else:
            await ctx.send(
                "Oh no! It appears that this channel is not NSFW."
                " If you want to do smash or passes, the channel must be marked NSFW. "
                "Server staff with the `Manage Channels` permission can run `furnsfw` to "
                "quickly toggle this channel setting."
            )

    ####################################################################################################################
    #                                               e621/e926
    ####################################################################################################################

    @commands.command(aliases=["e6"])
    @commands.guild_only()
    @commands.check(check_nsfw)
    # @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 5, commands.BucketType.user)
    # This is coded that no matter NSFW/SFW channel Sheri can easily detect it based on the flag!
    async def e621(self, ctx, *, tag: str = None):
        user = ctx.author
        flag = "e6"
        msg = None
        if can_send(ctx):
            msg = await ctx.send(f"Contacting e621 API standby...")
        if msg is not None:
            try:
                if can_embed(ctx):
                    await e6_search(self, ctx, user, tag, flag)
                    await msg.delete()
                else:
                    await ctx.send(
                        "Oh dear, it seems that this channel doesn't allow me the "
                        "`Embed Links` permission. Please fix it :)"
                    )
            except discord.Forbidden:
                await ctx.send(
                    "I attempted to add/remove reactions. Please ensure that I can manage reactions :)"
                )
            except discord.NotFound:
                pass

    @commands.command(aliases=["e9"])
    @commands.guild_only()
    async def e926(self, ctx, *, tag: str = None):
        return await ctx.send("e926 changed the way their API works. We are working to resolve it.")
        user = ctx.author
        flag = "e9"
        msg = await ctx.send(f"Contacting e926 API standby...")
        try:
            if can_embed(ctx):
                await e6_search(self, ctx, user, tag, flag)
                await msg.delete()
            else:
                await ctx.send(
                    "Oh dear, it seems that this channel doesn't allow me "
                    "the `Embed Links` permission. Please fix it :)"
                )
        except discord.Forbidden:
            await ctx.send(
                "I attempted to add/remove reactions. Please ensure that I can manage reactions :)"
            )

    ###################################################################################################################
    #                                              Animals
    ###################################################################################################################

    @commands.command(name="duck", aliases=["quack"])
    async def quackers(self, ctx):
        duck_choices = ["?type=jpg", "?type=gif"]
        verdict = random.choice(duck_choices)
        image = await Get.duck_api(self.bot, verdict)
        embed = discord.Embed(
            color=discord.Colour.green(),
            title="Ducks!",
            description=f"No Image? [Click Me]({image['url']})\n"
                        "Powered by random-d.uk",
        )
        embed.set_image(url=image["url"])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def nature(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'nature')

    @commands.command(aliases=["wuf", "wolves"])
    @commands.guild_only()
    async def wolf(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'wolves')

    @commands.command(aliases=["huskies", "huskys"])
    @commands.guild_only()
    async def husky(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'husky')

    @commands.command()
    @commands.guild_only()
    async def shiba(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'shiba')

    @commands.command(aliases=["oink"])
    @commands.guild_only()
    async def pig(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'pig')

    @commands.command(aliases=["foxes"])
    @commands.guild_only()
    async def fox(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'fox')

    @commands.command(name="cat")
    @commands.guild_only()
    async def cat(self, ctx):
        await ImgFunc.sheri_image(self, ctx, 'cat')

    @commands.command(aliases=["gobble"])
    @commands.guild_only()
    async def turkey(self, ctx):
        await ImgFunc.sheri_image(self, ctx, 'turkey')

    @commands.command(aliases=["bun", "bunnie"])
    @commands.guild_only()
    async def bunny(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'bunny')

    @commands.command(aliases=["sneps"])
    @commands.guild_only()
    async def snep(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.sheri_image(self, ctx, 'snep')

    #@commands.command(aliases=["turt"])
    @commands.guild_only()
    async def turtle(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.here_is_code_img(self, ctx, "turtle")

    @commands.group(invoke_without_command=True, case_insensitive=True, description="Random cats!")
    async def meow(self, ctx, *, breed: str = None):
        """{"user": [], "bot": ["embed_links"]}"""
        if not ctx.invoked_subcommand:
            image, name, details = await Get.cat(self.bot, breed)
            if not image:
                return await ctx.send("That's an invalid breed! You can use the `breeds`"
                                      " argument to double check the list of available breeds.")
            em = discord.Embed(color=self.bot.color, description=details)
            em.set_author(name=name)
            em.set_image(url=image)
            await ctx.send(embed=em)

    @meow.command(name="breeds", description="List the available cat breeds!")
    async def meow_breeds(self, ctx, page: int = 1):
        """{"user": [], "bot": ["embed_links"]}"""
        em = discord.Embed(color=self.bot.color)
        pages, breed_count = await Get.cat_breeds(self.bot)
        if page > len(pages):
            return await ctx.send("There aren't that many pages!")
        em.description = pages[page - 1]
        em.set_author(name=f"There are currently {breed_count} breeds to chose from!")
        em.set_footer(text=f"Page: {page}/{len(pages)}")
        await ctx.send(embed=em)

    @commands.group(invoke_without_command=True, case_insensitive=True, description="Random dogs!")
    async def woof(self, ctx, *, breed: str = None):
        """{"user": [], "bot": ["embed_links"]}"""
        if not ctx.invoked_subcommand:
            image, name, details = await Get.dog(self.bot, breed)
            if not image:
                return await ctx.send("Invalid breed!")
            em = discord.Embed(color=self.bot.color, description=details)
            em.set_author(name=name)
            em.set_image(url=image)
            await ctx.send(embed=em)

    @woof.command(name="breeds", description="List the available dog breeds!")
    async def woof_breeds(self, ctx, page: int = 1):
        """{"user": [], "bot": ["embed_links"]}"""
        em = discord.Embed(color=self.bot.color)
        pages, breed_count = await Get.dog_breeds(self.bot)
        if page > len(pages):
            return await ctx.send("There aren't that many pages!")
        em.description = pages[page - 1]
        em.set_author(name=f"There are currently {breed_count} breeds to chose from!")
        em.set_footer(text=f"Page: {page}/{len(pages)}")
        await ctx.send(embed=em)

    @commands.command(name="birb")
    async def alex_birb(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.alex_image(self, ctx, "birb")

    # @commands.group(name="panda")
    async def random_panda(self, ctx):
        if not ctx.invoked_subcommand:
            # noinspection PyCallByClass
            await ImgFunc.random_image(self, ctx, "panda")

    # @random_panda.command(name="red")
    async def random_panda_red(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.random_image(self, ctx, "red_panda")

    # @commands.command(name="koala")
    async def random_koala(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.random_image(self, ctx, "koala")

    # @commands.command(name="raccoon", aliases=["racoon"])
    async def random_raccoon(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.random_image(self, ctx, "racoon")

    @commands.command(name="sadcat")
    async def sadcat(self, ctx):
        # noinspection PyCallByClass
        await ImgFunc.alex_image(self, ctx, "sadcat")

    ####################################################################################################################
    #                       SFW DM SENDING
    ####################################################################################################################

    @commands.max_concurrency(2, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(name="send")
    async def dm_sending(self, ctx, content: str, member: discord.Member):
        if member.bot:
            return await send_message(ctx, message="You can't send images to a bot :)")
        endpoint_check = Endpoints.check_endpoint(content, ctx.channel.is_nsfw())
        if endpoint_check[0]:
            await send_dm(self, ctx, True if endpoint_check[1] == "NSFW" else False, content, member)
        if endpoint_check[1] == "unknown":
            valid_endpoints = Endpoints.list_endpoints(True, True)
            embed = discord.Embed(color=ctx.color,
                                  description=endpoint_check[2])
            embed.add_field(name="**SFW ENDPOINTS**", value=valid_endpoints[0], inline=False)
            if ctx.channel.is_nsfw():
                embed.add_field(name="**NSFW ENDPOINTS**", value=valid_endpoints[1], inline=True)
            await ctx.send(f"The endpoint {content} is invalid. Here are the endpoints you can use:", embed=embed)
        if endpoint_check[1] == "error":
            valid_endpoints = Endpoints.list_endpoints(True, False)
            embed = discord.Embed(color=ctx.color,
                                  description=endpoint_check[2])
            embed.add_field(name="**SFW ENDPOINTS**", value=valid_endpoints, inline=False)
            await ctx.send(f"Nope! This endpoint can't be used in an SFW channel!", embed=embed)

    ####################################################################################################################
    #                                NSFW DM SENDING
    ####################################################################################################################
    @commands.cooldown(4, 10, type=commands.BucketType.user)
    @commands.command(name="nsend")
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def n_send(self, ctx):
        return await ctx.send("Depreciated. Use `fursend`.")

    ####################################################################################################################
    #                           premium image commands
    ####################################################################################################################

    @commands.command(name='imgseek')
    @commands.check(donor_check)
    async def imgseek(self, ctx, endpoint: str, count: int = 10):
        "Creates a react slideshow of a specified endpoint"
        home = self.bot.get_guild(346892627108560901)
        left = discord.utils.get(home.emojis, name="left_arrow")
        right = discord.utils.get(home.emojis, name="right_arrow")
        x = discord.utils.get(home.emojis, name="error")
        emojis = [left, right, x]
        embed = discord.Embed(color=self.bot.color)
        page = 1
        search = True
        msg = None

        if endpoint not in sfw_endpoints + nsfw_endpoints:
            message = f"{endpoint} is an invalid endpoint "
            if ctx.channel.is_nsfw():
                message += f"The supported endpoints are\n" \
                           f"NSFW {nsfw_endpoint_list}\n" \
                           f"SFW {sfw_endpoint_list}"
            else:
                message += f"The supported endpoints are for a SFW channel are\n" \
                           f"{sfw_endpoint_list}"
                if can_send(ctx):
                    return await ctx.send(message)
                else:
                    return

        if endpoint in sfw_endpoints:
            if can_send(ctx) and can_embed(ctx) and can_react(ctx):
                embed.set_image(url="https://sheri.bot/media/sheri_api_load.gif")
                msg = await ctx.send(embed=embed)
                for emoji in emojis:
                    await msg.add_reaction(emoji)
            else:
                if can_react(ctx):
                    await ctx.message.add_reaction("❌")
                try:
                    return await ctx.author.send(f"Hey! I wasn't able to process your request in {ctx.channel.mention}. "
                                                 "Please make sure I have the `Send Messages`, `Attach Files`, "
                                                 "and `Embed Links` permissions.")
                except discord.Forbidden:
                    return
        if endpoint in nsfw_endpoints:
            if ctx.channel.is_nsfw():
                embed.set_image(url="https://sheri.bot/media/sheri_api_load.gif")
                msg = await ctx.send(embed=embed)
                for emoji in emojis:
                    await msg.add_reaction(emoji)
            else:
                return await ctx.send(
                    "I can't send NSFW images in SFW channels! Sorry~!\n"
                    "*Tip: Server staff can run `furnsfw` to quickly toggle NSFW channel status*")

        imgs = await Sheri_Get.main_api_multiple(self.bot, endpoint, count)
        pages = len(imgs)

        while search is True:
            if msg is not None:
                embed = discord.Embed(color=self.bot.color,
                                      description=f"Image not loading? [Image Link]({imgs[page]['url']})\n"
                                                  f"Problem with the image? [Report it here]({imgs[page]['report_url']})")
                embed.set_footer(text=f"Image {page}/{pages} | Endpoint: {endpoint} | https://sheri.bot/")
                embed.set_image(url=imgs[page]['url'])
                await msg.edit(embed=embed)

            def check(reaction, user):
                return (
                        user == ctx.author
                        and (reaction.emoji in emojis)
                )

            '''
            def theembed(page):
                embed = discord.Embed(color=self.bot.color,
                                     description=f"Image not loading? [Image Link]({imgs[page]['url']})\n"
                                                 f"Something wrong with the image? [Report it here]"
                                                 f"({imgs[page]['report_url']})")
                embed.set_footer(text=f"Image {page}/{pages} | Endpoint: {endpoint} | https://sheri.bot/")
                embed.set_image(url=imgs[page]['url'])
                return embed
            '''

            while True:
                try:
                    reaction, user = await self.bot.wait_for(
                        "reaction_add", timeout=60.0, check=check
                    )

                    if user == ctx.author:
                        await reaction.remove(user)

                        if reaction.emoji == emojis[0]:
                            page = page - 1
                            if page == -1:
                                page = pages - 1
                            # await reaction.remove(user)
                            break
                        elif reaction.emoji == emojis[1]:
                            page = page + 1
                            max = pages
                            if page >= max:
                                page = 0

                            # await reaction.remove(user)

                            break
                        elif reaction.emoji == emojis[2]:
                            search = False
                            await msg.delete()
                            break
                except discord.Forbidden:
                    return
                except asyncio.TimeoutError:
                    await msg.clear_reactions()

    #@commands.command(name='imgroulet')
    #@commands.check(check_nsfw)
    #async def imgroulet(self, ctx):                 #spacey project


def setup(bot):
    bot.add_cog(Images(bot))
