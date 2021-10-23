import asyncio

import aiohttp
import discord

blacklist_tags = [
    "nightmare_fuel",
    "cub",
    "young",
    "human_only",
    "gore",
    "what",
    "what_has_science_done",
    "where_is_your_god_now",
    "flash_game",
    "dress_up",
    "slideshow",
    "apng",
    "not_furry",
    "nezumi",
    "rape",
    "necrophilia",
    "beastiality",
    "bestiality",
    "castration",
    "death_by_penis",
    "digestion",
    "castration",
    "imminent_death",
    "loli",
    "shota",
    "epilepsy_warning",
    "hard_vore",
    "amputee",
    "amputation",
    "mutilation",
    "blood",
    "aogami",
]


def build_embed(site, tag, author, scores, post_rate, file_url):
    # i += 1
    em = discord.Embed(
        title=f"{site} searched with {tag}",
        description=f"**Artist: {author}**\nScore: ***{scores}*** || Rating: {post_rate}\n[Link]({file_url})",
    )
    em.set_image(url=file_url)
    # em.set_footer(text=f"Post {i}/{count}")

    return em


async def e6_search(self, ctx, user, tag, flag):
    if tag is None:
        await ctx.send(
            "No tags were provided! You can have a maximum of 5 tags."
        )
    else:
        tag_test = tag.split(" ")
        '''
        count = tag_test[-1]

        if count.isdigit():
            if count == "69":
                count = None
            else:
                tag_test.remove(count)
                tag = ",".join(tag_test)
        else:
            count = None
        '''

        x = 0
        ban_tag = set(tag_test).intersection(blacklist_tags)
        # print (f" banned tag: {ban_tag}")

        if len(tag_test) > 5:
            await ctx.send(f"{user.mention}, I only allow **up to 5 tags!**")
        else:
            if ban_tag:
                ban_list_tag = ""
                ban_tag = list(ban_tag)
                for i in ban_tag:
                    ban_list_tag += ban_tag[x] + " "
                    x += 1
                await ctx.send(
                    f"Sorry {user.mention}, but your search results include posts which contain the tag `{ban_list_tag}"
                    f"`, which has been blacklisted to comply with Discord's Community Guidelines. "
                    f"If your search has a high probability of returning results containing {ban_list_tag}, "
                    f"you may enter `-{ban_list_tag}` as a tag to "
                    f"exclude such results and more effectively avoid this error. "
                    f"We apologize for the inconvenience and thank you for your understanding."
                )
            else:
                '''
                if count is not None:
                    if int(count) > 15:
                        await ctx.send(
                            f"WHOA {user.name}, simmer down there creature. Posting only 15."
                        )
                        count = 15
                '''

                if ctx.channel.is_nsfw():
                    if flag == "e6":
                        site = "e621"
                    else:
                        site = "e926"
                else:
                    site = "e926"

                header = {
                    "User-Agent": "Sheri Blossom V4 [bot] by Waspyeh#0615 on discord"
                }

                api_link = f"https://{site}.net/posts.json?tags={tag} order:random&limit=150"
                # + site
                # + ".net/post/index.json?tags="
                # + tag
                # + " order:random"
                # + "&limit=150"

                async with aiohttp.ClientSession() as session:
                    raw_response = await session.get(api_link, headers=header)
                    if raw_response.status == 200:
                        pass
                    else:
                        return await ctx.send("Error with contacting e621.net API")

                    response_output = await raw_response.json()
                    post = response_output['posts']
                    max_post = len(post)
                    if not post:
                        await ctx.send("No return result")
                    else:
                        '''
                        if count is None:
                            count = 1
                        '''

                        i = 0
                        done = False
                        limit = 0
                        post_author = []
                        score = []
                        post_url = []
                        rating = []

                        while done is False:
                            try:
                                post_tags = post[i]["tags"]["general"]
                            except IndexError:
                                break
                                
                            blacklist_pass = set(blacklist_tags).intersection(post_tags)

                            if blacklist_pass:
                                i += 1
                            else:
                                banned_ext = ["webm", "swf"]
                                ext = post[i]['file']['ext']

                                if ext in banned_ext:
                                    i += 1
                                else:
                                    if "score" in tag_test:
                                        pass
                                    else:
                                        score_threshold = post[i]["score"]['total']
                                        score_threshold = score_threshold

                                        if score_threshold <= 10:
                                            i += 1
                                        else:
                                            score.append(post[i]["score"]['total'])

                                            authors = post[i]['tags']['artist']
                                            authors = ",".join(authors)
                                            post_author.append(authors)

                                            url = post[i]["file"]["url"]
                                            if url is None:
                                                i += 1
                                                continue

                                            post_url.append(post[i]["file"]['url'])

                                            rate = post[i]["rating"]

                                            if rate == "s":
                                                rating.append("Safe")
                                            elif rate == "e":
                                                rating.append("Explicit")
                                            elif rate == "q":
                                                rating.append("Questionable")
                                                
                                            done = True

                                            limit += 1

                                            '''
                                            if limit == int(count):
                                                done = True
                                            else:
                                                i += 1
                                            '''

                            if i == max_post:
                                done = True
                        i = 0

                        if post_url:
                            '''
                            if max_post < int(count):
                                await ctx.send(
                                    "Due to results, your queue has been reduced!"
                                )
                                count = max_post

                            if len(post_url) < int(count):
                                await ctx.send(
                                    "Due to results, your queue has been reduced!"
                                )
                                count = len(post_url)
                            '''

                            await posting_e6(
                                self,
                                i,
                                ctx,
                                user,
                                site,
                                tag,
                                post_author,
                                score,
                                post_url,
                                rating,
                                # count,
                            )
                        else:
                            await ctx.send("No return result")


