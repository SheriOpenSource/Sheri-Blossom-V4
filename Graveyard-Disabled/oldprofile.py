if member is None:
    member = ctx.author

async with ctx.bot.pool.acquire() as db:
    i_d = member.id
    user_info = await db.fetchrow(
        """SELECT * FROM botsettings_user WHERE id=$1""", i_d
    )

    if not user_info:
        await ctx.send("Some Error has occurred")
    else:

        # Create Levels class and get level info so we don't have to duplicate code here
        level_class = Levels(self.bot)
        level_info = await level_class.get_member_info(db, member)
        # Owners check
        owners = user_info["owner"]

        # Donor check
        is_donor = True if user_info["premium"] else False

        # Dev Check
        is_dev = user_info["developer"]

        # Staff checking
        try:
            support_server = self.bot.get_guild(id=346892627108560901)
            staff_role = discord.utils.get(
                support_server.roles, id=484003210739318785
            )

            is_staff = staff_role.members
        # Staff and Dev check cannot occur in DMs, If command issued in DMs make False so Profile does not fail.
        except AttributeError:

            is_staff = False

        # Get spouses from DB info and turn into actual user objects
        spouses = []
        for user_id in user_info["marry"]:
            try:
                spouse = self.bot.get_user(int(user_id))
                spouses.append(str(spouse))
            except discord.HTTPException:
                spouses.append(f"Unknown spouse (ID: {user_id})")
        spouses_string = ", ".join(spouses)
        if not spouses:
            spouses_string = "Nobody"

        base = 300
        if ctx.channel.is_nsfw():
            image = await Get.main_api(self.bot, "yiff")
            image = image["url"]
        else:
            image = await Get.main_api(self.bot, "mur")
            image = image["url"]

        async with aiohttp.ClientSession() as session:
            async with session.get(image) as raw_response:
                bg = BytesIO(await raw_response.read())

                bg = Image.open(bg).convert("RGBA")

        bg = resizer(1500, 1250, bg)

        if member.avatar:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f"{member.avatar_url}?size=1024"
                ) as raw_response:
                    pfp = BytesIO(await raw_response.read())

                    pfp = Image.open(pfp)

            pfp = resizer(base, base, pfp)

        #######################################
        #
        #       TEXT AND FONTS
        #
        ######################################

        user_tag = f"{member.name}"
        font = "utils/fonts/NOVASQUARE.TTF"
        basicfont = "utils/fonts/ARIALUNI.TTF"

        #########################################
        # Member allocating
        #   ###########

        choosen2 = list(member.name)

        # Fonts
        ########################
        header_font = ImageFont.truetype(font, size=50)
        stat_font = ImageFont.truetype(font, size=45)

        if len(choosen2) < 16:
            mem_letter = ImageFont.truetype(basicfont, size=110)

        elif len(choosen2) < 21:
            mem_letter = ImageFont.truetype(basicfont, size=100)

        elif len(choosen2) < 28:
            mem_letter = ImageFont.truetype(basicfont, size=95)

        else:
            mem_letter = ImageFont.truetype(basicfont, size=85)

        im = Image.new("RGBA", (1500, 1250), (0, 0, 169, 75))
        im_draw = ImageDraw.Draw(im)

        im_draw, im, buffer = pre_render(im_draw, im, bg)

        #####################################################################################
        # THE REAL MODE BEGINS!!! (Adding the text)
        #####################################################################################
        im_draw, im = render(
            im,
            im_draw,
            buffer,
            member,
            owners,
            is_dev,
            is_staff,
            is_donor,
            level_info,
            user_info,
            pfp,
            user_tag,
            font,
            basicfont,
            mem_letter,
            header_font,
            stat_font,
        )

        if (
                can_embed(ctx)
                and can_react(ctx)
                and can_send(ctx)
                and can_upload(ctx)
        ):
            embed = discord.Embed(color=self.bot.color).set_author(
                name=f"{member}'s Profile",
                url="https://sheri.bot",
                icon_url=avatar_check(member),
            )
            embed.set_image(url="attachment://pfp_card.png")
            embed.set_footer(
                text=f"https://sheri.bot/ | User ID: {member.id}",
                icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
            )

            if member == ctx.author:
                await ctx.send(
                    # content=f"Here is your profile, {member}!",
                    embed=embed,
                    file=dFile(fp=buffer, filename="pfp_card.png"),
                )
            else:
                await ctx.send(
                    # content=f"Here is **{member}**'s profile, {ctx.author}!",
                    file=dFile(fp=buffer, filename="pfp_card.png"),
                    embed=embed,
                )
        else:
            if can_send(ctx):
                return await ctx.send(
                    "I can not **EMBED_LINKS** or **ATTACH_FILES**. Please fix this if this was not intended..."
                )
            if can_react(ctx):
                await ctx.message.add_reaction("❌")
            try:
                await ctx.author.send(
                    "I can not **SEND MESSAGES**, **EMBED_LINKS, or **ATTACH_FILES**. Please fix this if this was not intended..."
                )
            except discord.Forbidden:
                pass