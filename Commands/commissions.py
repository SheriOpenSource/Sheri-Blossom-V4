import asyncio
import datetime
import discord
import url_regex
from discord.ext.commands import UserConverter
from discord.ext import commands


class ValidationError(Exception):
    pass


class Commissions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verification_channel = 697542626169192518
        self.completed_channel_sfw = 697542771019481108
        self.completed_channel_nsfw = 697542590844764190

    @staticmethod
    async def get_info(db, user, *, random=False):
        if not random:
            if isinstance(user, (discord.User, discord.Member)):
                info = await db.fetchrow(
                    "SELECT user_id, name, cinfo, fa, example, nsexample, verified "
                    "from botsettings_commissions WHERE user_id = $1",
                    user.id
                )
            else:
                info = await db.fetchrow(
                    "SELECT user_id, name, cinfo, fa, example, nsexample, verified "
                    "from botsettings_commissions WHERE name = $1",
                    user
                )
        else:
            info = await db.fetchrow(
                "SELECT user_id, name, cinfo, fa, example, nsexample, verified "
                "from botsettings_commissions WHERE verified = $1 ORDER BY random() LIMIT 1",
                True
            )
        return info

    @staticmethod
    async def insert_artist(db, a_id, a_name, a_info, a_example, a_nsexample, a_fa, is_verified):
        await db.execute(
            "INSERT INTO botsettings_commissions (user_id, name, cinfo, example, nsexample, fa, verified) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7)",
            a_id, a_name, a_info, a_example, a_nsexample, a_fa, is_verified
         )

    @staticmethod
    async def delete_artist(db, user):
        if isinstance(user, (discord.User, discord.Member)):
            return await db.execute(
                "DELETE from botsettings_commissions WHERE user_id = $1",
                user.id
            )
        elif isinstance(user, str):
            return await db.execute(
                "DELETE from botsettings_commissions WHERE name = $1",
                user
            )
        else:
            return None

    @staticmethod
    async def name_exists(db, name):
        return await db.fetch(
            "SELECT * from botsettings_commissions WHERE name = $1",
            name
        )

    @staticmethod
    async def verify_artist(db, user):
        await db.execute(
            "UPDATE botsettings_commissions SET verified = $1 WHERE user_id = $2",
            True, user.id
        )

    @staticmethod
    async def unverify_artist(db, user):
        await db.execute(
            "UPDATE botsettings_commissions SET verified = $1 WHERE user_id = $2",
            False, user.id
        )

    @staticmethod
    async def get_example_from_msg(ctx, msg):
        """ Literally only here to clean up down below: Get example pic from art provided. """
        if msg.attachments:
            return msg.attachments[0].url
        else:
            # If no attachment was provided, check to see if URL is valid
            find_links = url_regex.UrlRegex(msg.content)

            if not find_links.detect:
                raise ValidationError  # Still raising an exception so it can be caught in the other method.
            else:
                # If no error is raised from that then return msg.content
                return msg.content

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, pl):
        msg_id = pl.message_id
        channel_id = pl.channel_id
        guild_id = pl.guild_id
        user = pl.member
        emoji = pl.emoji
        if user is None:
            user = self.bot.get_user(pl.user_id)
        if user.bot:
            return

        channel = self.bot.get_channel(channel_id)
        if channel.id == self.verification_channel:
            async for msg in channel.history():
                if msg.id == msg_id:
                    embeds = msg.embeds
                    if embeds:
                        embed = embeds[0]
                        _type, _id = embed.footer.text.split()
                        user_id = int(_id)

                        artist = self.bot.get_user(user_id)
                        if artist is None:
                            artist = await self.bot.fetch_user(user_id)

                        async with self.bot.pool.acquire() as db:
                            if str(emoji) == "✔":
                                await artist.send(
                                    "Congratulations! You have been verified as an artist."
                                )
                                await self.verify_artist(db, artist)
                                await msg.delete()
                                completed_channel = self.bot.get_channel(
                                    self.completed_channel_sfw if _type == "[SFW]" else self.completed_channel_nsfw
                                )
                                await completed_channel.send(embed=embed)
                            elif str(emoji) == "❌":
                                await artist.send(
                                    "Sorry, but you have been denied as an artist."
                                )
                                await self.delete_artist(db, artist)
                                await msg.delete()

                        break
                    else:
                        continue
                else:
                    continue
        else:
            return

    @commands.group()
    async def commission(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @commission.command(description='Register yourself as an artist for people to commission you.')
    async def register(self, ctx):
        """ Register yourself as an artist for people to commission you. """
        author = ctx.author
        try:
            await author.send(
                "Please answer the following questions. This will timeout after 120 seconds."
            )
        except discord.Forbidden:
            return await ctx.send(
                f"{author.mention}, please change your privacy settings so that I can DM you."
            )
        else:
            async with self.bot.pool.acquire() as db:
                info = await self.get_info(db, author)
                if info is not None:
                    await self.delete_artist(db, author)
                    await author.send(
                        "It looks like you were already registered. I've deleted your old profile "
                        "for you, so that you can re-create/update your profile."
                    )

                def check(m):
                    return m.author == author and isinstance(m.channel, discord.DMChannel)

                try:
                    # Get alias
                    await author.send(
                        "Is there any alias you like to go by? Reply `None` to use your discord name."
                    )
                    name = await self.bot.wait_for('message', check=check, timeout=120.0)

                    if name.content == 'None':
                        name = author.name.lower()
                    else:
                        if await self.name_exists(db, name.content):
                            await ctx.send(
                                "I'm sorry, but that username is already taken. "
                                "Please choose another name and try again."
                            )
                            return await ctx.reinvoke()
                        else:
                            name = name.content.lower()

                    # Get page
                    await author.send(
                        "What is your current FurAffinity/DeviantArt, etc. page?"
                    )
                    page = await self.bot.wait_for('message', check=check, timeout=120.0)

                    # Get commission info
                    await author.send(
                        "Please send me your commission info. This can either be a message, "
                        "or a link to your information."
                    )
                    info = await self.bot.wait_for('message', check=check, timeout=120.0)

                    # Get example artwork
                    await author.send(
                        "Please link/upload one (1) example piece of artwork by you."
                    )
                    art = await self.bot.wait_for('message', check=check, timeout=120.0)

                    # If an attachment was provided, get its URL
                    example = await self.get_example_from_msg(ctx, art)

                    # Get possible NSFW artwork
                    await author.send(
                        "If you do NSFW art, please link/upload one (1) NSFW piece, or say `None` if you do not."
                    )
                    nsfw_art = await self.bot.wait_for('message', check=check, timeout=120.0)

                    # If an attachment was provided, get its URL
                    if nsfw_art.content != 'None':
                        nsexample = await self.get_example_from_msg(ctx, nsfw_art)
                    else:
                        nsexample = None

                except TimeoutError:
                    return await author.send("This window has timed out. Please re-run the command.")
                except ValidationError:
                    await author.send(
                        "I'm sorry, but it appears that the URL you sent is not valid. "
                        "Please check it and try again."
                    )
                    return await ctx.reinvoke()
                else:
                    # Add to DB
                    await self.insert_artist(
                        db, author.id, name, info.content, example, nsexample, page.content, False
                    )

                    await author.send(
                        "I have saved your information. Once you are approved, people will now be "
                        f"able to commission you via `furcommission request {name}`."
                    )
                    channel = self.bot.get_channel(self.verification_channel)
                    embed = discord.Embed(
                        title='New artist commission page request:',
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color(0xe62169)
                    )
                    embed.set_footer(text=f"[{'NSFW' if nsexample is not None else 'SFW'}] {author.id}")
                    embed.add_field(
                        name="Commission Info:",
                        value=info.content, inline=False)
                    embed.add_field(
                        name="FurAffinity/Deviant Art, etc.:",
                        value=page.content,
                    inline=False)
                    embed.add_field(
                        name="Example Art:",
                        value="See below.",
                        inline=False
                    )
                    embed.set_image(url=example)
                    msg = await channel.send(embed=embed)
                    await msg.add_reaction("✔")
                    await msg.add_reaction("❌")

    @commission.command(description='Send a request to a specified artist and optional request message.')
    async def request(self, ctx, artist, *, rq_msg=None):
        """ Send a request to a specified artist and optional request message. """
        author = ctx.author
        async with self.bot.pool.acquire() as db:
            info = await self.get_info(db, artist.lower())
            if info is None:
                await ctx.send(
                    "Sorry, but I could any information with the artist provided. "
                    "Are you sure you typed their name correctly?"
                )
            else:
                userid, artist, cinfo, fa, example, nsexample, verified = info
                user = self.bot.get_user(userid)
                if user is None:
                    user = await self.bot.fetch_user(userid)
                if not verified:
                    return await ctx.send(
                        "Sorry, but that artist is not verified yet, so I cannot submit a request for you. "
                        "Please come back later and try again."
                    )

                try:
                    await user.send(
                        f"Hello there, `{user.name}`!\n{author.mention} has requested to commission you! "
                        f"You can DM them using their discord here: {author}\n"
                        f"{f'They have also attached a message for you: `{rq_msg}`' if rq_msg is not None else ''}"

                    )
                except discord.Forbidden:
                    await ctx.send(
                        "Uh oh, it looks like I could not DM the artist myself regarding your inquiry. "
                        f"If you'd like to DM the artist yourself, you can do so here: {user}"
                    )
                else:
                    await ctx.send(
                        "I've sent the message! Now all there is to do is wait! =3\n"
                        "`Note: Make sure your privacy settings allow for users to send you friend requests, etc. "
                        f"so '{user}' will be able to contact you!`"
                    )

    @commission.command(
        aliases=['preview'], description='Preview artwork from a specified artist. Leave blank for random artist.'
    )
    async def artist(self, ctx, artist=None):
        """ Preview artwork from a specified artist. """
        try:
            converter = UserConverter()
            artist = await converter.convert(ctx, artist)
        except (commands.CommandError, TypeError):
            artist = artist.lower() if isinstance(artist, str) else None
        finally:
            async with self.bot.pool.acquire() as db:
                info = await self.get_info(db, artist, random=(True if artist is None else False))

                if info is None:
                    await ctx.send(
                        "Sorry, but I could any information with the artist provided. "
                        "Are you sure you typed their name correctly, or that they're approved yet?"
                    )
                else:
                    userid, artist, cinfo, fa, example, nsexample, verified = info
                    if not verified:
                        return await ctx.send(
                            "Sorry, but that artist is not verified yet and thus I cannot show you their details."
                        )

                    embed = discord.Embed(
                        title=f"Here's what I found for `{artist.title()}`: ",
                        description=f"If you want to commission this artist, do `furcommission request {artist}`!",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color(0xe62169)
                    )
                    embed.add_field(
                        name=f'Commission info for `{artist.title()}`:',
                        value=cinfo,
                        inline=False
                    )
                    embed.add_field(
                        name=f"`{artist.title()}`'s Current Art Portfolio:",
                        value=fa,
                        inline=False
                    )
                    embed.add_field(
                        name=f"Example art from `{artist.title()}`:",
                        value="See below.",
                        inline=False
                    )
                    user = self.bot.get_user(userid)
                    if user is None:
                        user = await self.bot.fetch_user(userid)
                    embed.set_footer(
                        text=f'"{artist.title()}" on discord: {user}'
                    )

                    if (isinstance(ctx.channel, discord.DMChannel)) \
                            or (not ctx.channel.is_nsfw()) \
                            or (nsexample is None):
                        embed.set_image(url=example)
                        embed.set_author(
                            name="(Click here if the image example does not load for you.)",
                            url=example
                        )
                    else:
                        embed.set_image(url=nsexample)
                        embed.set_author(
                            name="(Click here if the image example does not load for you.)",
                            url=nsexample
                        )
                    await ctx.send(embed=embed)

    @commission.command(description='Delete your artist profile.')
    async def delete(self, ctx):
        async with self.bot.pool.acquire() as db:
            if await self.delete_artist(db, ctx.author) is not None:
                await ctx.send(
                    "Deleted your artist profile. Have a good day!"
                )
            else:
                await ctx.send(
                    "Unable to delete your artist profile. Did you create one?"
                )

    @commission.command(description='Admin delete artist profile.')
    @commands.is_owner()
    async def adelete(self, ctx, artist):
        """ Admin delete artist profile. """
        async with self.bot.pool.acquire() as db:
            try:
                converter = UserConverter()
                artist = await converter.convert(ctx, artist)
            except (commands.CommandError, TypeError):
                artist = artist.lower() if isinstance(artist, str) else None
            finally:
                if await self.delete_artist(db, artist) is not None:
                    await ctx.send(
                        f"Deleted {artist}'s profile. Have a good day!"
                    )
                else:
                    await ctx.send(
                        f"Unable to delete {artist}'s profile. Did they have one?"
                    )


def setup(bot):
    bot.add_cog(Commissions(bot))
