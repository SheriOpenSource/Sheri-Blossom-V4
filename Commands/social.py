import asyncio
import random

import discord
import yaml
from discord.ext import commands

from API.API import Retrieval as Get
from Checks.bot_checks import check_nsfw
from Formats.chat_markdown import bold, italics
from Formats.formats import pagify, avatar_check
from Functions.core import send_message, commands_help
from Functions.social import draw_love_meter, draw_smash_meter, SocialFunc
from Lines.SocialLines import SocialLines as Data
from Lines.SocialLines import nsfw
from Lines.custom_emotes import CustomEmotes


class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    def embed_maker(self, ctx, action, user, sender):
        with open('Config/social.yaml', 'r') as f:
            data = yaml.safe_load(f)
        if user == sender:
            msg = data[action]['selfmsg']
        else:
            msg = data[action]['msg']
        num = random.randint(1, int(data[action]['num']))
        if action == "fever":
            filetype = ".jpg"
        else:
            filetype = ".gif"
        baseurl = "http://cdn.hardinserver.com/social/"
        url = f'{baseurl}{action}/{action}{num}{filetype}'
        embed = discord.Embed(color=ctx.color, title=msg.format(sender, user))
        embed.set_image(url=url)
        return embed

    @commands.group(name="social", aliases=['soc', 's'])
    @commands.guild_only()
    async def social_index(self, ctx):
        if ctx.invoked_subcommand is None:
            # embed = discord.Embed(title="Social Commands!")
            # list = ["kiss", "bite", "slap", "taunt", "cuddle", "hugs", "feed", "spanky", "tease", "hi5", "shoot", "lick",
            #        "shake", "shoot", "twerk", "strip", "thirsty", "moist", "whip", "facepalm", "ohno", "hungry", "nuts",
            #        "fever", "socialcmds"]
            # embed.description = ""
            # for x in list:
            #    embed.description += f"fursocial {x}\n"
            # return await ctx.send(embed=embed)
            await commands_help(ctx, ["social kiss",
                                      "social bite",
                                      "social slap",
                                      "social taunt",
                                      "social cuddle",
                                      "social hug",
                                      "social feed",
                                      "social spank",
                                      "social tease",
                                      "social hi5",
                                      "social shoot",
                                      "social lick",
                                      "social shake",
                                      "social twerk",
                                      "social strip",
                                      "social thirsty",
                                      "social moist",
                                      "social whip",
                                      "social facepalm",
                                      "social ohno",
                                      "social hungry",
                                      "social nuts",
                                      "social fever",
                                      "social help"
                                      ], "Non-Furry Social")

    @social_index.command(name='kiss', aliases=['kisses', 'k'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_kiss(self, ctx, *, user: discord.Member):
        """Kiss people!"""
        action = "kiss"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='bite', aliases=['bites'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def social_bite(self, ctx, *, user: discord.Member):
        """Bite people!"""
        action = "bite"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='slap', aliases=['slaps'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_slap(self, ctx, *, user: discord.Member):
        """Slap people!"""
        action = "slap"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='taunt', aliases=['taunts'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_taunt(self, ctx, *, user: discord.Member):
        """Taunt people!"""
        action = "taunt"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='cuddle', aliases=['cuddles'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_cuddle(self, ctx, *, user: discord.Member):
        """Cuddle people!"""
        action = "cuddle"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='hug', aliases=['hugs', 'h'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_hugs(self, ctx, *, user: discord.Member):
        """Hug people!"""
        action = "hug"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='feed', aliases=['feeds'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_feed(self, ctx, *, user: discord.Member):
        """Feed people!"""
        action = "feed"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='spank', aliases=['spanks'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_spank(self, ctx, *, user: discord.Member):
        """Spank people!"""
        action = "spank"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='tease', aliases=['teases'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_tease(self, ctx, *, user: discord.Member):
        """Tease people!"""
        action = "tease"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='hi5', pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_hi5(self, ctx, *, user: discord.Member):
        """HighFive people!"""
        action = "hi5"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='shoot', aliases=['shoots'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_shoot(self, ctx, *, user: discord.Member):
        """Shoot people!"""
        action = "shoot"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='lick', aliases=['licks'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def social_lick(self, ctx, *, user: discord.Member):
        """Lick people!"""
        action = "lick"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='shake', aliases=['shakes', 'handshake'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_shake(self, ctx, *, user: discord.Member):
        """Handshake!"""
        action = "shake"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='twerk', aliases=['twerks'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def social_twerk(self, ctx, *, user: discord.Member):
        """TWERK!"""
        action = "twerk"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='strip', aliases=['strips'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def social_strip(self, ctx, *, user: discord.Member):
        """STRIP!"""
        action = "strip"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='thirsty', aliases=['cooldown'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_thirsty(self, ctx, *, user: discord.Member):
        """The Thirst is Real!"""
        action = "thirsty"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='moist', pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_moist(self, ctx, *, user: discord.Member):
        """Moist lol!"""
        action = "moist"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='whip', aliases=['whips'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_whip(self, ctx, *, user: discord.Member):
        """Whip someone!"""
        action = "whip"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='facepalm', aliases=['facepalms', 'omg', 'fp'], pass_context=True,
                          invoke_without_command=True)
    @commands.guild_only()
    async def social_facepalm(self, ctx, *, user: discord.Member):
        """Facepalm images!"""
        action = "facepalm"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='ohno', aliases=['sassy'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_ohno(self, ctx, *, user: discord.Member):
        """Oh no they didnt images!"""
        action = "ono"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='hungry', pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    @commands.check(check_nsfw)
    async def social_hungry(self, ctx, *, user: discord.Member):
        """Hungry images!"""
        action = "hungry"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='nuts', aliases=['nutcheck'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_nuts(self, ctx, *, user: discord.Member):
        """NutCracker images!"""
        action = "nuts"
        await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))

    @social_index.command(name='fever', aliases=['bieber', 'beiber'], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def social_fever(self, ctx):
        """Do you have the Fever?"""
        action = "fever"
        user = ctx.message.author
        try:
            await ctx.send(embed=self.embed_maker(ctx, action, user, sender=ctx.message.author))
        except KeyError:
            await ctx.send(
                "Looks like you included a user! This command doesn't need that. Just use `fever` by itself.")

    @social_index.command(name='socialcmds', aliases=['scmds', 'cmds', 'cmdlist', 'help'], pass_context=True,
                          invoke_without_command=True)
    @commands.guild_only()
    async def social_socialcmds(self, ctx):
        """List all Social Commands"""
        embed = discord.Embed(title="Social Commands!")
        list = ["kiss", "bite", "slap", "taunt", "cuddle", "hugs", "feed", "spanky", "tease", "hi5", "shoot", "lick",
                "shake", "shoot", "twerk", "strip", "thirsty", "moist", "whip", "facepalm", "ohno", "hungry", "nuts",
                "fever", "socialcmds"]
        embed.description = ""
        for x in list:
            embed.description += f"fursocial {x}\n"
        await ctx.send(embed=embed)

    ########################################
    #       Hugging Commands
    ########################################
    @commands.guild_only()
    @commands.command(name="hug", aliases=["huggles", "huggies", "huddles", "hugs", "huggle"])
    async def sfw_hug(self, ctx, *users: discord.Member):
        """Hug a member!"""
        error_message = "You need to mention someone to hug!"
        await SocialFunc.social(self, ctx, error_message, 'hug', 'hug', False, *users)

    @commands.guild_only()
    @commands.command(name="nhug", aliases=["nhuggles", "nhuggies", "nhuddles", "nhugs", "nhuggle"])
    @commands.check(check_nsfw)
    async def nsfw_hug(self, ctx, *users: discord.Member):
        """Hug a member in a lewd way!"""
        error_message = "You need to mention someone to lewdly hug them."
        await SocialFunc.social(self, ctx, error_message, 'nhug', "hug", True, *users)

    ########################################
    #       Kissing Commands
    ########################################
    @commands.guild_only()
    @commands.command(name="kiss", aliases=["kisses", "kissies"])
    async def sfw_kiss(self, ctx, *users: discord.Member):
        """Kiss a member!"""
        error_message = "You need to mention someone to kiss them."
        await SocialFunc.social(self, ctx, error_message, 'kiss', 'kiss', False, *users)

    @commands.guild_only()
    @commands.command(name="nkiss", aliases=["nkisses", "nkissies"])
    @commands.check(check_nsfw)
    async def nsfw_kiss(self, ctx, *users: discord.Member):
        """Kiss a member in a lewd way"""
        error_message = "You have to mention someone to lewdly kiss them."
        await SocialFunc.social(self, ctx, error_message, 'nkiss', 'kiss', True, *users)

    ########################################
    #     Cuddling Commands
    ########################################
    @commands.guild_only()
    @commands.command(name='cuddle', aliases=["snuggle", "snuggles", "cuddles", "snug"])
    async def sfw_cuddle(self, ctx, *users: discord.Member):
        """Cuddle a member!"""
        error_message = "You have to mention someone to cuddle them."
        await SocialFunc.social(self, ctx, error_message, 'cuddle', 'cuddle', False, *users)

    @commands.guild_only()
    @commands.command(name="ncuddle", aliases=["nsnuggle", "nsnuggles", "ncuddles"])
    @commands.check(check_nsfw)
    async def nsfw_cuddle(self, ctx, *users: discord.Member):
        """Cuddle a member in a lewd way"""
        error_message = "You have to mention someone to lewdly cuddle them."
        await SocialFunc.social(self, ctx, error_message, 'ncuddle', 'cuddle', True, *users)

    ########################################
    #      Holding Commands
    ########################################
    @commands.command(name="hold")
    async def sfw_hold(self, ctx, *users: discord.Member):
        """Hold a member"""
        error_message = "You have to mention to cuddle them."
        await SocialFunc.social(self, ctx, error_message, 'hold', 'hold', False, *users)

    @commands.guild_only()
    @commands.command(name='nhold')
    @commands.check(check_nsfw)
    async def nsfw_hold(self, ctx, *users: discord.Member):
        """Hold a member in a lewd way!"""
        error_message = "You have to mention someone to lewdly hold them."
        await SocialFunc.social(self, ctx, error_message, 'nhold', 'hold', True, *users)

    ########################################
    #       Licking Commands
    ########################################
    @commands.guild_only()
    @commands.command(name="lick", aliases=['licky, licks'])
    async def sfw_lick(self, ctx, *users: discord.Member):
        """Lick a member!"""
        error_message = "You have to mention someone to lick them."
        await SocialFunc.social(self, ctx, error_message, 'lick', 'lick', False, *users)

    @commands.guild_only()
    @commands.command(name="nlick", aliases=["nlicky", "nlicks"])
    @commands.check(check_nsfw)
    async def nsfw_lick(self, ctx, *users: discord.Member):
        """Lick a member in a nsfw way"""
        error_message = "You have to mention someone to lewdly lick them."
        await SocialFunc.social(self, ctx, error_message, 'nlick', 'lick', True, *users)

    #########################################
    #    Wagging Commands
    #########################################
    @commands.guild_only()
    @commands.command(name="wag")
    async def sfw_wag(self, ctx, *users: discord.Member):
        """Wag your tail Floofball at someone!"""
        error_message = "You have to mention someone to wag your tail at them."
        await SocialFunc.social(self, ctx, error_message, None, 'wags', False, *users)

    @commands.guild_only()
    @commands.command(name="nwag")
    @commands.check(check_nsfw)
    async def nsfw_wag(self, ctx, *users: discord.Member):
        """Wag your tail Floofball at someone in a sfw way!"""
        error_message = "You have to mention someone to wag your tail at them."
        await SocialFunc.social(self, ctx, error_message, None, 'wags', True, *users)

    #########################################
    #    Pickup Commands
    #########################################
    @commands.guild_only()
    @commands.command(name="pickup")
    async def sfw_pickup(self, ctx, user: discord.Member = None):
        if not user:
            return await ctx.send("You need to pick someone to pickup with :)")
        rng = Data.get_social_line('pickup').format(f"**{user.name}**")
        message = f"**{ctx.author.name}** says {rng}"
        await send_message(ctx, message=message)

    @commands.guild_only()
    @commands.command(name="npickup")
    @commands.check(check_nsfw)
    async def nsfw_pickup(self, ctx, user: discord.Member = None):
        if not user:
            return await ctx.send("You need to pick someone to pickup with :)")
        rng = Data.get_social_line('pickup', True).format(f"**{user.name}**")
        message = f"**{ctx.author.name}** says {rng}."
        await send_message(ctx, message=message)

    #########################################
    #    Miscellaneous SFW Commands
    #########################################

    @commands.guild_only()
    @commands.command(name="insult")
    async def sfw_insult(self, ctx, user: discord.Member = None):
        """Insult a user."""
        if user is None:
            user = ctx.author
        insult_rng = Data.get_social_line('insults')
        await ctx.send(f"**{user}**, {insult_rng}")

    @commands.guild_only()
    @commands.command(name="pounce")
    async def sfw_pounce(self, ctx, *users: discord.Member):
        """Pounce on a member!"""
        error_message = "You need to mention someone to pounce on them."
        await SocialFunc.social(self, ctx, error_message, None, "pounces", False, *users)

    @commands.guild_only()
    @commands.command(name="boop")
    async def sfw_boop(self, ctx, *users: discord.Member):
        """Boop a Mamber!"""
        error_message = "You have to mention someone to boop them."
        await SocialFunc.social(self, ctx, error_message, 'boop', 'boop', False, *users)

    @commands.guild_only()
    @commands.command(name="pat")
    async def sfw_pat(self, ctx, *users: discord.Member):
        """Pats a member!"""
        error_message = "You have to mention someone to pat them."
        await SocialFunc.social(self, ctx, error_message, 'pat', 'pat', False, *users)

    @commands.guild_only()
    @commands.command(name="nuzzle")
    async def sfw_nuzzle(self, ctx, *users: discord.Member):
        """Nuzzle a member!"""
        error_message = "Have to mention someone to nuzzle them."
        await SocialFunc.social(self, ctx, error_message, None, 'nuzzles', False, *users)

    @commands.guild_only()
    @commands.cooldown(1, 30, type=commands.BucketType.user)
    @commands.command(name="kill")
    async def kill(self, ctx, user: discord.Member = None):
        if not user:
            return await ctx.send("you need to mention your victim")
        else:
            rng = Data.get_social_line('kills').format(
                f"**{user.name}**", f"**{ctx.author.name}**"
            )
            await send_message(ctx, message=rng)

    @commands.guild_only()
    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def ship(self, ctx, lover1: discord.Member, *, lover2: discord.Member = None):
        """Ship people!"""
        e = discord.Embed(
            color=self.bot.color,
            description=f"{CustomEmotes.get_emote(paw=True)} **Contacting my api, standby** {CustomEmotes.get_emote(paw=True)}",
        )
        e.set_image(url="https://sheri.bot/media/sheri_api_load.gif")
        msg = await send_message(ctx, embed=e)
        # Checking for second Member
        if not lover2:
            lover2 = ctx.author

        # Calling API
        lover1_ava, lover2_ava = (
            str(lover1.avatar_url_as(static_format="png")).split("?")[0],
            str(lover2.avatar_url_as(static_format="png")).split("?")[0],
        )
        try:
            status, response = await Get.fetch_ship_or_smash_img(ctx, lover1_ava, lover2_ava)
        except (TypeError, KeyError):
            return await ctx.send("Hmm, I need a bit more time calculating... Try again later!")

        # Checking for errors
        if not status:
            await msg.delete()
            err_emb = discord.Embed(color=self.bot.color, description=response)
            err_emb.set_image(url="https://dev.sheri.bot/media/service-unavaliable.png")
            return await ctx.send(embed=err_emb)

        # Making ship names
        name1 = (
                lover1.name[: -round(len(lover1.name) / 2)]
                + lover2.name[-round(len(lover2.name) / 2):]
        )
        name2 = (
                lover2.name[: -round(len(lover2.name) / 2)]
                + lover1.name[-round(len(lover1.name) / 2):]
        )

        # Making and sending the embed
        desc = (
            f"**{ctx.author.mention} ships {lover1.mention} and {lover2.mention}!**\n\n "
            f"Ship names: __**{name1}**__ or __**{name2}**__\n\n "
            f"{draw_love_meter()}"
        )
        em = discord.Embed(color=self.bot.color, description=desc)
        em.set_author(name="Lovely shipping!")
        em.set_image(url="attachment://ship.png")
        await msg.delete()
        try:
            await send_message(ctx, file=response, embed=em)
        except BaseException:
            await send_message(ctx, message="I need to think about this more. . .")

    ########################################
    #    Miscellaneous NSFW commands
    ########################################

    @commands.guild_only()
    @commands.check(check_nsfw)
    @commands.command(name="group")
    async def group(
            self, ctx, user1: discord.Member = None, user2: discord.Member = None
    ):
        if (user1 is None and user2 is None) or (user2 is None):
            return await ctx.send("You need to have at least 2 people to group with.")
        if ctx.author.id == user1.id or ctx.author.id == user2.id:
            return await ctx.send("You need to have at least 2 people to group with.")
        group_initate = bold(ctx.author.name)
        group_member1 = bold(user1.name)
        group_member2 = bold(user2.name)
        rng = random.choice(nsfw['group'])
        img = await Get.main_api(self.bot, "ngroup")
        embed = SocialFunc.social_img_embed(img['url'], img['report_url'])
        await ctx.send(
            italics(rng.format(group_initate, group_member1, group_member2)),
            embed=embed,
        )

    @commands.guild_only()
    @commands.command(name="bang", aliases=["fuck", "pound"])
    @commands.check(check_nsfw)
    async def nsfw_bang(self, ctx, *users: discord.Member):
        """Bang someone hard and good :)"""
        error_message = "You have to mention someone to bang them."
        await SocialFunc.social(self, ctx, error_message, 'bang', 'bang', True, *users)

    @commands.guild_only()
    @commands.command(name="creampie")
    @commands.check(check_nsfw)
    async def nsfw_creampie(self, ctx, *users: discord.Member):
        """Bang someone hard and good :)"""
        endpoints = ['fcreampie', 'mcreampie']
        error_message = "You have to mention someone to creampie them."
        await SocialFunc.social(self, ctx, error_message, random.choice(endpoints), 'creampie', True, *users)

    @commands.guild_only()
    @commands.command(name="present")
    @commands.check(check_nsfw)
    async def nsfw_presentation(self, ctx, *users: discord.Member):
        """Present yourself!"""
        error_message = "You have to mention someone to present yourself to them."
        await SocialFunc.social(self, ctx, error_message, 'fpresentation', 'presentation', True, *users)

    @commands.guild_only()
    @commands.command(name="masturbate", aliases=['kinky'])
    @commands.check(check_nsfw)
    async def nsfw_masturbate(self, ctx, *users: discord.Member):
        """Bang someone hard and good :)"""
        endpoints = ['fsolo', 'msolo']
        error_message = "You have to mention someone to masturbate in front of them."
        await SocialFunc.social(self, ctx, error_message, random.choice(endpoints), 'solo', True, *users)

    @commands.guild_only()
    @commands.command(name="ride")
    @commands.check(check_nsfw)
    async def nsfw_ride(self, ctx, *users: discord.Member):
        """get banged by someone hard and good :)"""
        error_message = "You have to mention someone to ride them."
        await SocialFunc.social(self, ctx, error_message, 'ride', 'ride', True, *users)

    @commands.guild_only()
    @commands.command(name="booty")
    @commands.check(check_nsfw)
    async def nsfw_booty(self, ctx, *users: discord.Member):
        """Booty"""
        error_message = "You have to mention someone to butt them."
        await SocialFunc.social(self, ctx, error_message, 'booty', 'booty', True, *users)

    @commands.guild_only()
    @commands.command(name="suck", aliases=["slurp", "sucks", "suckies", 'milk'])
    @commands.check(check_nsfw)
    async def nsfw_suck(self, ctx, *users: discord.Member):
        """Suck a member off"""
        error_message = "You have to mention someone to suck them."
        await SocialFunc.social(self, ctx, error_message, 'suck', 'suck', True, *users)

    @commands.guild_only()
    @commands.command(name="finger")
    @commands.check(check_nsfw)
    async def nsfw_finger(self, ctx, *users: discord.Member):
        """Finger a member"""
        error_message = "You have to mention someone to finger them."
        await SocialFunc.social(self, ctx, error_message, 'finger', 'finger', True, *users)

    @commands.guild_only()
    @commands.command(name="bulge", aliases=["buldge"])
    @commands.check(check_nsfw)
    async def nsfw_bulge(self, ctx, *users: discord.Member):
        """Bulges!"""
        error_message = "You have to mention someone to interact with their bulge."
        await SocialFunc.social(self, ctx, error_message, 'nbulge', 'bulge', True, *users)

    @commands.guild_only()
    @commands.command(name="spank", aliases=["spankies"])
    @commands.check(check_nsfw)
    async def nsfw_spank(self, ctx, *users: discord.Member):
        error_message = "You have to mention someone to lewdly lick them."
        await SocialFunc.social(self, ctx, error_message, 'nspank', 'spank', True, *users)

    @commands.guild_only()
    @commands.command(aliases=["teases"])
    @commands.check(check_nsfw)
    async def tease(self, ctx, *users: discord.Member):
        endpoints = ['ntease', 'nseduce', 'msolo', 'fsolo']
        error_message = "You have to mention someone to lewdly tease them."
        await SocialFunc.social(self, ctx, error_message, random.choice(endpoints), 'tease', True, *users)

    @commands.guild_only()
    @commands.command(aliases=["seduces"])
    @commands.check(check_nsfw)
    async def seduce(self, ctx, *users: discord.Member):
        endpoints = ['ntease', 'nseduce']
        error_message = "You have to mention someone to lewdly tease them."
        await SocialFunc.social(self, ctx, error_message, random.choice(endpoints), 'seduce', True, *users)

    @commands.guild_only()
    @commands.command()
    @commands.check(check_nsfw)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def smash(
            self, ctx, lover1: discord.Member, *, lover2: discord.Member = None
    ):
        """Ship people!"""
        e = discord.Embed(
            color=self.bot.color,
            description=f"{CustomEmotes.get_emote(paw=True)} **Contacting my api, standby** {CustomEmotes.get_emote(paw=True)}",
        )
        e.set_image(url="https://sheri.bot/media/sheri_api_load.gif")
        msg = await ctx.send(embed=e)
        # Checking for second Member
        if not lover2:
            lover2 = ctx.author

        # Calling API
        lover1_ava, lover2_ava = (
            str(lover1.avatar_url_as(static_format="png")).split("?")[0],
            str(lover2.avatar_url_as(static_format="png")).split("?")[0],
        )
        status, response = await Get.fetch_ship_or_smash_img(ctx, lover1_ava, lover2_ava, True)

        # Checking for errors
        if not status:
            await msg.delete()
            err_emb = discord.Embed(color=self.bot.color, description=response)
            err_emb.set_image(url="https://dev.sheri.bot/media/service-unavaliable.png")
            return await ctx.send(embed=err_emb)

        # Making and sending the embed
        desc = (
            f"**{ctx.author.mention} smashes {lover1.mention} and {lover2.mention}!**\n\n "
            f"{draw_smash_meter()}"
        )
        em = discord.Embed(color=self.bot.color, description=desc)
        em.set_author(name="Lovely shipping!")
        em.set_image(url="attachment://ship.png")
        await msg.delete()
        await ctx.send(file=response, embed=em)

    @commands.guild_only()  # cocksize mod test command
    @commands.command()
    @commands.check(check_nsfw)
    async def cocksizet(self, ctx, *users: discord.Member):
        """Detects user's penis length
        Enter multiple users for an accurate comparison!"""
        if not users:
            await ctx.send("You gotta mention someone to get their size :eyes:")
            return
        c = 1
        if ctx.author.id == 139800365393510400:
            await ctx.send("error 404 cock not found :mag_right:")
            return

        dongs = {}
        msg = ""
        state = random.getstate()

        for user in users:
            if user.id == 406709411961372673:
                dongs = "OwO what a big cock you have"
                c = 0
            elif random.seed(user.id):
                dongs[user] = "8{}D".format("=" * random.randint(0, 30))

        if c == 1:
            random.setstate(state)
            dongs = sorted(dongs.items(), key=lambda x: x[1])

        for user, dong in dongs:
            if c == 1:
                msg += "**{}'s size:**\n{}\n".format(user.name, dong)
            else:
                msg += "**{}'s size:**\n{}\n".format(user.name, dongs)
        for page in pagify(msg):
            embed = discord.Embed(color=self.bot.color, description=page)
            embed.set_footer(text="HoW BiG iS yOuR CoCk BoIs 😏")
            await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    @commands.check(check_nsfw)
    async def cocksize(self, ctx, *users: discord.Member):
        """Detects user's penis length
        Enter multiple users for an accurate comparison!"""
        if not users:
            await ctx.send("You gotta mention someone to get their size :eyes:")
            return
        dongs = {}
        msg = ""
        state = random.getstate()

        for user in users:
            random.seed(user.id)
            dongs[user] = "8{}D".format("=" * random.randint(0, 30))

        random.setstate(state)
        dongs = sorted(dongs.items(), key=lambda x: x[1])

        for user, dong in dongs:
            msg += "**{}'s size:**\n{}\n".format(user.name, dong)

        for page in pagify(msg):
            embed = discord.Embed(color=self.bot.color, description=page)
            embed.set_footer(text="HoW BiG iS yOuR CoCk BoIs 😏")
            await ctx.send(embed=embed)

    ################################################################################################
    #                           Marry System
    ################################################################################################

    @commands.command(name="marry")
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def marry_index(self, ctx, *, user: discord.Member = None):
        if user is None:
            return await ctx.send("Can't marry air silly!")
        if user.id == self.bot.user.id:
            return await ctx.send("I'm already taken!")
        if user.bot:
            return await ctx.send("You can't marry a robot")
        if user.id == ctx.author.id:
            return await ctx.send(
                "Wow, better find someone to mingle with instead of trying to marry yourself."
            )
        async with self.bot.pool.acquire() as db:
            your_info = await db.fetchrow(
                "SELECT marry FROM botsettings_user WHERE id=$1", ctx.author.id
            )
            their_info = await db.fetchrow(
                "SELECT marry FROM botsettings_user WHERE id=$1", user.id
            )
            their_spouses = their_info["marry"]
            your_spouses = your_info["marry"]
            if ctx.author.id in their_spouses and user.id in your_spouses:
                return await ctx.send("You can't marry the same person again!")

            def check(m):
                return m.author == user and m.channel == ctx.message.channel

            image = await Get.main_api(self.bot, "proposal")
            desc = "💍" + ctx.author.name + " *has proposed to* " + user.name + "💍"
            name = "⛪" + user.name + ",  Do you accept ? ⛪"
            em = discord.Embed(description=desc, color=self.bot.color)
            em.set_image(url=image["url"])
            em.add_field(
                name=name, value="Type **yes** to accept or **no** to decline."
            )
            await ctx.send(embed=em)
            try:
                response = await self.bot.wait_for("message", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                msg = f"The proposal between {ctx.author.name} and {user.name} has been declined."
                em2 = discord.Embed(description=msg, color=self.bot.color)
                return await ctx.send(embed=em2)
            yeses = [
                "yes",
                "Yes",
                "YES",
                "I do",
                "i do",
                "yep",
                "yus",
                "YES!",
                "yes!",
                "Yes!",
            ]
            nos = ["No", "no", "nope", "eww", "fuck off", "No!", "no!", "NO", "NO!"]
            if any(response.content in s for s in yeses):
                their_spouses.append(ctx.author.id)
                your_spouses.append(user.id)
                await db.execute(
                    "UPDATE botsettings_user SET marry=$1 WHERE id=$2",
                    your_spouses,
                    ctx.author.id,
                )
                await db.execute(
                    "UPDATE botsettings_user SET marry=$1 WHERE id=$2",
                    their_spouses,
                    user.id,
                )

                msg = f"❤ Congratulations {ctx.author.name} and {user.name} ❤"
                em1 = discord.Embed(description=msg, color=self.bot.color)
                await ctx.send(embed=em1)

            else:
                if any(response.content in s for s in nos):
                    msg = f"The proposal between {ctx.author.name} and {user.name} has been declined."
                    em2 = discord.Embed(description=msg, color=self.bot.color)
                    await ctx.send(embed=em2)

    @commands.command(name="divorce")
    async def divorce(self, ctx, user: discord.User = None):
        async with self.bot.pool.acquire() as db:
            if user is None:
                return await ctx.send("You can not divorce air silly.")
            if user.id == ctx.author.id:
                return await ctx.send("You have to have a mate to begin with :eyes:")
            your_info = await db.fetchrow(
                "SELECT marry FROM botsettings_user WHERE id=$1", ctx.author.id
            )
            their_info = await db.fetchrow(
                "SELECT marry FROM botsettings_user WHERE id=$1", user.id
            )
            their_spouses = their_info["marry"]
            your_spouses = your_info["marry"]

            if not their_spouses or not your_spouses:
                return
            
            if ctx.author.id in their_spouses and user.id in your_spouses:
                their_spouses.remove(ctx.author.id)
                your_spouses.remove(user.id)
                await db.execute(
                    "UPDATE botsettings_user SET marry=$1 WHERE id=$2",
                    your_spouses,
                    ctx.author.id,
                )
                await db.execute(
                    "UPDATE botsettings_user SET marry=$1 WHERE id=$2",
                    their_spouses,
                    user.id,
                )
                msg = f"You have divorced {user.name}!"
                em1 = discord.Embed(description=msg, color=self.bot.color)
                await ctx.send(embed=em1)
            else:
                return await ctx.send("You are not married to this person")

    @commands.command(name="spouses")
    async def spouses(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        async with self.bot.pool.acquire() as db:
            your_info = await db.fetchrow(
                "SELECT marry FROM botsettings_user WHERE id=$1", user.id
            )
            spouses = []
            for user_id in your_info["marry"]:
                try:
                    spouse = self.bot.get_user(int(user_id))
                    spouses.append(str(spouse))
                except discord.HTTPException:
                    spouses.append(f"Unknown spouse (ID: {user_id})")
            spouses_string = ", ".join(spouses)
            if not spouses:
                spouses_string = "Nobody"
            embed = discord.Embed(
                color=self.bot.color,
                description=spouses_string,
                title=f"{user.name}'s Spouses",
            ).set_author(name=user.name, icon_url=avatar_check(user))
            await send_message(ctx, embed=embed)


def setup(bot):
    bot.add_cog(Social(bot))
