'''
@commands.command(name="profile")
    async def profile(self, ctx, user: discord.Member = None):
        async with ctx.bot.pool.acquire() as db:
            if user is None:
                user = ctx.author

            # Fetch data from DB to get most basic info
            user_info = await db.fetchrow(
                """SELECT premium, foxesall, bunniesall, wolvesall, foxes, bunnies, wolves,
                                          coins, boxes, keys, marry, xp FROM botsettings_user WHERE id=$1""",
                user.id,
            )
            embed = (
                discord.Embed(color=self.bot.color)
                .set_author(name=user, icon_url=avatar_check(user))
                .set_thumbnail(url=avatar_check(user))
            )

            # Create Levels class and get level info so we don't have to duplicate code here
            level_class = Levels(self.bot)
            level_info = await level_class.get_member_info(db, user)

            # Donor check
            is_donor = "Yes" if user_info["premium"] else "No"

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

            embed.add_field(
                name="Global Level",
                value=f"{level_info['global_level']}\n"
                f"({level_info['remaining_global_xp']}/{level_info['global_level_xp']})",
            )

            embed.add_field(
                name="Current Items",
                value=f"Coins: ``{user_info['coins']}``\n"
                f"Boxes: ``{user_info['boxes']}``\n"
                f"Keys: ``{user_info['keys']}``",
                inline=False,
            )
            embed.add_field(
                name="Current Animals",
                value=f"Foxes: ``{user_info['foxes']}``\n"
                f"Bunnies: ``{user_info['bunnies']}``\n"
                f"Wolves: ``{user_info['wolves']}``",
            )
            embed.add_field(
                name="All-Time Catches",
                value=f"Foxes: ``{user_info['foxesall']}``\n"
                f"Bunnies: ``{user_info['bunniesall']}``\n"
                f"Wolves: ``{user_info['wolvesall']}``",
            )
            embed.add_field(name="Married to", value=spouses_string)
            embed.add_field(name="Donor status", value=is_donor)
            await ctx.send(embed=embed)'''