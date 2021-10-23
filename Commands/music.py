"""
This is an example cog that shows how you would make use of Lavalink.py.
This example cog requires that you have python 3.6 or higher due to the f-strings.
"""
import math
import re

import discord
import lavalink
from discord.ext import commands

radios = {
    "house": "http://mp3.stream.tb-group.fm/ht.mp3",
    "dance": "http://mp3.stream.tb-group.fm/tb.mp3",
    "hardstyle": "http://mp3.stream.tb-group.fm/hb.mp3",
    "trance": "http://mp3.stream.tb-group.fm/trb.mp3",
    "techno": "http://mp3.stream.tb-group.fm/clt.mp3",
    "hardcore": "http://mp3.stream.tb-group.fm/ct.mp3",
    "dnb": "http://mp3.stream.tb-group.fm/tt.mp3",
    "b985": "https://ad-im-cmg.streamguys1.com/atl985/atl985-sgplayer-aac?amsparams=playerid%3ASGplayer%3Bskey%3A1575779245634%3B&awparams=playerid%3ASGplayer%3B",
    "my961": "https://16813.live.streamtheworld.com/WHNNFMAAC.aac?dist=tg&tdsdk=js-2.9&pname=TDSdk&pversion=2.9&banners=300x250&sbmid=2fb3847e-bd3a-40f0-b41e-7c111b5a058b",
    "star941": "https://18003.live.streamtheworld.com/WSTRFM_SC?sbmid=4b72179a-4425-4bf9-bc90-56d6da8fd03b&DIST=CBS&TGT=radiocomPlayer&SRC=CBS&lsid=cookie:d34ae0a0-2b90-4f81-a879-861d6c3cdf7d",
    "lazer1033": "http://16923.live.streamtheworld.com/KAZRFMAAC.aac?pname=StandardPlayerV4&pversion=4.19.2-014&csegid=888&dist=triton-web&tdsdk=js-2.9&banners=300x250%2C728x90&sbmid=b6269445-461f-4b56-e286-f01d090fc3ba",
    "rock108": "http://14533.live.streamtheworld.com/KFMWFMAAC.aac?dist=tg&tdsdk=js-2.9&pname=TDSdk&pversion=2.9&banners=300x250&sbmid=fe3d8d56-1ce2-4f62-f42a-4356c311d28d"
}
station_choices = [x for x, y in radios.items()]

url_rx = re.compile("https?:\\/\\/(?:www\\.)?.+")

embeds_perm = (
    "Awe, looks like I'm missing a required permission please update my permissions please "
    "set Embed Links to approve, thank you."
)


