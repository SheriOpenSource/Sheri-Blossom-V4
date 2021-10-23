self.sentry.capture_exception(exception)
self.log.error(exception)
embed = self.error_embed(exception)
if isinstance(ctx.channel, discord.TextChannel):
    try:
        if can_send(ctx) and can_embed(ctx):
            return await ctx.send(embed=embed)
        elif can_send(ctx):
            return await ctx.send(
                "Oopsie, I have encountered an error, "
                "This has been logged and my developers will work on it as fast as possible!\n "
                "If this continues to persist please contact us at "
                "https://sheri.bot/support"
            )
    except (discord.Forbidden, discord.HTTPException):
        return
elif isinstance(ctx.channel, discord.DMChannel):
    try:
        await ctx.author.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        return

    @commands.command()
    async def tserver(self, ctx):
        """Shows Guild/Server Information."""
        roles = [role.mention for role in ctx.guild.roles]
        role_list = ", ".join(roles) if len(roles) < 10 else f"``{len(roles)}`` roles"
        emotes = [str(i) for i in ctx.guild.emojis]

        avatar = (
            ctx.message.author.avatar_url
            if ctx.message.author.avatar
            else self.bot.user.default_avatar_url
        )

        class Secret:
            id = 0
            roles = [ctx.guild.default_role]

        secret_member = Secret()
        secret_channels = 0
        secret_voice = 0
        text_channels = 0
        voice_channels = 0
        sfw_text_channels = 0
        nsfw_text_channels = 0
        for channel in ctx.guild.channels:
            perms = channel.permissions_for(secret_member)
            is_text = isinstance(channel, discord.TextChannel)
            is_voice = isinstance(channel, discord.VoiceChannel)
            text_channels += 1
            if is_text and not perms.read_messages:
                secret_channels += 1
            elif not is_text and (not perms.connect or not perms.speak):
                secret_voice += 1
            elif is_voice and perms.connect:
                voice_channels += 1
            elif is_text and channel.is_nsfw():
                nsfw_text_channels += 1
            elif is_text and not channel.is_nsfw():
                sfw_text_channels += 1

        sfw_percentage = round(sfw_text_channels / text_channels * 100)
        nsfw_percentage = round(nsfw_text_channels / text_channels * 100)

        member_by_status = Counter(str(m.status) for m in ctx.guild.members)
        streamcount = 0
        listencount = 0
        for member in ctx.guild.members:
            if member.activity:
                if member.activity.type == discord.ActivityType.streaming:
                    streamcount += 1
                if member.activity.type == discord.ActivityType.listening:
                    listeningcount += 1
        try:
            all_bans = f"{len(await ctx.guild.bans()):,}"
        except discord.errors.Forbidden:
            all_bans = "Unknown"
        days_passed = (ctx.message.created_at - ctx.guild.created_at).days
        created_at = f"``{ctx.guild.created_at.strftime('%d %b %Y %H:%M')}``\nThat's over ``{days_passed:,}`` days ago!"
        members = set(ctx.guild.members)
        offline = filter(lambda m: m.status is discord.Status.offline, members)
        offline = set(offline)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        bot_percentage = round(len(bots) / ctx.guild.member_count * 100)
        voice_locked = round(voice_channels / secret_voice * 100)
        users = members - bots

        desc = (
            f"**Owner** : [{ctx.guild.owner}]({ctx.guild.owner.id})\n"
            f"**Users** : {len(users)} ({len(users - offline)} online)\n"
            f"**Bots** : {len(bots)} ({len(bots - offline)} online)\n"
            f"**Bans** : {all_bans} \n\n"
        )
        images = ''
        if ctx.guild.banner:
            images += f"[Banner Url]({ctx.guild.banner_url_as(format='png')})\n"

        if ctx.guild.splash:
            images += f"[Splash Url]({ctx.guild.splash_url_as(format='png')})\n"

        e = discord.Embed(color=self.bot.color,
                          description=f"**Owner: ``{ctx.guild.owner}``\n"
                                      f"Server ID: ``{ctx.guild.id}``\n"
                                      f"Discord Partner:  "
                                      f"``{'Yes, they were blessed by Wumpus' if 'PARTNERED' in ctx.guild.features else 'Nope :('}``\n"
                                      f"{images if images else ''}"
                                      f"Nitro Boost Level ``{ctx.guild.premium_tier}``\n"
                                      f"Nitro Boosters: ``{ctx.guild.premium_subscription_count}``\n"
                                      f"Members: ``{len(users):,}``\n"
                                      f"Banned Members: ``{'Unknown' if all_bans == 'Unknown' else all_bans}``\n"
                                      f"Bots: ``{len(bots):,}`` (``{bot_percentage}%``)\n**"
                          )
        e.add_field(
            name="**Security**",
            value=f"**NSFW Filter: ``{ctx.guild.explicit_content_filter}``\n"
                  f"Verification Level: ``{str(ctx.guild.verification_level)}``\n"
                  f"2FA Enabled: ``{'Yes' if ctx.guild.mfa_level > 0 else 'No'}``**", inline=True
        )
        e.add_field(
            name="Server Roles",
            value=f"Top Role:  ``{ctx.guild.roles[len(ctx.guild.roles) - 1]}``\n"
                  f"Server Roles:  {role_list}", inline=True
        )
        e.add_field(name="**Voice Channels**",
                    value=f"**Voice Region: {ctx.guild.region}\n"
                          f"Voice Channels: {voice_channels} ({secret_voice} {voice_locked}% locked)\n"
                          f"AFK Voice Timeout: {f'{ctx.guild.afk_timeout} Seconds' if ctx.guild.afk_timeout >= 1 else 'Not Configured'}\n"
                          f"AFK Voice Channel: {'Not configured' if ctx.guild.afk_channel is None else ctx.guild.afk_channel}**",
                    inline=True)
        e.add_field(name="**Text Channels**",
                    value=f"**Default Channel: {ctx.guild.channels[0].mention}\n"
                          f"Total Text Channels: ``{text_channels}`` ({secret_channels} secret)\n"
                          f"SFW Text Channels: ``{sfw_text_channels}`` (``{sfw_percentage}%`` is SFW)\n"
                          f"NSFW Text Channels: ``{nsfw_text_channels}`` (``{nsfw_percentage}%`` is NSFW)**",
                    inline=False)

        e.add_field(
            name="**Members by status**",
            value=f"{statuses['online']} ``{member_by_status['online']:,}``\n"
                  f"{statuses['idle']} ``{member_by_status['idle']:,}``\n"
                  f"{statuses['dnd']} ``{member_by_status['dnd']:,}``\n"
                  f"{statuses['streaming']} ``{streamcount:,}``\n"
                  f"{statuses['listening']} ``{listeningcount}``"
                  f"{statuses['offline']} ``{member_by_status['offline']:,}``\n",
            inline=False)

        e.add_field(
            name="Roles",
            value=", ".join(roles) if len(roles) < 10 else f"``{len(roles)}`` roles",
        )
        if len(emotes) > 1:
            e.add_field(
                name="Emotes",
                value=" ".join(emotes) if len(emotes) < 21 else f"{len(emotes)} emotes",
            )
        e.set_footer(
            text="Server info requested by: " + str(ctx.message.author), icon_url=avatar
        )

        e.set_thumbnail(url=icon_check(ctx.guild))
        await ctx.send(embed=e)

    @commands.command(aliases=["server", "guild"])
    async def serverinfo(self, ctx):
        """Shows Guild/Server Information."""
        roles = [role.name.replace("@", "@\u200b") for role in ctx.guild.roles]
        emotes = [str(i) for i in ctx.guild.emojis]
        avatar = (
            ctx.message.author.avatar_url
            if ctx.message.author.avatar
            else self.bot.user.default_avatar_url
        )

        class Secret:
            id = 0
            roles = [ctx.guild.default_role]

        secret_member = Secret()
        secret_channels = 0
        secret_voice = 0
        text_channels = 0
        for channel in ctx.guild.channels:
            perms = channel.permissions_for(secret_member)
            is_text = isinstance(channel, discord.TextChannel)
            text_channels += 1
            if is_text and not perms.read_messages:
                secret_channels += 1
            elif not is_text and (not perms.connect or not perms.speak):
                secret_voice += 1
        voice_channels = len(ctx.guild.channels) - text_channels
        member_by_status = Counter(str(m.status) for m in ctx.guild.members)
        streamcount = 0
        for member in ctx.guild.members:
            if member.activity:
                if member.activity.type == discord.ActivityType.streaming:
                    streamcount += 1
        try:
            all_bans = str(len(await ctx.guild.bans()))
        except discord.errors.Forbidden:
            all_bans = "Unknown"
        days_passed = (ctx.message.created_at - ctx.guild.created_at).days
        created_at = f"{ctx.guild.created_at.strftime('%d %b %Y %H:%M')}\n**That's over __{days_passed}__ days ago!**"
        members = set(ctx.guild.members)
        offline = filter(lambda m: m.status is discord.Status.offline, members)
        offline = set(offline)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        users = members - bots
        desc = (
            f"**Owner** : [{ctx.guild.owner}]({ctx.guild.owner.id})\n"
            f"**Users** : {len(users)} ({len(users - offline)} online)\n"
            f"**Bots** : {len(bots)} ({len(bots - offline)} online)\n"
            f"**Bans** : {all_bans} \n\n"
        )
        e = discord.Embed(description=desc, color=self.bot.color)
        e.set_author(name=ctx.guild.name, icon_url=icon_check(ctx.guild))
        e.set_thumbnail(url=icon_check(ctx.guild))
        if ctx.guild.splash:
            e.set_image(url=ctx.guild.splash_url)
        channels_text = (
            f"\n**Text**: {text_channels} ({secret_channels} secret)\n"
            f"**Voice**: {voice_channels} ({secret_voice} locked)"
        )
        e.add_field(
            name="Guild information\n",
            value=f"**Id**: \n[{ctx.guild.id}]({ctx.guild.id})\n"
                  + f"**Region**: {ctx.guild.region}\n"
                    f"**Large guild**: {'Yes' if ctx.guild.large else 'No'}\n"
                  + f"**Created At**:\n{created_at}\n",
        )

        e.add_field(
            name="Channels",
            value=f"**Highest role**: \n{ctx.guild.roles[len(ctx.guild.roles) - 1]}\n"
                  f"**Default channel**: \n{ctx.guild.channels[0].name}\n"
                  f"**Channels**: {channels_text}\n",
        )
        e.add_field(
            name="Members by status",
            value=f"{statuses['online']} **{member_by_status['online']}**\n"
                  f"{statuses['idle']} **{member_by_status['idle']}**\n"
                  f"{statuses['dnd']} **{member_by_status['dnd']}**\n"
                  f"{statuses['offline']} **{member_by_status['offline']}**\n"
                  "**Members streaming**:\n"
                  f"{statuses['streaming']} **{streamcount:,}**\n",
        )
        e.add_field(
            name="Security",
            value=f"**NSFW Filter**: ``{ctx.guild.explicit_content_filter}``\n"
                  f"**Verification Level**: \n{str(ctx.guild.verification_level)}\n",
        )

        e.add_field(
            name="Specials",
            value=f"**Discord Partnered**: \n"
                  f"{'Yes, they were blessed by Wumpus' if 'PARTNERED' in ctx.guild.features else 'Nope :('}\n"
                  f"**Nitro Boost Level**:\n {ctx.guild.premium_tier}\n"
                  f"**Number of Boosters**:\n {ctx.guild.premium_subscription_count}",
        )
        e.add_field(
            name="Roles",
            value=", ".join(roles) if len(roles) < 10 else f"{len(roles)} roles",
        )
        if len(emotes) > 1:
            e.add_field(
                name="Emotes",
                value=" ".join(emotes) if len(emotes) < 21 else f"{len(emotes)} emotes",
            )
        e.set_footer(
            text="Server info requested by: " + str(ctx.message.author), icon_url=avatar
        )
        await ctx.send(embed=e)

