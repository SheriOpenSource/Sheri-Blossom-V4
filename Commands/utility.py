import asyncio
import re
from collections import Counter
from random import randint

import aiohttp
import discord
from discord.ext import commands

from API.ExAPI import External_Retrieval as ExGet
from Checks.bot_checks import can_send, can_edit_role, can_embed, can_react, can_manage_user
from Formats.chat_markdown import bold
from Formats.formats import avatar_check, icon_check
from Functions.reminders import Reminders as Reminder
from Functions.text import escape, pagify
from Functions.time import get_relative_delta, parse_time
from Lines.custom_emotes import CustomEmotes
from Lines.names import Names
from Functions.core import send_message
from Checks.checks import donor_check

statuses = {
    "idle": "<:away2:642763092303806474>",
    "dnd": "<:dnd2:642763090705776670>",
    "online": "<:online2:642763090647318558>",
    "streaming": "<:streaming2:642763091964198986>",
    "listening": "<:Spooodify:636278290339987460>",
    "offline": "<:offline2:642763090743787550>",
}
voice_perms = [
    "connect",
    "deafen_members",
    "move_members",
    "mute_members",
    "priority_speaker",
    "speak",
    "stream",
    "use_voice_activation",
]


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
        self.tineye_session = bot.session

    @staticmethod
    def _tag_to_title(tag):
        return tag.replace(' ', ', ').replace('_', ' ').title()

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None, aliases=None):
        if aliases is None:
            aliases = ["pfp"]
        author = ctx.message.author
        if user is None:
            user = author
        image = avatar_check(user)
        em = discord.Embed(
            color=self.bot.color,
            description=f"{user.display_name}'s Avatar\n"
                        f"**Avatar Link: [Link]({image})**",
        )
        em.set_footer(text="🐾 Murrr!! Stop stealing avatars 🐾")
        em.set_image(url=image)
        await send_message(ctx, embed=em)

    @commands.command()
    async def emote(self, ctx, emoji: str):
        """Shows the emoji your looking for."""
        if not re.compile(r"<(a?:.+):([0-9]+)>").match(emoji):
            url = "https://twemoji.maxcdn.com/2/72x72/{}.png".format(
                "-".join(
                    char.encode("unicode_escape").decode("utf-8")[2:].lstrip("0")
                    for char in emoji
                )
            )
            async with self.session.get(url) as resp:
                if resp.status == 404:
                    return await ctx.send(f"Murrr, I cant find `{emoji}`. 🐾")
                else:
                    em = discord.Embed(color=self.bot.color, title=f"{emoji}.")
                    em.set_footer(text="🐾 Murrr!! Stop stealing emotes 🐾")
                    em.set_image(url=url)
                    return await ctx.send(embed=em)
        if re.compile(r"<:(.+):([0-9]+)>").match(emoji):
            name, eid = re.compile(r"<(a?:.+):([0-9]+)>").findall(emoji)[0]
            url = "https://cdn.discordapp.com/emojis/{}.png".format(eid)
            n = name.replace(":", "")
            em = discord.Embed(
                color=self.bot.color, title=f"{ctx.author.name} here's {n}."
            )
            em.set_footer(text="🐾 Murrr!! Stop stealing emotes 🐾")
            em.set_image(url=url)
            return await ctx.send(embed=em)
        if re.compile(r"<(a?:.+):([0-9]+)>").match(emoji):
            name, eid = re.compile(r"<(a?:.+):([0-9]+)>").findall(emoji)[0]
            url = "https://cdn.discordapp.com/emojis/{}.gif".format(eid)
            n = name.replace("a:", "")
            em = discord.Embed(
                color=self.bot.color, title=f"{ctx.author.name} here's {n}."
            )
            em.set_footer(text="🐾 Murrr!! Stop stealing emotes 🐾")
            em.set_image(url=url)
            return await ctx.send(embed=em)

        # Emote cmd bracket
        @commands.command(aliases=["adde"])
        @commands.has_permissions(manage_emojis=True)
        @commands.cooldown(1, 5, commands.BucketType.user)
        async def addemote(self, ctx, name: str = None, *, reason: str = None):
            if name is None:
                await ctx.send("You need a name silly!")
            else:
                image = ctx.message.attachments

                if not image:
                    await ctx.send(
                        "I need an image!\n Supported formats are PNG, JPG and GIF\n\nNote: Must be less than 256kb!")
                else:
                    image = image[0]
                    img = "{0.url}".format(image)
                    err = False
                    async with aiohttp.ClientSession() as session:
                        raw_response = await session.get(img)
                        response = await raw_response.read()

                    if raw_response.status != 200:
                        raise self.query_error
                    if reason is None:
                        reason = f"Added by {ctx.message.author}"
                    try:
                        emoji = await ctx.guild.create_custom_emoji(
                            name=name,
                            image=response,
                            roles=None,
                            eason=reason
                        )
                    except discord.HTTPException:
                        await ctx.send(
                            f"Error when creating the emoji. Make sure its PNG,JPG and GIF with also less than 256kb")
                        err = True
                    else:
                        if err is not True:
                            await ctx.send(f"Your emoji was created with:\nID:{emoji.id}")

    @commands.command()
    async def poll(self, ctx, *, question: str):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        embed = discord.Embed(
            color=self.bot.color,
            title="Poll Information",
            description="Please click/press on the reactions on this message to vote.",
        )
        reactions = [
            ":shericheck:603533980758966293",
            ":sheri:603533981165551616",
            ":sheriX:603533982252138507",
        ]
        message = None
        if can_send(ctx) and can_embed(ctx):
            message = await ctx.send(
                f"**{ctx.author.name}** asks:\n" f"{question}", embed=embed
            )
        else:
            await ctx.author.send(f"I do not have the proper permissions to post in {ctx.channel.mention}")
        if message:
            for x in reactions:
                try:
                    await message.add_reaction(x)
                except discord.Forbidden:
                    pass

    @commands.command(name="colorinf", aliases=["colorinfo"])
    async def colort(self, ctx, color_hex: str):
        async with ctx.channel.typing():
            if color_hex[:1] == "#":
                color_hex = color_hex[1:]

            if color_hex == "random":
                color_hex = "%06x" % randint(0, 0xFFFFFF)

            if not re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', color_hex):
                return await ctx.send("You're only allowed to enter HEX (0-9 & A-F)")
            try:
                color_info = await ExGet.alexflipnote_api(self.bot, f"color/{color_hex}")
            except TypeError:
                return await ctx.send("Either you did not enter a hex value or the api seems to be down.")

            embed = discord.Embed(title=f"Color: {color_info['name']}",
                                  color=color_info['int'])
            embed.set_footer(text="Info Provided by https://alexflipnote.dev")
            embed.set_thumbnail(url=color_info['image'])
            embed.set_image(url=color_info['image_gradient'])
            embed.add_field(name=bold('Hex'),
                            value=color_info['hex'],
                            inline=True)
            embed.add_field(name=bold('Int'),
                            value=color_info['int'],
                            inline=True)
            embed.add_field(name=bold('rgb'),
                            value=color_info['rgb'],
                            inline=True)
            embed.add_field(name=bold('brightness'),
                            value=color_info['brightness'],
                            inline=True)
            if isinstance(ctx.channel, discord.TextChannel):
                if can_send(ctx):
                    if can_embed(ctx):
                        await ctx.send(embed=embed)
                    else:
                        return await ctx.send("I need to be able to embed links in this channel.")
                else:
                    if can_react(ctx):
                        await ctx.message.add_reaction('❌')
                    try:
                        await ctx.author.send(f"I cannot send messages AND/OR embed links in {ctx.channel.mention}.")
                    except discord.Forbidden:
                        return
            else:
                await ctx.send(embed=embed)

    ####################################################################################################################
    #                                  Who said they needed guild information? Eh whatever.
    ####################################################################################################################
    @commands.command()
    @commands.guild_only()
    async def tuser(self, ctx, *, user: discord.Member = None):
        """ Shows user's info """
        async with ctx.channel.typing():
            if not user:
                user = ctx.author
            permissions = ctx.channel.permissions_for(user)
            allowed, denied = "", ""
            for name, value in permissions:
                name = name.replace("_", " ").title()
                if value:
                    allowed += f"+ {name}\n"
                else:
                    denied += f"- {name}\n"

            if user.voice is not None:
                voice = (
                    f"In {user.voice.channel.name} with {len(user.voice.channel.members) - 1} others"
                    if len(user.voice.channel.members) > 1
                    else f"In {user.voice.channel.name} by themselves"
                )
            else:
                voice = "Not connected"
            roles = [x.mention for x in user.roles if x.name != "@everyone"]
            since_created = (ctx.message.created_at - user.created_at).days
            since_joined = (ctx.message.created_at - user.joined_at).days
            user_joined = user.joined_at.strftime("%d %b %Y %H:%M")
            user_created = user.created_at.strftime("%d %b %Y %H:%M")
            member_number = (
                    sorted(ctx.guild.members, key=lambda m: m.joined_at).index(user) + 1
            )
            data = discord.Embed(color=user.color)
            game = f""
            if user.activity is None:
                pass
            else:
                game += (
                    f"{user.activity.type.name.capitalize()} {user.activity.name}"
                    if user.activity.type != "streaming"
                    else f"Streaming **[{user.activity.name}]({user.activity.url})**"
                )

            if roles:
                roles = sorted(
                    roles,
                    key=[
                        x.mention for x in ctx.guild.roles if x.name != "@everyone"
                    ].index,
                )
                roles = ", ".join(roles)
            else:
                roles = "None"

            embed = discord.Embed(
                color=self.bot.color,
                description=f"Name: ``{user.name}``\n"
                            f"Discriminator: ``{user.discriminator}``\n"
                            f"Nickname: ``{user.nick if user.nick is not None else 'Not Set'}``\n",
            )
            embed.add_field(
                name="**Activity**",
                value=f"Voice Chat: ``{voice}``\n"
                      f"Status: {statuses[str(user.status)]}\n"
                      f"Activity: ``{game}``\n",
            )
            embed.set_footer(text=f"Member #{member_number} | User ID:{user.id}")

            data.add_field(name="Voice", value=voice, inline=False)
            data.add_field(name="Top Role", value=user.top_role.name, inline=False)
            data.add_field(name="Activity", value=game, inline=False)
            data.add_field(name="Roles", value=roles, inline=False)

            data.set_footer(text=f"Member #{member_number} | User ID:{user.id}")
            data.set_thumbnail(url=avatar_check(user))

        await ctx.send(embed=embed)

    @commands.command(aliases=["user"])
    @commands.guild_only()
    async def userinfo(self, ctx, *, user: discord.Member = None):
        """ Shows user's info """
        async with ctx.channel.typing():
            if not user:
                user = ctx.author
            permissions = ctx.channel.permissions_for(user)
            allowed, denied = [], []
            for name, value in permissions:
                name = name.replace("_", " ").title()
                allowed.append(name) if value else denied.append(name)
            if user.voice is not None:
                voice = (
                    f"In {user.voice.channel.name} with {len(user.voice.channel.members) - 1} others"
                    if len(user.voice.channel.members) > 1
                    else f"In {user.voice.channel.name} by themselves"
                )
            else:
                voice = "Not connected."
            roles = [x.mention for x in user.roles if x.name != "@everyone"]
            since_created = (ctx.message.created_at - user.created_at).days
            since_joined = (ctx.message.created_at - user.joined_at).days
            user_joined = user.joined_at.strftime("%d %b %Y %H:%M")
            user_created = user.created_at.strftime("%d %b %Y %H:%M")
            member_number = (
                    sorted(ctx.guild.members, key=lambda m: m.joined_at).index(user) + 1
            )
            created_on = f"{user_created}\n({since_created} days ago)"
            joined_on = f"{user_joined}\n({since_joined} days ago)"
            data = discord.Embed(color=user.color)
            game = f"{user.status} {statuses[str(user.status)]} \n"
            if user.activity is None:
                pass
            elif user.activity.type == 4:
                game += f"Custom **{user.activity.state}**"
            else:
                game += (
                    f"{user.activity.type.name.capitalize()} {user.activity.name}"
                    if user.activity.type != "streaming"
                    else f"Streaming **[{user.activity.name}]({user.activity.url})**")

            if roles:
                if len(roles) > 10:
                    roles = f"Too many to list! - {len(roles)} total"
                else:
                    roles = sorted(
                        roles,
                        key=[
                            x.mention for x in ctx.guild.roles if x.name != "@everyone"
                        ].index,
                    )
                    roles = ", ".join(roles)
            else:
                roles = "None"

            eighteen = discord.utils.get(ctx.message.guild.roles, name="18+")
            underage = discord.utils.get(ctx.message.guild.roles, name="Underage")

            if eighteen in user.roles:
                data.add_field(name="Age Gate", value="18+")
            elif underage in user.roles:
                data.add_field(name="Age Gate", value="Underage")

            data.add_field(name="Voice", value=voice, inline=False)
            data.add_field(name="Top Role", value=user.top_role.name, inline=False)
            data.add_field(name="Activity", value=game, inline=False)
            data.add_field(name="Roles", value=roles, inline=False)

            data.set_footer(text=f"Member #{member_number} | User ID:{user.id}")

            name = " ~ ".join((str(user), user.nick)) if user.nick else str(user)

            data.set_author(name=name, url=avatar_check(user))
            data.set_thumbnail(url=avatar_check(user))

            data.add_field(name="Joined Discord on", value=created_on, inline=False)
            data.add_field(name="Joined this server on", value=joined_on, inline=False)
        await ctx.send(embed=data)

    @commands.command(aliases=["gui"])
    async def guserinfo(self, ctx, usid: str):
        """Gives you the info of ANY user."""
        if not usid.isdigit():
            await ctx.send("User IDs only\nExample:`248294452307689473`")
            return
        try:
            user = await self.bot.fetch_user(int(usid))
        except discord.errors.NotFound:
            await ctx.send(f"I can't find this member on discord with the id of {usid}")
            return
        # except:
        #   await ctx.send("❌ An error has occurred.")
        #    return
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        since_created = (ctx.message.created_at - user.created_at).days
        created_on = "{}\n(**__{}__** days ago)".format(user_created, since_created)
        if user.bot is False:
            data = discord.Embed(
                description=("**__User__** ID : " + str(user.id)), color=self.bot.color
            )
        else:
            data = discord.Embed(
                description=("**__Bot__** ID : " + str(user.id)), color=self.bot.color
            )
        data.add_field(name="Joined Discord on", value=created_on)
        if user.avatar_url:
            data.set_author(
                name="{}#{}".format(user.name, user.discriminator), url=user.avatar_url
            )
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(
                name="{}#{}".format(user.name, user.discriminator),
                url=user.default_avatar_url,
            )
            data.set_thumbnail(url=user.default_avatar_url)
        try:
            await ctx.send(embed=data)
        except:
            await ctx.send("❌ **error** You must give this bot embed permissions")

    @staticmethod
    async def member_activity(members):
        stream_count = 0
        listen_count = 0
        for member in members:
            if member.activity:
                if member.activity.type == discord.ActivityType.streaming:
                    stream_count += 1
                if member.activity.type == discord.ActivityType.listening:
                    listen_count += 1
        return listen_count, stream_count

    @staticmethod
    async def get_bans(guild):
        try:
            all_bans = f"{len(await guild.bans()):,}"
        except discord.errors.Forbidden:
            all_bans = "Unknown"
        return all_bans

    @commands.guild_only()
    @commands.group(name="server", aliases=["serverinfo", "guild"])
    async def server_info(self, ctx):
        online = CustomEmotes.get_status_emote("online")
        dnd = CustomEmotes.get_status_emote('dnd')
        idle = CustomEmotes.get_status_emote('idle')
        streamers = CustomEmotes.get_status_emote('streaming')
        listeners = CustomEmotes.get_status_emote('spotify')
        if ctx.invoked_subcommand is None:
            loading_message = await ctx.send(
                f"{CustomEmotes.get_emote(paw=True)} "
                f"Loading server info for {ctx.guild.name}... "
                f"{CustomEmotes.get_emote(paw=True)}"
            )
            days_passed = (ctx.message.created_at - ctx.guild.created_at).days
            created_at = f"{ctx.guild.created_at.strftime('%d %b %Y %H:%M')}! That's over {days_passed:,} days ago!"
            total_voice_channels = len(
                [
                    channel
                    for channel in ctx.guild.channels
                    if isinstance(channel, discord.VoiceChannel)
                ]
            )
            total_channels = len(ctx.guild.channels)
            sfw_channels = len(
                [
                    channel
                    for channel in ctx.guild.channels
                    if isinstance(channel, discord.TextChannel)
                       and not channel.is_nsfw()
                ]
            )
            nsfw_channels = len(
                [
                    channel
                    for channel in ctx.guild.channels
                    if isinstance(channel, discord.TextChannel) and channel.is_nsfw()
                ]
            )
            roles = [role.mention for role in ctx.guild.roles]
            role_list = (
                ", ".join(roles) if len(roles) < 10 else f"``{len(roles)}``"
            )
            total_members = len(ctx.guild.members)
            members = len([member for member in ctx.guild.members if not member.bot])
            member_by_status = Counter(str(m.status) for m in ctx.guild.members)
            spotify, streamer = await self.member_activity(ctx.guild.members)

            emotes = [str(i) for i in ctx.guild.emojis]
            bots = len([member for member in ctx.guild.members if member.bot])
            bans = await self.get_bans(ctx.guild)
            embed = discord.Embed(
                color=self.bot.color,
                description=f"If {ctx.guild.name} has Nitro boost level 1 or 2, you can view the splash (invite background) and/or server banner respectively with the commands below\n"
                            "`furserver splash`\n"
                            "`furserver banner`",
            )
            embed.set_footer(
                icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                text="Created at: " + created_at,
            )
            embed.set_thumbnail(url=icon_check(ctx.guild))
            embed.add_field(
                name=f"**{ctx.guild.name}**",
                value=f"**Owner: ``{ctx.guild.owner}``\n"
                      f"ID: ``{ctx.guild.id}``\n"
                      f"Discord Partner: "
                      f"``{'Yes, they were blessed by Wumpus' if 'PARTNERED' in ctx.guild.features else 'Nope :('}``\n"
                      f"Nitro Boost Level: ``{ctx.guild.premium_tier}``"
                      f" (``{ctx.guild.premium_subscription_count}`` Boosters)\n"
                      f"Server Region: ``{ctx.guild.region}``**",
            )
            embed.add_field(
                name="**Security**",
                value=f"**NSFW Filter:``{ctx.guild.explicit_content_filter}``\n"
                      f"Verification Level: ``{str(ctx.guild.verification_level)}``\n"
                      f"2FA Enabled: ``{'Yes' if ctx.guild.mfa_level > 0 else 'No'}``**",
                inline=False,
            )
            embed.add_field(
                name="**Server Roles**",
                value=f"**Top Role: ``{ctx.guild.roles[len(ctx.guild.roles) - 1]}``\n"
                      f"Server Roles: {role_list}**",
                inline=False,
            )
            embed.add_field(
                name="**Voice Channels**",
                value=f"**Voice Channels: ``{total_voice_channels}``\n"
                      f"AFK Voice Timeout: ``{f'{ctx.guild.afk_timeout} Seconds' if ctx.guild.afk_timeout >= 1 else 'Not Configured'}``\n"
                      f"AFK Voice Channel: ``{'Not configured' if ctx.guild.afk_channel is None else ctx.guild.afk_channel}``**",
                inline=False,
            )

            embed.add_field(
                name="**Text Channels**",
                value=f"**"
                      f"Total Text Channels: ``{total_channels}``\n"
                      f"SFW Text Channels: ``{sfw_channels}``\n"
                      f"NSFW Text Channels: ``{nsfw_channels}``**",
                inline=False,
            )
            embed.add_field(
                name="**Member Statistics**",
                value=f"**Total Members: ``{total_members:,}``\n"
                      f"Real Members: ``{members:,}``\n"
                      f"Robotic Members: ``{bots:,}``\n"
                      f"Banned Members: ``{bans}``\n**",
                inline=False,
            )
            # embed.add_field(
            # name="**Members by status**",
            # value=f"**{online} Online: ``{member_by_status['online']:,}``\n"
            # f"{idle} Idle: ``{member_by_status['idle']:,}``\n"
            # f"{dnd['dnd']} Do Not Disturb: ``{member_by_status['dnd']:,}``\n"
            # f"{streamers['streaming']} Streaming: ``{streamer:,}``\n"
            # f"{spotify['listening']} Listening: ``{spotify:,}``\n"
            # f"{listeners} Offline: ``{member_by_status['offline']:,}``**\n",
            # inline=False,
            # )
            if len(emotes) >= 1:
                embed.add_field(
                    name="**Server Emotes**",
                    value=" ".join(emotes)
                    if len(emotes) < 21
                    else f"{len(emotes)} emotes",
                    inline=False,
                )

            await asyncio.sleep(3)
            await loading_message.edit(
                content=f"ℹ | **{ctx.author.name}**, here is the server info you requested <:thumbs_up:563783885230702622>",
                embed=embed,
            )

    @server_info.command(name="mini", aliases=["smol", "small"])
    async def mini_server(self, ctx):
        loading_message = await ctx.send(
            f"{CustomEmotes.get_emote(paw=True)} "
            f"Loading... "
            f"{CustomEmotes.get_emote(paw=True)}"
        )
        days_passed = (ctx.message.created_at - ctx.guild.created_at).days
        created_at = f"{ctx.guild.created_at.strftime('%d %b %Y %H:%M')} • {days_passed:,} days ago!"
        total_voice_channels = len(
            [
                channel
                for channel in ctx.guild.channels
                if isinstance(channel, discord.VoiceChannel)
            ]
        )
        total_channels = len(ctx.guild.channels)
        total_channels = len(ctx.guild.channels)
        roles = [role.mention for role in ctx.guild.roles]
        total_members = len(ctx.guild.members)
        members = len([member for member in ctx.guild.members if not member.bot])
        bots = len([member for member in ctx.guild.members if member.bot])
        embed = discord.Embed(
            title=ctx.guild.name,
            color=self.bot.color,
        )
        embed.set_footer(
            text="Created: " + created_at,
        )
        embed.set_thumbnail(url=icon_check(ctx.guild))
        embed.add_field(
            name=f"**General Info**",
            value=f"**Owner: ``{ctx.guild.owner}``**\n"
                  f"**ID: ``{ctx.guild.id}``**\n"
                  f"**Boosting: ``{ctx.guild.premium_tier}``**"
                  f" • **``{ctx.guild.premium_subscription_count}``**\n"
                  f"**Region: ``{ctx.guild.region}``**",
            inline=False,
        )
        embed.add_field(
            name="**Channels**",
            value=f"**``{total_channels}``** Text • **``{total_voice_channels}``** Voice\n",
            inline=False,
        )
        embed.add_field(
            name="**Member Count**",
            value=f":bust_in_silhouette:**``{members:,}``** • :robot:**``{bots:,}``**\n",
            inline=False,
        )

        await asyncio.sleep(1)
        await loading_message.edit(
            content=f"<:information_sheri:648192172629426177> | Here is the info you requested!",
            embed=embed,
        )

    @server_info.command(name="splash")
    async def server_splash(self, ctx):
        if "PARTNERED" in ctx.guild.features:
            if ctx.guild.splash:
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"[Splash URL]({ctx.guild.splash_url_as(format='png')})",
                )
                embed.set_image(url=ctx.guild.splash_url_as(format="png"))
                await ctx.send(
                    content=f"ℹ | **{ctx.author.name}**, Here is {ctx.guild.name}'s invite splash image.",
                    embed=embed,
                )
            else:
                await ctx.send(
                    "Looks like the server is apart of discord partners but they didn't set the splash image!"
                )
        else:
            if ctx.guild.premium_tier >= 1:
                if ctx.guild.splash:
                    embed = discord.Embed(
                        color=self.bot.color,
                        description=f"[Splash URL]({ctx.guild.splash_url_as(format='png')})",
                    )
                    embed.set_image(url=ctx.guild.splash_url_as(format="png"))
                    await ctx.send(
                        content=f"ℹ | **{ctx.author.name}**, Here is {ctx.guild.name}'s invite splash image.",
                        embed=embed,
                    )
                else:
                    await ctx.send(
                        "Looks like your server has nitro boost 1 which contains invite splash image but it wasn't set."
                    )
            else:
                await ctx.send(
                    "It looks like your server does not have the requirements for a splash invite image.\n"
                    "Required: Verified Server or Nitro Boost level 1 or Discord Partner"
                )

    @server_info.command(name="banner")
    async def server_banner(self, ctx):
        if "PARTNERED" in ctx.guild.features:
            if ctx.guild.banner:
                embed = discord.Embed(
                    color=self.bot.color,
                    description=f"[Banner URL]({ctx.guild.banner_url_as(format='png')})",
                )
                embed.set_image(url=ctx.guild.banner_url_as(format="png"))
                await ctx.send(
                    content=f"ℹ | **{ctx.author.name}**, Here is {ctx.guild.name}'s banner.",
                    embed=embed,
                )
            else:
                await ctx.send(
                    "Looks like the server is apart of discord partners but they didn't set the banner!"
                )
        else:
            if ctx.guild.premium_tier >= 2:
                if ctx.guild.banner:
                    embed = discord.Embed(
                        color=self.bot.color,
                        description=f"[Banner URL]({ctx.guild.banner_url_as(format='png')})",
                    )
                    embed.set_image(url=ctx.guild.banner_url_as(format="png"))
                    await ctx.send(
                        content=f"ℹ | **{ctx.author.name}**, Here is {ctx.guild.name}'s banner.",
                        embed=embed,
                    )
                else:
                    await ctx.send(
                        "Looks like your server has nitro boost 2 which contains a server banner but it wasn't set."
                    )
            else:
                await ctx.send(
                    "It looks like your server does not have the requirements for a banner.\n"
                    "Required: Verified Server or Nitro Boost level 2 or Discord Partner"
                )

    #######################################################################
    #   Mass Nickname
    ######################################################################

    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.command(aliases=["mn"], no_pm=True)
    @commands.has_permissions(manage_nicknames=True)
    async def massnick(self, ctx, rolename, *, nickname):
        """change everyone's nick"""
        guild = ctx.guild
        roletest = discord.utils.get(guild.roles, name=rolename)
        if not roletest:
            return await send_message(ctx, message=f"I don't see {rolename} in {ctx.guild.name} list of roles.")
        counter = 0
        nc = 0
        rolename = f"{rolename}"
        rolename = rolename.strip("@")
        if rolename.startswith("<@&"):
            roleid = rolename.replace("<@&", "").replace(">", "")
            for droplet in guild.roles:
                if droplet.id == int(roleid):
                    rolename = droplet.name

        catched = [
            members
            for members in guild.members
            if (discord.utils.get(guild.roles, name=rolename) in members.roles)
        ]
        await ctx.send(
            content=f"{CustomEmotes.get_emote(paw=True)} {ctx.author}, I am adding {nickname} to {len(catched):,}"
                    f" members that are apart of {discord.utils.get(guild.roles, name=rolename).mention} role."
        )
        if discord.utils.get(guild.roles, name=rolename):
            member_list = [
                members
                for members in guild.members
                if (discord.utils.get(guild.roles, name=rolename) in members.roles)
            ]
            for user in member_list:
                try:
                    await user.edit(
                        nick=nickname,
                        reason=f"[Mass Nickname] Responsible Moderator: {ctx.author}({ctx.author.id})",
                    )
                    nc += 1
                    await asyncio.sleep(1.5)
                except discord.Forbidden:
                    counter += 1
                except discord.HTTPException:
                    await ctx.send(
                        "<a:rokinsheri:447071660596789279> lol nickname rate limits"
                    )
            await ctx.send(
                content=f"{ctx.author.mention}, I have completed adding {nickname} to {len(member_list):,} members that are apart of {discord.utils.get(guild.roles, name=rolename).mention}.\n"
                        f"Results are as follows:\n"
                        f"- Nicknames successfully changed: {nc:,}\n"
                        f"- Nicknames failed to change: {counter:,}\n"
            )
        else:
            await ctx.send(
                "<:error:391715668598325248> ERROR: Could not find rolename `%s`, please make sure you typed it case "
                "accurate" % rolename
            )

    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.command(aliases=["mnc"], no_pm=True)
    @commands.has_permissions(manage_nicknames=True)
    async def massnickclear(self, ctx, rolename):
        """clears everyone's nickname in a role"""
        guild = ctx.guild
        counter = 0
        nc = 0
        member_list = [
            members
            for members in guild.members
            if (discord.utils.get(guild.roles, name=rolename) in members.roles)
        ]
        msg = await ctx.send(
            content=f"{ctx.author.mention}, I am now processing your request "
                    f"<:fwrok:446318910711529473>\n"
                    f"<a:loading:446087688521777153> Clearing **{len(member_list)}** member("
                    f"s) "
                    f"of **{guild.name}** <a:loading:446087688521777153>"
        )
        if discord.utils.get(guild.roles, name=rolename):
            member_list = [
                members
                for members in guild.members
                if (discord.utils.get(guild.roles, name=rolename) in members.roles)
            ]
            for user in member_list:
                try:
                    await user.edit(
                        nick="",
                        reason=f"Mass Nick Clearing Command ran by {ctx.author}.",
                    )
                    nc += 1
                    await asyncio.sleep(1.5)
                except discord.Forbidden:
                    counter += 1
                except discord.HTTPException:
                    await ctx.send(
                        "<a:rokinsheri:447071660596789279> lol nickname rate limits"
                    )
            await ctx.send(
                content=f"{ctx.author.mention}<:check:437236812189270018> Mass Nick Completed "
                        f"<:check:437236812189270018> \n"
                        f"**{nc}** nicknames cleared in **{guild.name}**\n"
                        f"I have encountered <:error:391715668598325248> {counter} "
                        f"<:error:391715668598325248> errors. Please "
                        f"manually change their names if "
                        f"possible or check my permissions as I cannot modify nicknames on people with"
                        f" roles higher than me."
            )
        else:
            await ctx.send(
                f"<:error:391715668598325248> ERROR: Could not find rolename `{rolename}`, please make sure"
                f" you typed it case accurate"
            )

    #######################################################################
    #   Mass Add Members
    ######################################################################

    @commands.group(name="massadd")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def massadd_index(self, ctx):
        """Massadd Functionality"""
        if ctx.invoked_subcommand is None:
            return await ctx.send_cmd_help(ctx)

    @massadd_index.command(name="all")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def massadd_all(self, ctx, *, role: discord.Role):
        """Adds all members to a role"""
        guild = ctx.message.guild
        users = guild.members
        role_changes = 0
        permission_errors = 0
        if can_send(ctx):
            msg = await ctx.send(
                f"Attempting to add {role.mention} to {guild.member_count:,} members."
            )
            if can_edit_role(ctx, role):
                for user in users:
                    try:
                        await user.add_roles(
                            role,
                            reason=f"🐾 [Utility] Mass+ Role adding executed by {ctx.author}",
                        )
                        role_changes += 1
                    except:
                        permission_errors += 1
                        continue
                await msg.delete()
                await ctx.send(
                    f"Role adding has completed {ctx.author.mention}, I have encountered {permission_errors} errors.\n"
                    f"Added {role.mention} to {role_changes:,} members."
                )
            else:
                return await ctx.send(
                    "I can not add this role to the bots as I cannot manage this role."
                )

    @massadd_index.command(name="users")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def massadd_users(self, ctx, *, role: discord.Role):
        """Adds all users excluding bots."""
        if role in ctx.guild.roles:
            users = list([member for member in ctx.guild.members if not member.bot])
            members = len(users)
            role_changes = 0
            permission_errors = 0
            if can_send(ctx):
                msg = await ctx.send(
                    f"Attempting to add {role.mention} to ``{members:,}`` members."
                )
                if can_edit_role(ctx, role):
                    for user in users:
                        try:
                            await user.add_roles(
                                role,
                                reason=f"🐾 [Utility] Mass+ Role adding executed by {ctx.author}",
                            )
                            role_changes += 1
                        except:
                            permission_errors += 1
                            continue
                else:
                    await ctx.send(
                        "I can not add this role to the user(s)/member(s) as I cannot manage this role."
                    )
                await msg.delete()
                await ctx.send(
                    f"Role adding has completed {ctx.author.mention}, I have encountered {permission_errors} errors.\n"
                    f"Added {role.mention} to {role_changes:,} members."
                )
        else:
            if role is None:
                await ctx.send(
                    "I can't find this role in your server. Are you sure it exists?"
                )

    @massadd_index.command(name="bots")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def massadd_bots(self, ctx, *, role: discord.Role):
        """Adds all bots excluding users."""
        if role in ctx.guild.roles:
            users = list([member for member in ctx.guild.members if member.bot])
            members = len(users)
            role_changes = 0
            permission_errors = 0
            if can_send(ctx):
                msg = await ctx.send(
                    f"Attempting to add {role.mention} to {members:,} bots."
                    f" server/guild members whom are not bots."
                )
                if can_edit_role(ctx, role):
                    for user in users:
                        try:
                            await user.add_roles(
                                role,
                                reason=f"🐾 [Utility] Mass+ Role adding executed by {ctx.author}",
                            )
                            role_changes += 1
                        except:
                            permission_errors += 1
                            continue
                else:
                    return await ctx.send(
                        "I can not add this role to the bots as I cannot manage this role."
                    )
                await msg.delete()
                await ctx.send(
                    f"Role adding has completed {ctx.author.mention}, I have encountered {permission_errors} errors.\n"
                    f"Added {role.mention} to {role_changes:,} bots."
                )
        else:
            await ctx.send(
                "I can't find this role in your server. Are you sure it exists?"
            )

    @commands.group(name="massremove")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def massremove_index(self, ctx):
        """Massremoves Functionality"""
        if ctx.invoked_subcommand is None:
            return await ctx.send_cmd_help(ctx)

    @massremove_index.command(name="all")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def massremove_all(self, ctx, *, role: discord.Role):
        """Removes all members from a role"""
        guild = ctx.message.guild
        users = list(guild.members)
        role_changes = 0
        permission_errors = 0
        if can_send(ctx):
            msg = await ctx.send(
                f"Attempting to remove {role.mention} from ``{len(users):,}`` members."
            )
            if can_edit_role(ctx, role):
                for user in users:
                    try:
                        await user.remove_roles(
                            role,
                            reason=f"🐾 [Utility] Mass- Role removal executed by {ctx.author}",
                        )
                        role_changes += 1
                    except (discord.Forbidden, discord.HTTPException):
                        permission_errors += 1
                        continue
                await msg.delete()
                await ctx.send(
                    f"Role removing has completed {ctx.author.mention}, I have encountered"
                    f" {permission_errors:,} errors.\nRemoved {role.mention} from ``{role_changes:,}`` members."
                )
            else:
                return await ctx.send(
                    "I can not add this role to the bots as I cannot manage this role."
                )

    @massremove_index.command(name="users")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def massremove_users(self, ctx, *, role: discord.Role):
        """Removes all users for the role mentioned excluding bots."""
        if role in ctx.guild.roles:
            users = list([member for member in ctx.guild.members if not member.bot])
            members = len(users)
            role_changes = 0
            permission_errors = 0
            if can_send(ctx):
                msg = await ctx.send(
                    f"Attempting to remove {role.mention} from {members:,} members."
                )
                if can_edit_role(ctx, role):
                    for user in users:
                        try:
                            await user.remove_roles(
                                role,
                                reason=f"🐾 [Utility] Mass- Role removal executed by {ctx.author}",
                            )
                            role_changes += 1
                        except discord.Forbidden:
                            permission_errors += 1
                            continue
                else:
                    await ctx.send(
                        "I can not add this role to the user(s)/member(s) as I cannot manage this role."
                    )
                await msg.delete()
                await ctx.send(
                    f"Role removing has completed {ctx.author.mention}, I have encountered"
                    f" {permission_errors:,} errors.\nRemoved {role.mention} from {role_changes:,} members."
                )
        else:
            if role is None:
                await ctx.send(
                    "I can't find this role in your server. Are you sure it exists?"
                )

    @massremove_index.command(name="bots")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def massremove_bots(self, ctx, *, role: discord.Role):
        """Removes all bots from role excluding users."""
        if role in ctx.guild.roles:
            users = list([member for member in ctx.guild.members if member.bot])
            members = len(users)
            role_changes = 0
            permission_errors = 0
            if can_send(ctx):
                msg = await ctx.send(
                    f"Attempting to remove {role.mention} {members:,} bots."
                )
                if can_edit_role(ctx, role):
                    for user in users:
                        try:
                            await user.remove_roles(
                                role,
                                reason=f"🐾 [Utility] Mass- Role removal executed by {ctx.author}",
                            )
                            role_changes += 1
                        except (discord.Forbidden, discord.HTTPException):
                            permission_errors += 1
                            continue
                else:
                    return await ctx.send(
                        "I can not add this role to the bots as I cannot manage this role."
                    )
                await msg.delete()
                await ctx.send(
                    f"Role removing has completed {ctx.author.mention}, I have encountered"
                    f" {permission_errors:,} errors.\nRemoved {role.mention} from {role_changes:,}."
                )
        else:
            await ctx.send(
                "I can't find this role in your server/guild. Are you sure it exists?"
            )

    @massadd_index.command(name="role")
    @commands.has_permissions(manage_roles=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def massadd_role(self, ctx, role: discord.Role, *, role_add: discord.Role):
        if role in ctx.guild.roles:
            users = discord.utils.get(ctx.guild.roles, name=role.name).members
            role_changes = 0
            permission_errors = 0
            if can_send(ctx):
                msg = await ctx.send(
                    f"Attempting to add {role_add.name} to ``{len(users):,}`` members that has the role ``{role.name}``"
                )
                if can_edit_role(ctx, role_add):
                    for user in users:
                        try:
                            await user.add_roles(
                                role_add,
                                reason=f"🐾 [Utility] Mass- Role add executed by {ctx.author}",
                            )
                            role_changes += 1
                        except (discord.Forbidden, discord.HTTPException):
                            permission_errors += 1
                            continue
                else:
                    return await ctx.send(
                        "I couldn't add this role to them because I do not have the proper permissions to do so.\n"
                        "If you believe this a mistake, please contact support at <https://invite.sheri.bot>"
                    )
                await msg.delete()
                await ctx.send(
                    f"Role adding has completed {ctx.author.mention}, I have encountered {permission_errors} errors.\n"
                    f"Added {role_add.mention} to {role_changes:,} members."
                )

    ####################################################################################################################
    #                                       Permissions
    ####################################################################################################################

    @commands.group(name="perms")
    async def permissions(self, ctx):
        if ctx.invoked_subcommand is None:
            # user = self.bot.get_user(self.bot.user.id)
            user = ctx.guild.me
            perms = ctx.channel.permissions_for(user)
            # perms = ctx.guild.me.permissions_in(ctx.channel)
            perms_we_have = ""
            perms_we_dont = ""
            if isinstance(ctx.channel, discord.TextChannel):
                for perm in perms:
                    if perm[0] not in voice_perms:
                        perm_name = perm[0].replace("_", " ").title()
                        if perm[1]:
                            perms_we_have += f"+\t{perm_name}\n"
                        else:
                            perms_we_dont += f"-\t{perm_name}\n"
            elif isinstance(ctx.channel, discord.VoiceChannel):
                for perm in perms:
                    if perm[0] in voice_perms:
                        perm_name = perm[0].replace("_", " ").title()
                        if perm[1]:
                            perms_we_have += f"+\t{perm_name}\n"
                        else:
                            perms_we_dont += f"-\t{perm_name}\n"
            desc = f"```diff\n{perms_we_have}{perms_we_dont}\n```"
            em = discord.Embed(color=self.bot.color, description=desc)
            em.set_author(name=f"{user.name}'s permissions in {ctx.channel.name}:")
            await ctx.send(embed=em)

    ####################################################################################################################
    #                                   Channel Management
    ####################################################################################################################
    @commands.command(name="nsfw")
    @commands.has_permissions(manage_channels=True)
    async def change_nsfw(self, ctx):
        nsfw_status = ctx.channel.is_nsfw()
        if nsfw_status:
            try:
                await ctx.channel.edit(nsfw=False)
                await ctx.send("You couldn't stand the heat!\n" "**NSFW STATUS: ``OFF~``**")
            except:
                await ctx.send(
                    "Ooops, That didn't go quite right! Either I don't have channel edit permissions or you are not allowed to run this command.")
        else:
            try:
                await ctx.channel.edit(nsfw=True)
                await ctx.send("Oh, You dirty furball 😏\n" "**NSFW STATUS: ``ON~``**")
            except:
                await ctx.send(
                    "Ooops, That didn't go quite right! Either I don't have channel edit permissions or you are not allowed to run this command.")

    @commands.group(name="channel")
    async def channel_management(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=self.bot.color,
                description=f"fur**channel text** - Display Info or change info regarding a text Channel.\n"
                            f"~~fur**channel voice** - Display Info or change info regarding a voice channel\n~~",
            )
            await ctx.send(embed=embed)

    @channel_management.group(name="text")
    async def channel_management_text(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=self.bot.color,
                description="fur**channel text edit** - Shows the help for editing commands\n"
                            "fur**channel text info** - Shows the information of a channel.",
            )
            await ctx.send(embed=embed)

    @channel_management_text.group("edit")
    async def channel_management_text_edit(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=self.bot.color,
                description="fur**channel text edit name #channel channel-name** - Edits the specified channel's name.\n"
                            "fur**channel text edit topic #channel channel-topic** - Edits the specified channel's topic.",
            )
            await ctx.send(embed=embed)

    @channel_management_text_edit.command(name="topic")
    async def channel_management_text_edit_topic(
            self, ctx, channel: discord.TextChannel, *, topic: str
    ):
        if ctx.guild.me.permissions_in(channel).manage_channels:
            await channel.edit(
                topic=topic, reason=f"{ctx.author} ran channel text edit topic :)"
            )
            await ctx.send(
                f"I was able to change the channel name to:"
                f"```fix\n{topic}```\n"
                f"Am I good wolfo?"
            )

    @channel_management_text.command(name="info")
    async def channel_management_info(self, ctx, channel: discord.TextChannel):
        embed = discord.Embed(color=self.bot.color, title="Channel Information")
        embed.add_field(
            name=f"{channel.name} ({channel.id})",
            value=f"Nsfw Channel: ``{'yes' if channel.is_nsfw() else 'No'}``\n"
                  f"Slow Mode: ``{'No' if channel.slowmode_delay == 0 else channel.slowmode_delay}``\n",
            inline=False,
        )
        if channel.topic is not None and len(channel.topic) <= 1200:
            embed.add_field(name="Channel Topic", value=f"{channel.topic}")
        else:
            embed.add_field(
                name="Channel Topic",
                value="Channel does not have a topic, or it is too big to view here.",
                inline=False,
            )
        await ctx.send(embed=embed)

    ####################################################################################################################
    #                                  Role Managment
    ####################################################################################################################
    @commands.group()
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=self.bot.color,
                description="fur**role info role/ID** - Shows generic role info\n"
                            "fur**role edit color/name color hex/name\n"
                            '- Name needs to be surrounded by quotes if there are spaces! "role name"',
            )
            await ctx.send(embed=embed)

    @role.command(name="info")
    async def role_info(self, ctx, *, role: discord.Role = None):
        if role is None:
            return await ctx.send("Unable to find role.")
        else:
            role_members = len(
                [member for member in ctx.guild.members if role in member.roles]
            )
            embed = discord.Embed(
                color=role.color,
                title=ctx.guild.name,
                description=f"{role.mention} | \{role.mention}",
            )
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(
                name=ctx.guild.owner, icon_url=avatar_check(ctx.guild.owner)
            )
            embed.add_field(
                name=f"{role.name}[{role.id}]",
                value=f"**Color: ``{role.color}``\n"
                      f"Hoisted: ``{role.hoist}``\n"
                      f"Mentionable: ``{role.mentionable}``\n"
                      f"Members with role: ``{role_members}``\n**",
            )
            embed.set_footer(
                icon_url=self.bot.footer_emote, text=f"Info requested by {ctx.author}."
            )
            await ctx.send(embed=embed)

    @role.command(name="edit")
    async def role_edit(self, ctx, role: discord.Role = None, *args):
        prolec = role.color
        if role is None:
            return await ctx.send("Unable to find role.")
        try:
            if args[0] == "color":
                if args[1]:
                    color = discord.Color(int(args[1].replace("#", ""), 16))
                    await role.edit(color=color)
                    await ctx.send("Done.")
                else:
                    await ctx.send("Must supply a hex code.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage this role.")

    ####################################################################################################################
    #               Reminders
    ####################################################################################################################

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

    @commands.command(name="deletereminder", aliases=["delreminder"])
    async def delete_reminder(self, ctx, reminder_id: int):
        """Deletes a reminder
            Usage; furdelreminder reminderid"""
        deleted = await Reminder(ctx).delete(reminder_id)
        if deleted == "UPDATE 1":
            return await ctx.send("I have deleted that reminder!")
        await ctx.send_error("Hmm I couldn't seem to find that reminder for you, make sure the id is correct!")

    ##############
    # Misc Utility
    ##############

    @commands.command(name='revimg', aliases=['revimage'])
    async def reverse_image_search(self, ctx, url=None):
        """
        Reverse image search!
        usage:  [p]revimg <image-link> or file upload
        """
        try:
            if url is not None:
                await ctx.message.delete()
            if url is None:
                try:
                    url = ctx.message.attachments[0].url
                except IndexError:
                    return await ctx.send('No URL or Image detected. Please try again!')
            embed = discord.Embed(title='Reverse Image Details', color=16776960)
            embed.add_field(name="Sauce", value=f'[Sauce Image Results](https://saucenao.com/search.php?url={url})',
                            inline=True)
            embed.add_field(name="Google",
                            value=f'[Google Image Results](https://www.google.com/searchbyimage?&image_url={url})',
                            inline=True)
            embed.add_field(name="TinEye", value=f'[Tineye Image Results](https://www.tineye.com/search?url={url})',
                            inline=True)
            embed.add_field(name="IQBD", value=f'[IQBD Image Results](https://iqdb.org/?url={url})', inline=True)
            embed.add_field(name="Yandex",
                            value=f'[Yandex Image Results](https://yandex.com/images/search?url={url}&rpt=imageview)',
                            inline=True)
            await ctx.send(embed=embed)
        except discord.NotFound:
            await ctx.send(
                'Oopsie woopsie, Looks like your message was deleted by a bot since it contained a link! Try uploading an image.'
                ' if that doesn\'t work then you need to tell your server owners to allow links and images.')

    @commands.command(name='decancer')
    async def decancer(self, ctx, user: discord.Member):
        cancered_name = user.display_name
        fixed_name = user.display_name.encode("ASCII", "ignore").decode('UTF-8')
        if cancered_name != fixed_name:
            if len(fixed_name) >= 3:
                fixed_name = Names.get_name()
                if can_manage_user(user):
                    try:
                        await user.setnick(name=fixed_name, reason="Cancer Name")
                        await ctx.send(f"Changed user's name to {fixed_name}. No unicode names :(")
                    except discord.Forbidden:
                        return
        else:
            await ctx.send("I can't make this name any better...")

    @commands.group(name="giveaway", aliases=['ga'])
    async def giveaway(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @giveaway.command(name="create", aliases=['c'])
    async def giveaway_create(self, ctx):
        """Create giveaways"""
        giveaway_begin = await ctx.send("Wuf, How long would this giveaway last?")
        duration = ""

        def check(m):
            return m.author == ctx.message.author

        try:
            duration = await self.bot.wait_for('message', check=check, timeout=30)

            if duration:
                duration_parsed = parse_time(duration.content)
                await ctx.send(f"{duration_parsed}")

        except asyncio.TimeoutError:
            await ctx.send("You took to long <:Sheri_cry:604040023003758598> You will need to rerun the command!")

def setup(bot):
    bot.add_cog(Utility(bot))