async def is_in_voice(self, ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        usrchannel = ctx.author.voice.channel
    else:
        usrchannel = 0
        ctx.send("you must be in a voice chat to use this command")
        return


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(
                bot, "lavalink"
        ):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(346702890368368640)
            # bot.lavalink.add_node("10.1.1.131", 4437, "4dmin", "us", "API SERVER")
            bot.lavalink.add_node(
                "69.197.162.19", 5437, "4dmin", "us", "Central Server"
            )
            # bot.lavalink.add_node(
            #    "96.233.60.54", 5437, "4dmin", "us", "Gl!tch's Instance"
            # )
            # bot.lavalink.add_node(
            #    "96.233.60.54", 5437, "4dmin", "eu", "Gl!tch's Instance"
            # )
            # bot.lavalink.add_node(
            #    "96.233.60.54", 5437, "4dmin", "asia", "Gl!tch's Instance"
            # )
            bot.add_listener(bot.lavalink.voice_update_handler, "on_socket_response")
        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    @staticmethod
    async def format_time(time):
        seconds = (time / 1000) % 60
        minutes = (time / (1000 * 60)) % 60
        hours = (time / (1000 * 60 * 60)) % 24
        if "%02d" % hours == "00":
            return "%02d:%02d" % (minutes, seconds)
        else:
            return "%02d:%02d:%02d" % (hours, minutes, seconds)

    @staticmethod
    async def get_emoji(query: str):
        if "https://twitch.tv/" in query:
            emoji = "<:Twitch:316197473024606229>"
        elif "https://soundcloud.com/" in query:
            emoji = "<:SoundCloud:429105941808414752>"
        elif "https://vimeo.com/" in query:
            emoji = "<:Vimeo:496162803917258752>"
        elif "https://mixer.com/" in query or "https://beam.pro/" in query:
            emoji = "<:Mixer:496162976500547624>"
        elif "https://www.youtube.com" in query or "https://youtu.be/" in query:
            emoji = "<:YouTube:429102198920839188>"
        elif query.startswith("ytsearch:"):
            emoji = "<:YouTube:429102198920839188>"
        else:
            emoji = " "
        return emoji

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.TrackStartEvent):
            c = event.player.fetch("channel")
            if c:
                c = self.bot.get_channel(c)
                if c:
                    player = event.player
                    if player.current.stream:
                        dur = "LIVE"
                    else:
                        dur = await self.format_time(player.current.duration)
                    emoji = await self.get_emoji(player.current.uri)
                    requsr = self.bot.get_user(player.current.requester)
                    if isinstance(c, discord.abc.PrivateChannel):
                        return
                    else:
                        em = discord.Embed(
                            color=self.bot.color,
                            title="Now Playing:",
                            description=f"{emoji} **[{player.current.title}]({player.current.uri})**",
                        )
                    em.add_field(name="Duration:", value=f"{dur}")
                    em.add_field(name="Requested by:", value=f"{requsr}")
                    em.set_thumbnail(url=self.thumbnail(player.current.uri))
                    em.set_author(name="Sheri Music", icon_url=self.bot.user.avatar_url)
                    messages = False
                    async for message in c.history(limit=5):
                        for x in message.embeds:
                            if (
                                    message.author.name == self.bot.user.name
                                    and x.title == "Now Playing:"
                            ):
                                messages = True
                                await message.edit(embed=em)
                    if not messages:
                        await c.send(embed=em)

        elif isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            c = event.player.fetch("channel")
            if c:
                c = self.bot.get_channel(c)
                if c:
                    await c.send("I finished the Queue!")
            await self.connect_to(guild_id, None)
            # Disconnect from the channel -- there's nothing else to play.

    @staticmethod
    def thumbnail(url):
        """ Returns the video thumbnail. Could be an empty string. """
        if "youtube" in url:
            return "https://img.youtube.com/vi/{}/default.jpg".format(
                url.split("?v=")[1]
            )

        return ""

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.
        return guild_check

    async def connect_to(self, guild_id: int, channel_id: str):
        """ Connects to the given voicechannel ID. A channel_id of `None` means disconnect. """
        guild = self.bot.get_guild(guild_id)
        await self.bot.shards[guild.shard_id].ws.voice_state(str(guild_id), channel_id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None:
            return
        if self.bot.user in before.channel.members:
            if len(before.channel.members) == 1:
                player = self.bot.lavalink.player_manager.get(member.guild.id)
                player.queue.clear()
                await player.stop()
                await self.connect_to(member.guild.id, None)

    @commands.command(aliases=["p"])
    @commands.guild_only()
    async def play(self, ctx, *, query: str):
        """ Searches and plays a song from a given query. """
        await ctx.send("Notice: Youtube has been making this command unreliable. Consider using furradio if your "
                       "song from youtube can not be played OR try a direct url from a different provider"
                       " etc: soundcloud, vimeo.")
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        # query = query.strip("<>")
        # if not url_rx.match(query):
        # return await ctx.send(
        # "Please provide a twitch/mixer/vimeo/sound cloud/ link for me to play for you!"
        # )
        # if "youtube" in query or "youtu.be" in query:
        # return await ctx.send(
        # "Sheri will no longer provide support for streaming through Youtube as youtube is banning people for doing this."
        # )

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send("Nothing found!")

        embed = discord.Embed(color=self.bot.color)

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Playlist Enqueued!"
            embed.description = (
                f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
            )
        else:
            track = results["tracks"][0]
            embed.title = "Track Enqueued"
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            player.add(requester=ctx.author.id, track=track)
        await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()

    @commands.command(name="radio")
    @commands.guild_only()
    async def radio(self, ctx, station: str = None):
        stations = ", ".join(station_choices)
        if station is None:
            return await ctx.send(f"Valid radio stations are: {stations}")
        if station in station_choices:
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)
            results = await player.node.get_tracks(radios[station])
            embed = discord.Embed(color=self.bot.color)

            if not results["tracks"]:
                return await ctx.send("Services Unavailable")

            track = results["tracks"][0]
            embed.title = "Radio Enqueued"
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            player.add(requester=ctx.author.id, track=track)
            await ctx.send(embed=embed)
            if not player.is_playing:
                await player.play()
        else:

            await ctx.send(f"Invalid station. The valid stations are {stations}")

    @commands.command()
    @commands.guild_only()
    async def seek(self, ctx, *, seconds: int):
        """ Seeks to a given position in a track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)

        await ctx.send(f"Moved track to **{lavalink.utils.format_time(track_time)}**")

    @commands.command(aliases=["forceskip"])
    @commands.guild_only()
    async def skip(self, ctx):
        """ Skips the current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Not playing.")
        current = f"[{player.current.title}]({player.current.uri})"
        await player.skip()
        embed = discord.Embed(
            color=self.bot.color, description=current, title="Skipped"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        """ Stops the player and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Not playing.")

        player.queue.clear()
        await player.stop()
        await ctx.send("⏹ | Stopped.")

    @commands.command(aliases=["np", "n", "playing"])
    @commands.guild_only()
    async def now(self, ctx):
        """ Shows some stats about the currently playing song. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.current:
            return await ctx.send("Nothing playing.")
        position = lavalink.utils.format_time(player.position)
        if player.current.stream:
            duration = "🔴 LIVE"
        else:
            duration = lavalink.utils.format_time(player.current.duration)
        song = f"**[{player.current.title}]({player.current.uri})**\n({position}/{duration})"

        embed = discord.Embed(
            color=discord.Color.blurple(), title="Now Playing", description=song
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["q"])
    @commands.guild_only()
    async def queue(self, ctx, page: int = 1):
        """ Shows the player's queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("Nothing queued.")
        if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
            return await ctx.send(embeds_perm.format(ctx.author.voice.channel))

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ""
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f"`{index + 1}.` [**{track.title}**]({track.uri})\n"

        embed = discord.Embed(
            colour=discord.Color.blurple(),
            description=f"**{len(player.queue)} tracks**\n\n{queue_list}",
        )
        embed.set_footer(text=f"Viewing page {page}/{pages}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["resume"])
    @commands.guild_only()
    async def pause(self, ctx):
        """ Pauses/Resumes the current track. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Not playing.")

        if player.paused:
            await player.set_pause(False)
            await ctx.send("⏯ | Resumed")
        else:
            await player.set_pause(True)
            await ctx.send("⏯ | Paused")

    @commands.command(aliases=["vol"])
    @commands.guild_only()
    async def volume(self, ctx, volume: int = None):
        """ Changes the player's volume (0-1000). """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not volume:
            return await ctx.send(f"🔈 | {player.volume}%")

        await player.set_volume(
            volume
        )  # Lavalink will automatically cap values between, or equal to 0-1000.
        await ctx.send(f"🔈 | Set to {player.volume}%")

    @commands.command()
    @commands.guild_only()
    async def shuffle(self, ctx):
        """ Shuffles the player's queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("Nothing playing.")

        player.shuffle = not player.shuffle
        await ctx.send("🔀 | Shuffle " + ("enabled" if player.shuffle else "disabled"))

    @commands.command(aliases=["loop"])
    @commands.guild_only()
    async def repeat(self, ctx):
        """ Repeats the current song until the command is invoked again. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Nothing playing.")

        player.repeat = not player.repeat
        await ctx.send("🔁 | Repeat " + ("enabled" if player.repeat else "disabled"))

    @commands.command()
    @commands.guild_only()
    async def remove(self, ctx, index: int):
        """ Removes an item from the player's queue with the given index. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("Nothing queued.")

        if index > len(player.queue) or index < 1:
            return await ctx.send(
                f"Index has to be **between** 1 and {len(player.queue)}"
            )

        removed = player.queue.pop(index - 1)  # Account for 0-index.

        await ctx.send(f"Removed **{removed.title}** from the queue.")

    @commands.command()
    @commands.cooldown(1, 30)
    @commands.guild_only()
    async def find(self, ctx, *, query):
        """ Lists the first 10 search results from a given query. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not query.startswith("ytsearch:") and not query.startswith("scsearch:"):
            query = "ytsearch:" + query

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send("Nothing found.")

        tracks = results["tracks"][:10]  # First 10 results

        o = ""
        for index, track in enumerate(tracks, start=1):
            track_title = track["info"]["title"]
            track_uri = track["info"]["uri"]
            o += f"`{index}.` [{track_title}]({track_uri})\n"

        embed = discord.Embed(color=discord.Color.blurple(), description=o)
        await ctx.send(embed=embed)

    @commands.command(aliases=["dc"])
    @commands.guild_only()
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send("Not connected.")

        if not ctx.author.voice or (
                player.is_connected
                and ctx.author.voice.channel.id != int(player.channel_id)
        ):
            return await ctx.send("You're not in my voicechannel!")

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await ctx.send("*⃣ | Disconnected.")

    @commands.command(name="players")
    async def players(self, ctx):
        await ctx.send(
            f"I'm currently playing on {len(self.bot.lavalink.player_manager)} servers"
        )

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )
        # Create returns a player if one exists, otherwise creates.

        should_connect = ctx.command.name in (
            "play"
        )  # Add commands that require joining voice to work.

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You need to be in a voice channel floof ball.")

        if not player.is_connected:
            if not should_connect:
                await ctx.send("I'm not connected :(")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if (
                    not permissions.connect or not permissions.speak
            ):  # Check user limit too?
                await ctx.send(
                    "I need the `CONNECT` and `SPEAK` permissions floof ball."
                )

            player.store("channel", ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.send(
                    "You need to be in my voice channel in order to ask me to play something!"
                )


def setup(bot):
    bot.add_cog(Music(bot))