@commands.command(name="addguild", hidden=True)
    @commands.check(is_owner)
    async def add_guilds(self, ctx):
        await ctx.send("Starting.............")
        for guild in self.bot.guilds:
            await add_guild(self.bot.pool, guild)
            print(f"Added {guild.name} to the database.")

    @commands.command(name="adduser", hidden=True)
    @commands.check(is_owner)
    async def add_users(self, ctx):
        await ctx.send("Starting.............")
        for member in self.bot.users:
            if not member.bot:
                await add_user(self.bot.pool, member)
                print(f"Added {member} to the database.")


@commands.command(name="daily")
@commands.guild_only()
@commands.cooldown(1, 86400, type=commands.BucketType.user)
async def dailies(self, ctx, user: discord.Member = None):
    # If user is true, gift the daliy to that person with increased values
    embed = discord.Embed(color=self.bot.color)

    if user:
        coin_rewards = randint(150, 400)
        box_rewards = randint(1, 10)
        key_rewards = randint(1, 10)
        msg = await ctx.send(
            f"**{ctx.author.name}** has gifted **{user.name}** their dalies, See what you got!"
        )
        await asyncio.sleep(5)
    else:
        user = ctx.author
        coin_rewards = randint(100, 300)
        box_rewards = randint(1, 5)
        key_rewards = randint(1, 5)
        msg = await ctx.send(
            f"**{ctx.author.name}**, you have claimed your dalies, See what you got!"
        )
        await asyncio.sleep(5)

    # Contact the db for user info
    user_info = await self.get_user_currency(ctx, user)
    # Current user Values
    keys, boxes, coins = user_info["keys"], user_info["boxes"], user_info["coins"]
    # Math time
    updated_coins, updated_boxes, updated_keys = (
        coins + coin_rewards,
        boxes + box_rewards,
        keys + key_rewards,
    )
    # Update the database
    await self.update_user_currency(
        ctx, user, updated_keys, updated_boxes, updated_coins
    )

    # image logic
    if ctx.channel.is_nsfw():
        # pull an image from /yiff for dailies
        api = await Get.main_api(self.bot, "yiff")
        embed.set_image(url=api["url"])
    else:
        # Pull an image from /mur for dalies
        api = await Get.main_api(self.bot, "mur")
        embed.set_image(url=api["url"])

    # Build the info and then send
    if can_embed(ctx) and can_send(ctx):
        embed.add_field(
            name="Claimed Rewards",
            value=f"Keys: ``{key_rewards}``\n"
                  f"Boxes: ``{box_rewards}``\n"
                  f"Coins: ``{coin_rewards}``",
        )
        embed.add_field(
            name="Current Inventory",
            value=f"Keys: ``{keys}`` > ``{updated_keys}``\n"
                  f"Boxes: ``{boxes}`` > ``{updated_boxes}``\n"
                  f"Coins: ``{coins}`` > ``{updated_coins}``",
        )
        await msg.edit(embed=embed)

        @commands.command(aliases=["bal"])
        @commands.guild_only()
        async def balance(self, ctx, user: discord.Member = None):
            if not user:
                user = ctx.author

            cmd = self.bot.get_command("daily")
            daily_warning = None
            if cmd.is_on_cooldown(ctx) is False and user == ctx.author:
                daily_warning = "**Your dailies collection is available! Do `furdaily` to get more earnings!**"

            user_info = await self.get_user_currency(ctx, user)
            keys, boxes, coins = user_info["keys"], user_info["boxes"], user_info["coins"]
            api = await Get.main_api(self.bot, "mur")

            post = discord.Embed(title=f"{user.name}'s Balance!", color=self.bot.color)

            if daily_warning:
                post.description = daily_warning

            post.add_field(name="Collections:",
                           value=f"{coins:,} coins\n"
                                 f"{keys:,} keys\n"
                                 f"{boxes:,} boxes")
            post.set_image(url=api["url"])

            await ctx.send(embed=post)

    """
                # Member Logs
                async with self.bot.pool.acquire() as db:
                    try:
                        logging_config = await db.fetchrow(
                            "SELECT member_channel, logs_enabled, default_channel, logs_embed FROM botsettings_guild WHERE id=$1",
                            before.guild.id)

                        if logging_config['logs_enabled']:
                            if logging_config['member_channel']:
                                try:
                                    channel = self.bot.get_channel(int(logging_config['member_channel']))
                                except Exception as e:
                                    capture_exception(e)
                            else:
                                try:
                                    if logging_config['default_channel']:
                                        channel = self.bot.get_channel(int(logging_config['default_channel']))
                                except Exception as e:
                                    capture_exception(e)
                            if before.nick != after.nick:
                                if logging_config['logs_embed']:
                                    nick_changes = discord.Embed(color=0xF48C0D,
                                                                 description=f"**{before} has changed their nickname**\n"
                                                                             f"Before: {before.nick}\n"
                                                                             f"After: {after.nick}") \
                                        .set_author(name=before.name, icon_url=avatar_check(before))
                                    try:
                                        await channel.send(embed=nick_changes)
                                    except discord.Forbidden:
                                        return
                                else:
                                    message = f"{before} has changed their nickname to {after.nick}"
                                    try:
                                        await channel.send(message)
                                    except discord.Forbidden:
                                        return
                    except Exception as e:
                        capture_exception(e)
    """


    @commands.command()
    async def balt(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author

        cmd = self.bot.get_command("daily")
        daily_warning = None
        if cmd.is_on_cooldown(ctx) is False and user == ctx.author:
            daily_warning = "Your dailies collection is avaliable! Run `furdaily`"

        # user_info = await self.get_user_currency(ctx, user)
        async with ctx.bot.pool.acquire() as db:
            user_info = await db.fetchrow(
                """SELECT coins, boxes, keys, foxes, bunnies, wolves, foxesall, wolvesall, bunniesall  
                FROM botsettings_user WHERE id = $1""",
                user.id,
            )
        keys, boxes, coins, wolves, foxes, bunnies = user_info["keys"], user_info["boxes"], user_info["coins"], \
                                                     user_info["wolves"], user_info["foxes"], user_info["bunnies"]

        digital = "utils/fonts/SYDNIE.TTF"
        dig_font = ImageFont.truetype(digital, size=80)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    'https://cdn.discordapp.com/attachments/346892627108560902/638579696312778753/image0.png') as raw_response:
                bg = BytesIO(await raw_response.read())

                bg = Image.open(bg).convert('RGBA')

        bg = bg.resize((1250, 950), Image.ANTIALIAS)
        output = io.BytesIO()
        bg.save(output, format='PNG')

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    'https://i.pinimg.com/originals/9d/f1/e3/9df1e357e6b4e99f4a7e8ae5263274d6.png') as raw_response:
                bg1 = BytesIO(await raw_response.read())

                bg1 = Image.open(bg1).convert('RGBA')

        bg1 = bg1.resize((100, 100), Image.NEAREST)

        bg1.save(output, format='PNG')

        async with aiohttp.ClientSession() as session:
            async with session.get('https://img.pngmix.com/pm/rabbits/rabbits_003.png') as raw_response:
                bg2 = BytesIO(await raw_response.read())

                bg2 = Image.open(bg2).convert('RGBA')

        bg2 = bg2.resize((80, 80), Image.NEAREST)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    'https://images.vexels.com/media/users/3/140314/isolated/preview/645b3ddb021b03c735970864318c255e-fox-silhouette-by-vexels.png') as raw_response:
                bg3 = BytesIO(await raw_response.read())

                bg3 = Image.open(bg3).convert('RGBA')

        bg3 = bg3.resize((100, 100), Image.NEAREST)

        bg2.save(output, format='PNG')

        im = Image.new('RGBA', (1250, 950), (0, 0, 0, 0))
        im_draw = ImageDraw.Draw(im)
        if wolves > 999:
            wolves = "+999"
        if bunnies > 999:
            bunnies = "+999"
        if foxes > 999:
            foxes = "+999"
        im_draw.rectangle((40, 75, 1200, 600), fill=(25, 223, 50, 255))
        im.paste(bg, (0, 0), bg)
        im_draw.text((200, 215), text=f"Coins: {coins:,}", fill=(55, 25, 55, 200), font=dig_font)
        im_draw.text((200, 275), text=f"Boxes: {boxes:,}", fill=(55, 25, 55, 200), font=dig_font)
        im_draw.text((200, 335), text=f"Keys: {keys:,}", fill=(55, 25, 55, 200), font=dig_font)
        im.paste(bg1, (190, 400), bg1)
        im_draw.text((300, 400), text=f"{wolves}", fill=(55, 25, 55, 200), font=dig_font)
        im.paste(bg2, (490, 400), bg2)
        im_draw.text((600, 400), text=f"{bunnies}", fill=(55, 25, 55, 200), font=dig_font)
        im.paste(bg3, (790, 400), bg3)
        im_draw.text((900, 400), text=f"{foxes}", fill=(55, 25, 55, 200), font=dig_font)

        buffer = BytesIO()
        im.save(buffer, 'png')
        buffer.seek(0)
        post = discord.Embed()
        post.set_image(url="attachment://bal.png")

        await ctx.send(file=dFile(fp=buffer, filename='bal.png'), content=daily_warning, embed=post)

    @commands.command()
    async def resetdaily(self, ctx, user: discord.Member = None):
        if ctx.author.id != 106511913222955008:
           return await ctx.send("This is Somas Skittles command. *bap* Bad furry!")
        else:
            if user is None:
                user = ctx.author

            async with ctx.bot.pool.acquire() as db:
                await db.execute("UPDATE botsettings_user SET next_daily=$1 WHERE id=$2",
                                 None, user.id)

            await ctx.send("It's been resetted Queen Somas.")

    @commands.command()
    async def daily2(self, ctx, user: discord.Member = None):
        cooldown_format = ""
        if user is None:
            user = ctx.author
            received = f"ℹ | **{ctx.author.name}**, You have collected your dailies."
            cool_down_message = f"{ctx.author.name}, You have already collected your dailies for the day.\n" \
                                f"You can try again in {cooldown_format}"
            message = "You have collected your dailies! See what you have obtained below!"
        else:
            received = f"ℹ | **{user.name}**, {ctx.author.name} has given you their dailies today!"
            cool_down_message = f"{ctx.author.name}, You can't gift your dailies to {user.name} because you already collected/gave your dailies.\n" \
                                f"You can try again in {cooldown_format}"
            message = f"You have given {user.name} your dailies for today!"
        streak_end = False
        coin_rewards = randint(100, 300)
        box_rewards = randint(1, 5)
        key_rewards = randint(1, 5)
        # delta = relativedelta(ctx.message.created_at, ctx.author.created_at)

        async with ctx.bot.pool.acquire() as db:
            cooldown_data = await db.fetchval("SELECT next_daily FROM botsettings_user WHERE id=$1",
                                              ctx.author.id)
            user_info = await db.fetchrow(
                """SELECT coins, boxes, dailies_streak, keys, foxes, bunnies, wolves 
                FROM botsettings_user WHERE id = $1""",
                user.id,
            )
            keys, boxes, coins = user_info["keys"], user_info["boxes"], user_info["coins"]

            now = datetime.datetime.now(pytz.utc)
            delta = cooldown(cooldown_data, now)
            next_message = now + datetime.timedelta(days=1)
            if delta.hours:
                cooldown_format += f"{delta.hours} hours"
            if delta.minutes:
                cooldown_format += f" {delta.minutes} minutes"
            if delta.seconds:
                cooldown_format += f" {delta.seconds} seconds"
            cooldown_format += "."
            # delta = relativedelta(str(now), str(cool_down))
            if user == ctx.author:
                cool_down_message = f"{ctx.author.name}, You have already collected your dailies for the day.\n" \
                                    f"You can try again in {cooldown_format}"
            else:
                cool_down_message = f"{ctx.author.name}, You can't gift your dailies to {user.name} because you already collected/gave your dailies.\n" \
                                    f"You can try again in {cooldown_format}"

            if cooldown_data:
                if delta.seconds >= 0:
                    return await ctx.send(cool_down_message)

            msg = await ctx.send(
                f"ℹ | **{ctx.author.name}**, {message}"
            )
            await asyncio.sleep(2)

            if ctx.channel.is_nsfw():
                # pull an image from /yiff for dailies
                api = await Get.main_api(self.bot, "yiff")
                url = api["url"]
            else:
                # Pull an image from /mur for dalies
                api = await Get.main_api(self.bot, "mur")
                url = api["url"]

            spell = list("Furry")

            # Count the times its been used.
            token = user_info['dailies_streak']
            print(token)
            print(len(spell))
            day = delta.days
            print(day)
            if not day:
                day = 0
            if day > -1:  # The streak continuation window
                if token >= len(spell):
                    streak_end = True
                    token = 0
                    streak = "You've recieved a **BONUS** from your streak! Come back tomorrow to continue the streak again."
                else:
                    token += 1
                    streak = "You are currently on a streak to spell out furry! Come back tomorrow for the next letter :)"
            else:
                if token != 0:
                    token = 0
                    streak = "You've lost your streak! You can come back tomorrow to begin your streak."
                else:
                    token = 0
                    streak = "Come back tomorrow to begin your streak."

                    # Math time
            if streak_end is False:
                updated_coins, updated_boxes, updated_keys = (
                    coins + coin_rewards,
                    boxes + box_rewards,
                    keys + key_rewards,
                )
            else:
                coin_rewards = int(coin_rewards * 2.5)
                box_rewards = int(box_rewards * 2.5)
                key_rewards = int(key_rewards * 2.5)

                updated_coins, updated_boxes, updated_keys = (
                    coins + coin_rewards,
                    boxes + box_rewards,
                    keys + key_rewards,
                )

            # Database things
            await db.execute(
                "UPDATE botsettings_user SET dailies_streak=$1, boxes=$2, keys=$3, coins=$4, next_daily=$6 WHERE id=$5",
                token, updated_boxes, updated_keys, updated_coins, user.id, next_message)

            word = []

            i = 0

            while i < token:
                word.append(spell[i])

                i += 1

                if i == 20:
                    break

            word = "".join(word)
            gui = await self.daily_gui(
                ctx,
                user,
                url,
                word,
                streak_end,
                coin_rewards,
                box_rewards,
                key_rewards,
                updated_coins,
                updated_boxes,
                updated_keys,
            )

            post = discord.Embed(
                color=0x836193, description="Spell out furry and get a bonus!"
            )
            post.add_field(
                name="Image Info",
                value=f"**Link to image [here]({api['url']})\n"
                      f"Something wrong? Report it [here]({api['report_url']})**",
                inline=True,
            )
            post.set_author(
                icon_url="https://cdn.discordapp.com/attachments/515925482617700392/635686603741724682/logo.png",
                url="https://sheri.bot/",
                name="https://sheri.bot",
            )
            post.set_thumbnail(url=avatar_check(user))
            post.set_footer(
                icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                text="Image hosted on https://sheri.bot/",
            )
            post.set_image(url=url)

            # await ctx.send(f"The Delta Hours: {delta.hours}")

            await ctx.send(embed=post, file=dFile(fp=gui, filename="daily_card.png"))
            await msg.edit(
                content=f"{received}\n{streak}"
            )

    async def daily_gui(
            self,
            ctx,
            user,
            url,
            word,
            streak_end,
            coin_rewards,
            box_rewards,
            key_rewards,
            updated_coins,
            updated_boxes,
            updated_keys,
    ):
        font = "utils/fonts/NOVASQUARE.TTF"
        sexyfont = "utils/fonts/AKRONIM-REGULAR.TTF"

        if streak_end is False:
            color = [255, 255, 255]
        else:
            color = [0, 255, 0]

        stat_font = ImageFont.truetype(font, size=45)
        up_font = ImageFont.truetype(font, size=30)
        bonus_font = ImageFont.truetype(sexyfont, size=100)

        im = Image.new("RGBA", (1000, 300), (0, 0, 169, 0))
        im_draw = ImageDraw.Draw(im)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://cdn.discordapp.com/attachments/436367441224925193/635691464193474570/sheridailyF.png"
            ) as raw_response:
                banner = BytesIO(await raw_response.read())

                banner = Image.open(banner)

        im.paste(banner, (0, 0))

        # This is going to be annoying
        w1, h = im_draw.textsize(f"{updated_keys:,}", font=stat_font)
        w2, h = im_draw.textsize(f"{updated_coins:,}", font=stat_font)
        w3, h = im_draw.textsize(f"{updated_boxes:,}", font=stat_font)
        w4, h = im_draw.textsize(word, font=bonus_font)

        # Keys
        im_draw.text(
            (((450 - w1) / 2), 105),
            text=f"{updated_keys:,}",
            fill=(255, 255, 255, 200),
            font=stat_font,
        )
        im_draw.text(
            (200, 155),
            text=f"+{key_rewards}",
            fill=(color[0], color[1], color[2], 100),
            font=up_font,
        )

        # Coins
        im_draw.text(
            (((1000 - w2) / 2), 105),
            text=f"{updated_coins:,}",
            fill=(255, 255, 255, 200),
            font=stat_font,
        )
        im_draw.text(
            (450, 155),
            text=f"+{coin_rewards}",
            fill=(color[0], color[1], color[2], 100),
            font=up_font,
        )

        # Daily Word
        im_draw.text(
            (((1000 - w4) / 2), 200),
            text=word,
            fill=(255, 255, 255, 200),
            font=bonus_font,
        )

        # Boxes
        im_draw.text(
            (((450 - w3) / 2 + 550), 105),
            text=f"{updated_boxes:,}",
            fill=(255, 255, 255, 200),
            font=stat_font,
        )
        im_draw.text(
            (750, 155),
            text=f"+{box_rewards}",
            fill=(color[0], color[1], color[2], 100),
            font=up_font,
        )

        buffer = BytesIO()
        im.save(buffer, "png")
        buffer.seek(0)

        return buffer

