import discord

from API.API import Retrieval as Sheri_Get
from API.ExAPI import External_Retrieval as Get
from Functions.core import send_message


class ImgFunc:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    @staticmethod
    def image_embed(ctx, desc: str, img: str, sheri: bool = False, host: str = None):
        embed = discord.Embed(color=ctx.color, description=desc)
        if sheri:
            embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                             text="Hosted by: https://sheri.bot/")
        else:
            embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/457367016823848970.png?v=1",
                             text="If there's an issue with ANY image, please take it up with the provider.")
        if host:
            embed.set_author(name=host)
        embed.set_image(url=img)
        return embed

    async def neko_image(self, ctx, endpoint):
        nekos = await Get.neko_api(self.bot, endpoint)
        message = f"**[Image Link]({nekos['url']})**"
        await send_message(ctx,
                           embed=ImgFunc.image_embed(ctx, message, nekos['url'], host="nekos.life"))

    async def sheri_image(self, ctx, endpoint):
        sheri = await Sheri_Get.main_api(self.bot, endpoint)
        try:
            url = sheri["url"]
        except KeyError:
            return
        else:
            pass

        try:
            report = sheri["report_url"]
        except KeyError:
            return await send_message(ctx, message=url)
        else:
            pass

        message = (f"**Link to image [here]({url})\n"
                   f"Something wrong? Report it [here]({report})**\n"
                   f"``{sheri['report_url']}``")
        await send_message(ctx,
                           embed=ImgFunc.image_embed(ctx, message, sheri['url'], sheri=True))

    async def alex_image(self, ctx, endpoint):
        image = await Get.alexflipnote_api(self.bot, endpoint)
        message = f"**[Image Link]({image['file']})**"
        await send_message(ctx,
                           embed=ImgFunc.image_embed(ctx, message, image['file'], host="alexflipnote.dev"))

    async def here_is_code_img(self, ctx, endpoint):
        img = await Get.some_random_api_img(self.bot, endpoint)
        message = f"**[Image Link]({img['Link']})**"
        await send_message(ctx,
                           embed=ImgFunc.image_embed(ctx, message, img['Link']),
                           host="and-here-is-my-code.glitch.me")

    async def random_image(self, ctx, endpoint):
        image = await Get.some_random_api_img(self.bot, endpoint)
        message = f"**[Image Link]({image['link']})**"
        await send_message(ctx,
                           embed=ImgFunc.image_embed(ctx, message, image['link'], host="some-random-api.ml"))

    async def bb_image(self, ctx, endpoint):
        image = await Get.boob_api(self.bot, endpoint)
        message = f"**[Image Link]({image['url']})**"
        await send_message(ctx,
                           embed=ImgFunc.image_embed(ctx, message, image['url'], host="boob.bot"))