def indexer(i, post_author, score, post_url, rating):
    the_author = post_author[i]
    the_score = score[i]
    the_url = post_url[i]
    the_rating = rating[i]

    return the_author, the_score, the_rating, the_url


async def posting_e6(
        self, i, ctx, u, site, tag, post_author, score, post_url, rating
):
    the_author, the_score, the_rating, the_url = indexer(
    i, post_author, score, post_url, rating
    )
    count = 1
    em = build_embed(site, tag, the_author, the_score, the_rating, the_url)
    await ctx.send(embed=em)
    # search = True
    # m = None
    # while search is True:
    #     if m is None:
    #         the_author, the_score, the_rating, the_url = indexer(
    #             i, post_author, score, post_url, rating
    #         )
    # 
    #         em = build_embed(
    #             site, tag, the_author, the_score, the_rating, the_url, i, count
    #         )
    #         m = await ctx.send(embed=em)
    #     else:
    #         the_author, the_score, the_rating, the_url = indexer(
    #             i, post_author, score, post_url, rating
    #         )
    # 
    #         em = build_embed(
    #             site, tag, the_author, the_score, the_rating, the_url, i, count
    #         )
    # 
    #         await m.edit(embed=em)
    # 
    #     if int(count) > 1:
    #         reactions = ["⬅", "⬇", "➡"]
    # 
    #         for reaction in reactions:
    #             await m.add_reaction(reaction)
    # 
    #         def check(r, u):
    #             return (
    #                     u == ctx.message.author
    #                     and (
    #                             str(r.emoji) == "⬅"
    #                             or str(r.emoji) == "➡"
    #                             or str(r.emoji) == "⬇"
    #                     )
    #                     and (r.message.id == m.id)
    #             )
    # 
    #         try:
    #             while True:
    #                 reaction, user = await self.bot.wait_for(
    #                     "reaction_add", timeout=120.0, check=check
    #                 )
    #                 await m.remove_reaction(reaction.emoji, user)
    # 
    #                 if user == ctx.author:
    #                     await reaction.remove(user)
    #                     if str(reaction.emoji) == "⬅":
    #                         i = i - 1
    #                         if i == -1:
    #                             i = int(count) - 1
    # 
    #                         break
    #                     elif str(reaction.emoji) == "➡":
    #                         i = i + 1
    #                         themax = int(count)
    #                         if i >= themax:
    #                             i = 0
    # 
    #                         break
    #                     elif str(reaction.emoji) == "⬇":
    #                         search = False
    #                         await m.clear_reactions()
    #                         break
    # 
    #         except asyncio.TimeoutError:
    #             await m.clear_reactions()
    # 
    #             return
    #     else:
    #         search = False