f"**{CustomEmotes.get_emote(False)['sheri emotes']['commands']}[Commands](https://sheri.bot/commands) "
                                          f"{Get_emote['sheri emotes']['api']}[API](https://sheri.bot/api/v2/) "
                                          f"{Get_emote['sheri emotes']['link']}[Website](https://sheri.bot/)\n"
                                          f"🏥[ Support](https://invite.sheri.bot/) "
                                          f"{Get_emote['statuses']['online']}[Status](https://status.sheri.bot/) "
                                          f"{Get_emote['sheri emotes']['book']}[Lore](https://sheri.bot/lore)\n"
                                          f"{Get_emote['service emotes']['twitter']}[Twitter](https://twitter.sheri.bot/)"
                                          f"{Get_emote['service emotes']['patreon']} [Patreon](https://patreon.sheri.bot/)**\n"


@commands.command(name="help")
async def help(self, ctx):
    guilds = "{:,}".format(len(self.bot.guilds))
    users = "{:,}".format(
        len([member for member in self.bot.users if not member.bot])
    )
    embed = discord.Embed(
        color=self.bot.color,
        description="Like sheri? Consider spreading "
                    "the word about sheri and checking out our social media",
    )
    embed.set_author(name="Sheri's Help File", icon_url=avatar_check(self.bot.user))
    embed.set_thumbnail(url=avatar_check(self.bot.user))
    embed.add_field(
        name="Sheri's Help",
        value=f"**{CustomEmotes.get_emote(False)['sheri emotes']['commands']}[Commands](https://sheri.bot/commands) "
              f"{Get_emote['sheri emotes']['api']}[API](https://sheri.bot/api/v2/) "
              f"{Get_emote['sheri emotes']['link']}[Website](https://sheri.bot/)\n"
              f"🏥[Support](https://invite.sheri.bot/) "
              f"{Get_emote['statuses']['online']}[Status](https://status.sheri.bot/) "
              f"{Get_emote['sheri emotes']['book']}[Lore](https://status.sheri.bot/)**",
    )
    embed.add_field(
        name="Social Media",
        value=f"**{Get_emote['service emotes']['twitter']}[Twitter](https://twitter.sheri.bot/)\n**",
    )
    embed.add_field(name="Dashboard", value=f"https://sheri.bot/settings")
    embed.add_field(
        name="Hosting isn't cheap!",
        value=f"{Get_emote['service emotes']['patreon']} [Patreon](https://patreon.sheri.bot/)",
    )
    embed.set_footer(
        icon_url=self.bot.footer_emote,
        text="Sheri has been coded with <3 in python 3.7.3",
    )
    if can_embed(ctx):
        await ctx.send(
            embed=embed,
            content=f"{CustomEmotes.get_emote(True)}| "
                    f"**Guilds: ``{guilds}``** | **Users: ``{users}``** | **Version: ``4.0``** | "
                    f"{CustomEmotes.get_emote(True)}",
        )
    else:
        await ctx.send(
            "It appears that i am unable to send embedded messages here. "
            "Make sure I can send embedded links/messages for your best experience with me"

            @ commands.command(name="say", pass_context=True)
            @ commands.check(authorized)
            async

        def say(self, ctx, *, msg):
            await ctx.message.delete()
            await ctx.send(msg)


    @commands.command(name="colorinf", aliases=["colorinfo"])
    async def view(self, ctx, *, hex: str = None):
        """Views the current color for this guild. Add "fraction" to the end for more info."""
        if isinstance(ctx.message.channel, discord.abc.PrivateChannel):
            return await ctx.send("Command is disabled in DMs.")
        if hex is None:
            return await ctx.send("Need a color hex")
        gid = ctx.message.guild.id
        async with self.session.get(
                f"http://www.thecolorapi.com/id?hex={hex}&format=json"
        ) as resp:
            result = await resp.json()
        desc = (
            f'**Name:**\n    **Value:** {result["name"]["value"]}\n'
            f'    **Closest named Hex:** {result["name"]["closest_named_hex"]}\n'
            f'    **Match Closest?:** {result["name"]["exact_match_name"]}\n'
            f'    **Distance from closest:** {result["name"]["distance"]}\n'
            f'**Hex:**\n    **Value:** {result["hex"]["value"]}\n'
            f'    **Clean:** {result["hex"]["clean"]}\n'
            f"    **Decimal:** {hex}\n"
            f'**RGB:**\n    **Value:** {result["rgb"]["value"]}\n'
        )
        if ctx.message.content.endswith("fraction"):
            desc += (
                f"    **Fraction:**\n"
                f'        **R:** {result["rgb"]["fraction"]["r"]}\n'
                f'        **G:** {result["rgb"]["fraction"]["g"]}\n'
                f'        **B:** {result["rgb"]["fraction"]["b"]}\n'
            )
        desc += f'**HSL:**\n    **Value:** {result["hsl"]["value"]}\n'
        if ctx.message.content.endswith("fraction"):
            desc += (
                f"    **Fraction:**\n"
                f'        **H:** {result["hsl"]["fraction"]["h"]}\n'
                f'        **S:** {result["hsl"]["fraction"]["s"]}\n'
                f'        **L:** {result["hsl"]["fraction"]["l"]}\n'
            )
        desc += f'**HSV:**\n    **Value:** {result["hsv"]["value"]}\n'
        if ctx.message.content.endswith("fraction"):
            desc += (
                f"    **Fraction:**\n"
                f'        **H:** {result["hsv"]["fraction"]["h"]}\n'
                f'        **S:** {result["hsv"]["fraction"]["s"]}\n'
                f'        **V:** {result["hsv"]["fraction"]["v"]}\n'
            )
        desc += f'**CMYK:**\n    **Value:** {result["cmyk"]["value"]}\n'
        if ctx.message.content.endswith("fraction"):
            desc += (
                f"    **Fraction:**\n"
                f'        **C:** {result["cmyk"]["fraction"]["c"]}\n'
                f'        **M:** {result["cmyk"]["fraction"]["m"]}\n'
                f'        **Y:** {result["cmyk"]["fraction"]["y"]}\n'
                f'        **K:** {result["cmyk"]["fraction"]["k"]}\n'
            )
        desc += f'**XYZ:**\n    **Value:** {result["XYZ"]["value"]}\n'
        if ctx.message.content.endswith("fraction"):
            desc += (
                f"    **Fraction:**\n"
                f'        **X:** {result["XYZ"]["fraction"]["X"]}\n'
                f'        **Y:** {result["XYZ"]["fraction"]["Y"]}\n'
                f'        **Z:** {result["XYZ"]["fraction"]["Z"]}'
            )
        em = discord.Embed(color=self.bot.color, description=desc)
        em.set_thumbnail(url="http://www.colorhexa.com/%s.png" % str(hex))
        await ctx.send(embed=em)


    #@rp_index.command(name="edit")
    #@commands.guild_only()
    #async def rp_editing(self, ctx, slot : str, *, character):
        #slot_picks = ["name", "age","species", "bio", "img", "gender", "sexuality"]

        #slot = slot.lower()
        #if slot not in slot_picks:
            #return await ctx.send("Invalid edit field:\n"
                         #"`name`\n`age`\n`gender`\n`sexuality`\n`species`\n`bio` - description\n`img` - image")
        #if character is None:
            #return await ctx.send(
                #"You must enter the name of the character you want to see."
            #)

        #db_character = await self.get_rp_character(ctx, character)

        #if db_character is None:
            #return await ctx.send(
                #"I couldn't find a character by this name. Are you sure your spelling is correct and any necessary capitalization is included?"
            #)
        #else:
            #while True:
                #slot = "image"

                #def check(m):
                    #return isinstance(m.channel, discord.DMChannel) and m.author == ctx.author

                #if slot == "name":
                    #await ctx.author.send(
                        #"What would you like to name your character? Please keep in mind that names are case-sensitive. Any capitalization you include here "
                        #"will need to be included whenever you use the ``furchar view`` command, otherwise I will return an error when attempting to fetch your character's information.")
                    #try:
                        #response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    #except asyncio.TimeoutError:
                        #return await ctx.author.send(
                            #"You took too long to respond. Please run the character creation command again."
                        #)
                    #value = response.content
                    #break
                #elif slot == "age":
                    #await ctx.author.send(f"How old is {character}?\n")
                    #try:
                        #response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    #except asyncio.TimeoutError:
                        #return await ctx.author.send(
                            #"You took too long to respond. Please run the character creation command again."
                        #)
                    #if response.content.isdigit():
                        #if int(response.content) >= 18:
                            #value = response.content
                        #elif int(response.content) <= 17:
                            #value = response.content
                            #if db_character["nsfw"]:
                                #return await ctx.send(
                                    #"I'm sorry, but you are not allowed to store NSFW cub characters in me.\n"
                                    #"NSFW cub is **NOT** allowed on Discord."
                                #)
                        #break
                    #elif not response.content.isdigit():
                        #value = response.content
                    #if not response:
                        #break
                    #break
                #elif slot == "gender":
                    #await ctx.author.send(f"What is {character}'s gender?")
                    #try:
                        #response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    #except asyncio.TimeoutError:
                        #return await ctx.author.send(
                            #"You took too long to respond. Please run the character creation command again."
                        #)
                    #value = response.content
                    #break
                #elif slot == "species":
                    #await ctx.author.send(f"What is {character}'s species?")
                    #try:
                        #response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    #except asyncio.TimeoutError:
                        #return await ctx.author.send(
                            #"You took too long to respond. Please run the character creation command again."
                        #)
                    #value = response.content
                    #break
                #elif slot == "bio":
                    #await ctx.author.send(
                        #f"Any additional information about {character}?"
                    #)
                    #try:
                        #response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    #except asyncio.TimeoutError:
                        #return await ctx.author.send(
                            #"You took too long to respond. Please run the character creation command again."
                        #)
                    #value = response.content
                    #break
                #elif slot == "img":
                    #slot = "image"

                    #await ctx.author.send(
                        #"In order to complete your entry for your character, please upload an image or provide a URL "
                        #"that represents your character. Image URLs must be `.png`, `.jpg`, or `.mjpg` file type.\n"
                        #"**If your character is NSFW, please only provide a URL as Discord does not allow NSFW "
                        #"content to be sent to bots.**\n"
                    #)
                    #try:
                        #response = await ctx.bot.wait_for("message", timeout=60, check=check)
                    #except asyncio.TimeoutError:
                        #return await ctx.author.send(
                            #"You took too long to respond. Please run the character creation command again."
                        #)
                    #img_url = None
                    #try:
                        #img_url = response.attachments[0].url
                    #except (KeyError, IndexError):
                        #pass
                    #if (
                            #response.content.endswith(".png")
                            #or response.content.endswith(".jpg")
                            #or response.content.endswith(".mjpg")
                    #):
                        #img_url = response.content
                    #elif img_url is not None:
                        #pass
                    #else:
                        #return await ctx.author.send(
                            #"You provided a URL that isn't acceptable. Please run the character creation command again."
                        #)
                    ## db_character["image"] = img_url
                    #value = img_url
                    #break

            #await self.rp_editor(ctx, character, slot, value)
            #await ctx.send("Editing completed!")


guild_info = await db.fetchrow(
                    "SELECT moderation_channel, logs_embed, logs_enabled FROM botsettings_guild WHERE id=$1",
                    ctx.guild.id,
                )
                if guild_info["logs_enabled"]:
                    if guild_info["logs_embed"]:
                        embed = discord.Embed(
                            title=f":no_entry_sign: {member} Banned :no_entry_sign:",
                            color=self.bot.danger_color,
                            timestamp=ctx.message.created_at,
                        )
                        embed.add_field(
                            name="User",
                            value=member.mention if real_member else member,
                            inline=True,
                        )
                        embed.set_thumbnail(url=avatar_check(member))
                        embed.set_footer(text=f"User ID: {member.id}")
                        embed.add_field(
                            name="Moderator", value=ctx.author.mention, inline=True
                        )
                        embed.add_field(name="Reason", value=reason, inline=False)
                        await self.bot.get_channel(
                            guild_info["moderation_channel"]
                        ).send(embed=embed)
                    else:
                        await self.bot.get_channel(
                            guild_info["moderation_channel"]
                        ).send(
                            f":no_entry_sign: {ctx.author.mention} has banned "
                            f"{member.mention if real_member else member}\nReason: {reason}"
                        )
owners = [
    173237945149423619,  # Kanin
    139800365393510400,  # Waspy,
    248294452307689473,  # Tails
    252362165456076800,  # Kyle <3
    83006253919375360,  # Atoro
    493308716427509761,  # Talvi
    106511913222955008,  # Alphy
    443276440168038401,  # Kano,
    209219778206760961,  # Jazzy
    158292798368382976,  # DeviousKR
    406707961214402568  # Spacey Da Dragon
]


@commands.Cog.listener()
async def on_message(self, message):
    ctx = await self.bot.get_context(message)
    core = self.get_cmdlist()
    ban_cmd = ["reload", "load", "unload", "update", "cmdlist"]

    if ctx.valid:
        if not str(ctx.command) in core.cmd:
            if str(ctx.command) not in ban_cmd:
                core.cmd.append(str(ctx.command))
                core.count.append(1)
                core.last = str(ctx.command)
        else:
            if str(ctx.command) not in ban_cmd:
                dex = core.cmd.index(f"{str(ctx.command)}")
                core.count[dex] += 1
                core.last = str(ctx.command)


def is_owner_check(ctx):
    return ctx.message.author.id in [
        173237945149423619,  # Kanin
        106511913222955008,  # Alphy
        139800365393510400,  # Waspy,
        248294452307689473,  # Tails
        493308716427509761,  # Talvi
        252362165456076800,  # Kyle <3
        83006253919375360,  # Atoro
        209219778206760961,  # Jazzy
        158292798368382976,  # DeviousKR
    ]


@commands.command(hidden=True)
@commands.check(is_owner)
async def ssh(self, ctx, command: str):
    msg = await ctx.send("<a:lewding:468520251789934612> Processing.......")
    command = command.replace("`", "").split()
    command_run = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output = command_run.stdout.read().decode()
    paged = pagify(output)
    for page in paged:
        desc = "```fix\n{0}```".format(page)
        message = (
                "Command was successful! Here is the output from the update.\n" + desc
        )
        await ctx.send(content=message)


# paws = CustomEmotes.get_emote(paw=True)
# embed = discord.Embed(color=self.bot.color,
# title=f"{paws} {answer.author.display_name} caught the wild {animal_name[animal]}! {paws}",
# description=f"{'I sent the image to your DMs ' if wants_dm else 'Want the image sent to your DMs? Go to https://sheri.bot/settings/profile/ to enable the option.'}\n"
#            f"**{answer.author.display_name}** now has ``{new_count} {animal}``")
# embed.set_footer(icon_url='https://cdn.discordapp.com/emojis/457367016823848970.png?v=1',
# text="Image Hosted on: https://sheri.bot/ | Powered by: https://furhost.net")
# embed.set_author(icon_url=image['url'], url=image['url'],
# name="Click here for the image that was caught")
# await ctx.send(
#    embed=embed,
#    delete_after=20,
# )

if wants_dm:
    e = discord.Embed(
        color=self.bot.color,
        description=f"You caught {animal_name[animal]} in "
                    f"**{ctx.guild.name}**.\n"
                    f"Here is the image. [**{animal_name[animal]} image**]({image['url']})",
    )
    e.set_image(url=image['url'])
    try:
        await answer.author.send(
            f"You now have {new_count} {animal} ^_^", embed=e
        )
    except discord.Forbidden:
        pass
