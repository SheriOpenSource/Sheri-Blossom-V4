import asyncio

import discord

from Checks.bot_checks import can_delete
from Formats.formats import avatar_check
from Functions.core import send_message


async def away_check(bot, ctx, message):

    try:
        async with bot.pool.acquire() as db:
            away = await db.fetchval(
                """SELECT away FROM botsettings_user WHERE id=$1""",
                message.author.id
            )
  
            # Check to see if they are online and away on the bot and make them back

            #if away and message.author.status is discord.Status.online:
            # if away and str(message.author.status) == "online":
            #     msg = await send_message(ctx, message=f"Welcome back {message.author.display_name}!")
            #     await asyncio.sleep(5)
            #     await msg.delete()
            #     await ctx.pool.execute(
            #         """UPDATE botsettings_user SET away=$1 WHERE id=$2""",
            #         False,
            #         message.author.id,
            #     )


            for mention in message.mentions:
                try:
                    away = await db.fetchval(
                    """SELECT away FROM botsettings_user WHERE id=$1""",
                    mention.id
                    )
                    if away is True:
                        away_message = await db.fetchval(
                            """SELECT away_message FROM botsettings_user WHERE id=$1""",
                            mention.id,
                        )
                        embed = discord.Embed(
                            color=ctx.color,
                            title=f"{mention.display_name} is currently away!",
                        )
                        embed.set_thumbnail(url=avatar_check(mention))
                        embed.add_field(
                            name="**They have left this message:**",
                            value=away_message, inline=True
                        )
                        msg = await send_message(ctx, embed=embed)
                        await asyncio.sleep(10)
                        await msg.delete()
                except Exception:
                    return
    except Exception as e:
        try:
            ctx.sentry.capture_exception(e)
        except Exception as e:
            print(e)
