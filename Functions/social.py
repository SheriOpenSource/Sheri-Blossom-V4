import decimal
from random import randint

import discord
from discord.ext import commands

from API.API import Retrieval as Get
from Formats.chat_markdown import bold
from Functions.core import embed_color, send_message
from Functions.errors import TooManyUsers, UsedOnSelf
from Lines.SocialLines import SocialLines as Data
from Lines.custom_emotes import sheri_emotes, footer

love_message = ""
smash_message = ""


def draw_smash_meter():
    global smash_message
    random_integer = randint(0, 100)
    love = decimal.Decimal(str(random_integer / 10)).quantize(
        decimal.Decimal("1"), rounding=decimal.ROUND_HALF_UP
    )
    love_emoji = "<:stickylove:452190037321449472>"
    bar = ""

    if random_integer == 100:
        love_emoji = "<a:spinnytealpaw:608728799982387200>"
        love_message = "Das gunna be a heavy smash"
    elif random_integer == 69:
        love_emoji = "😏"
        love_message = "That's the sex position *wink wonk*"
    elif random_integer == 0:
        love_emoji = "💔"
        love_message = "All sorts of fails on that smash...."
    elif random_integer <= 15:
        love_message = "That's a yikes.."
    elif random_integer <= 30:
        love_message = "They can hear the condom ripping.."
    elif random_integer <= 45:
        love_message = "Accidental cream pie accident..."
    elif random_integer <= 60:
        love_message = "Nothing went wrong! Just a little messy!"
    elif random_integer <= 75:
        love_message = "Best smash in a while!"
    elif random_integer <= 90:
        love_message = "Give it a go, you're made for each other!"
    else:
        love_message = "Smash them very hard and don't stop fluff butt!"

    for i in range(10):
        if i < love:
            bar += love_emoji
        else:
            bar += "🖤"

    return f"**Smash percent:** {bar} **{random_integer}%**\n**{love_message}**"


def draw_love_meter():
    global love_message
    random_integer = randint(0, 100)
    love = decimal.Decimal(str(random_integer / 10)).quantize(
        decimal.Decimal("1"), rounding=decimal.ROUND_HALF_UP
    )
    love_emoji = "❤"
    bar = ""

    if random_integer == 100:
        love_emoji = "💛"
        love_message = "Go get married! I hope I'm invited ❤"
    elif random_integer == 0:
        love_emoji = "💔"
        love_message = (
            "That's not good... maybe delete this and try again before they see?"
        )
    elif random_integer <= 15:
        love_message = "That's a yikes.."
    elif random_integer <= 30:
        love_message = "Maybe in the future?"
    elif random_integer <= 45:
        love_message = "I mean this is the perfect range for friends?"
    elif random_integer <= 60:
        love_message = "Maybe try talking more?"
    elif random_integer <= 75:
        love_message = "Best friends, stay as best friends."
    elif random_integer <= 90:
        love_message = "Give it a go, you're made for each other!"
    else:
        love_message = "I ship it!"

    for i in range(10):
        if i < love:
            bar += love_emoji
        else:
            bar += "🖤"

    return f"**Love percent:** {bar} **{random_integer}%**\n**{love_message}**"


class SocialFunc:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    @staticmethod
    def process_users(ctx, users):
        if not users:
            raise commands.MissingRequiredArgument
        users = [x.display_name for x in list(set(users)) if x is not ctx.author]
        if len(users) > 3:
            raise TooManyUsers
        if not users:
            raise UsedOnSelf
        word = "was" if len(users) == 1 else "were"
        users = f"{', '.join(users[:-1])}, and {users[-1]}" if len(users) > 2 else " and ".join(users)
        return users.replace("@", ""), word

    @staticmethod
    def social_img_embed(url, report):
        embed = discord.Embed(color=embed_color(),
                              description=f"Something wrong with the image? {bold(f'[Report it here]({report})')}\n"
                                          f"``{report}``\n"
                                          f"Image Not loading? {bold(f'[Image URL]({url})')}")
        embed.set_image(url=url)
        embed.set_footer(icon_url=footer, text="Image hosted on https://sheri.bot/")
        return embed

    @staticmethod
    async def social(self, ctx, error, endpoint, social, nsfw: bool = False, *users):
        try:
            if users:
                processed_users = SocialFunc.process_users(ctx, users)

                message = Data.get_social_line(social, nsfw).format(
                    bold(ctx.author.display_name.replace("@", "")),
                    bold(processed_users[0]))
                # For some reason if we don't have an endpoint for the command.
                embed = await ctx.pool.fetchval("SELECT social_embeds FROM botsettings_guild WHERE id=$1",
                                                ctx.guild.id)
                if embed:
                    if endpoint is None:
                        return await send_message(ctx, message=message)
                    social_image = await Get.main_api(self.bot, endpoint)
                    await send_message(ctx, message=message + f" {sheri_emotes['llove']}",
                                       embed=SocialFunc.social_img_embed(url=social_image['url'],
                                                                         report=social_image['report_url']))
                else:
                    await send_message(ctx, message=message + f" {sheri_emotes['llove']}")
            else:
                await send_message(ctx, message=error)

        except TooManyUsers:
            return await send_message(ctx, message="You cannot interact with more than 3 people at a time.")
        except (KeyError, ValueError):
            return await send_message(ctx, message="An internal error has occurred. Please contact support!")
        except UsedOnSelf:
            return await send_message(ctx, message=":eyes: Maybe you should mention someone else other than yourself.")
