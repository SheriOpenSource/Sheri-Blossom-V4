import io
import math
from io import BytesIO

import aiohttp
import discord
from PIL import Image, ImageDraw, ImageFont
from discord import File as dFile
from discord.ext import commands

from API.API import Retrieval as Get
from Checks.bot_checks import can_embed, can_send, can_upload, can_react
from Commands.levels import Levels
from Formats.formats import avatar_check, icon_check
from Lines.custom_emotes import CustomEmotes
from Functions.core import send_message

badge = {
    "owner":
        ["https://cdn.discordapp.com/attachments/410489459885342730/677439009022017544/badgeown.png",
         50, 480],
    "dev":
        ["https://cdn.discordapp.com/attachments/674033588358086656/677201742319845388/developer.png",
         50, 500],
    "vip":
        ["https://cdn.discordapp.com/attachments/674033588358086656/676915778527821835/shieldVIP.png",
         50, 500],
    "donor":
        ["https://cdn.discordapp.com/attachments/509374698900029445/679544903616692274/patrion.png.png",
         50, 500],
    "support":
        ["https://cdn.discordapp.com/attachments/470277176726519828/684419305684729946/supportbadge.png.png",
         50, 500],
    "default":
        ["https://cdn.discordapp.com/attachments/509374698900029445/684490588934111235/freebadge.png",
         50, 500]
}


def is_staffer(self, member):
    guild = self.bot.get_guild(346892627108560901)
    if member not in guild.members:
        return False
    else:
        staff = guild.get_role(692569814115418112)

        if member in staff.members:
            return True
        else:
            return False


def resizer(w, h, img):
    w_percent = w / float(img.size[0])
    w_size = int(math.ceil(float(img.size[0]) * float(w_percent)))
    h_percent = h / float(img.size[1])
    h_size = int(math.ceil(float(img.size[1]) * float(h_percent)))
    if w_size != w:
        w_size = w
    if h_size != h:
        h_size = h
    img = img.resize((w_size, h_size), Image.ANTIALIAS)
    output = io.BytesIO()
    img.save(output, format="PNG")

    return img


async def image_render(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as raw_response:
            bg = BytesIO(await raw_response.read())

            bg = Image.open(bg)

    return bg


def badges(im_draw, font, member, owners, is_staff, is_donor, is_dev):
    admin = "Maintainer"
    dev = "Developer"
    donor = "Premium"
    supp = "Support"
    staff = "Staff"

    badge_letter = ImageFont.truetype(font, size=55)
    dow, _ = im_draw.textsize(donor, font=badge_letter)
    dw, _ = im_draw.textsize(dev, font=badge_letter)
    aw, _ = im_draw.textsize(admin, font=badge_letter)
    suw, _ = im_draw.textsize(supp, font=badge_letter)
    stw, _ = im_draw.textsize(staff, font=badge_letter)

    if owners is True:
        im_draw.rectangle((5, 625, 300, 700), fill=(57, 159, 159, 255))  # Badge Slot 1
        im_draw.text(
            (((300 - aw) / 2), 628),
            text=admin,
            fill=(255, 255, 255, 200),
            font=badge_letter,
        )
        if is_dev is True:
            im_draw.rectangle(
                (5, 725, 300, 800), fill=(225, 55, 80, 255)
            )  # Badge Slot 2
            im_draw.text(
                (((300 - dw) / 2), 728),
                text=dev,
                fill=(255, 255, 255, 200),
                font=badge_letter,
            )
        if is_donor:
            im_draw.rectangle(
                (5, 825, 300, 900), fill=(232, 91, 70, 255)
            )  # Badge Slot 3
            im_draw.text(
                (((300 - dow) / 2), 828),
                text=donor,
                fill=(255, 255, 255, 200),
                font=badge_letter,
            )

        if member in is_staff:
            im_draw.rectangle(
                (5, 925, 300, 1000), fill=(111, 111, 111, 255)
            )  # Badge Slot 4
            im_draw.text(
                (((300 - stw) / 2), 928),
                text=staff,
                fill=(255, 255, 255, 200),
                font=badge_letter,
            )

        return im_draw

    elif is_dev is True:
        im_draw.rectangle((5, 725, 300, 800), fill=(225, 55, 80, 255))  # Badge Slot 2
        im_draw.text(
            (((300 - dw) / 2), 728),
            text=dev,
            fill=(255, 255, 255, 200),
            font=badge_letter,
        )

    elif is_donor:
        im_draw.rectangle((5, 625, 300, 700), fill=(232, 91, 70, 255))  # Badge Slot 1
        im_draw.text(
            (((300 - dow) / 2), 628),
            text=donor,
            fill=(255, 255, 255, 200),
            font=badge_letter,
        )

        if member in is_staff:
            im_draw.rectangle(
                (5, 725, 300, 800), fill=(111, 111, 111, 255)
            )  # Badge Slot 2
            im_draw.text(
                (((300 - dow) / 2), 728),
                text=staff,
                fill=(255, 255, 255, 200),
                font=badge_letter,
            )

        return im_draw

    elif member in is_staff:
        im_draw.rectangle((5, 625, 300, 700), fill=(111, 111, 111, 255))  # Badge Slot 1
        im_draw.text(
            (((300 - stw) / 2), 628),
            text=staff,
            fill=(255, 255, 255, 200),
            font=badge_letter,
        )
        if is_donor:
            im_draw.rectangle(
                (5, 725, 300, 800), fill=(232, 91, 70, 255)
            )  # Badge Slot 2
            im_draw.text(
                (((300 - dow) / 2), 728),
                text=donor,
                fill=(255, 255, 255, 200),
                font=badge_letter,
            )

        return im_draw

    return im_draw

    # elif member.id in owners:
    #    im_draw.rectangle((5, 625, 300, 700), fill=(57, 159, 159, 255))  # Badge Slot 1
    #    im_draw.text((((300 - aw) / 2), 628), text=admin, fill=(255, 255, 255, 200), font=badge_letter)
    #   # im_draw.rectangle((5, 725, 300, 800), fill=(225, 55, 80, 255))  # Badge Slot 2
    #    # im_draw.text((((300 - dw) / 2), 728), text=dev, fill=(255, 255, 255, 200), font=badge_letter)
    #    return im_draw


def pre_render(im_draw, im, bg):
    im.paste(bg, (0, 0))

    im_draw.rectangle((0, 500, 1500, 610), fill=(100, 0, 220, 100))  # TopSidebar
    im_draw.rectangle((0, 280, 310, 1200), fill=(50, 0, 220, 75))  # Sidebar
    im_draw.rectangle((0, 300, 300, 600), fill=(25, 100, 200, 50))  # Avatar Border

    ##############################################################################

    # Body All Time Rankings

    im_draw.rectangle((310, 600, 1500, 965), fill=(125, 100, 200, 200))  # Body block

    # im_draw.rectangle((310, 600, 700, 690), fill=(225, 100, 200, 255))  # All Time block
    im_draw.rectangle((550, 600, 775, 665), fill=(225, 100, 200, 255))  # All Time block

    ##############################################################################

    # Body Current Rankings

    im_draw.rectangle((800, 600, 990, 665), fill=(225, 100, 200, 255))  # Current block

    ##############################################################################

    # Body Keys Rankings

    im_draw.rectangle((1150, 600, 1300, 665), fill=(225, 100, 200, 255))  # Key block

    ##############################################################################

    # Body Boxes Rankings

    im_draw.rectangle((1150, 785, 1300, 850), fill=(225, 100, 200, 255))  # Box block

    ###########################################################################

    # Misc

    im_draw.rectangle((310, 965, 1500, 1200), fill=(20, 10, 69, 255))  # Misc Block

    buffer = BytesIO()
    im.save(buffer, "png")
    buffer.seek(0)
    pfp_blend = Image.blend(im, bg, 0.2)
    im.paste(pfp_blend, (0, 0))

    return im_draw, im, buffer


def render(
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
):
    im.paste(pfp, (5, 305))  # The PFP

    # The Member Name

    im_draw.text(
        (315 - 5, 375), text=f"{user_tag}", fill=(0, 0, 0, 100), font=mem_letter
    )
    im_draw.text(
        (315 + 5, 375), text=f"{user_tag}", fill=(0, 0, 0, 100), font=mem_letter
    )
    im_draw.text(
        (315, 375 - 5), text=f"{user_tag}", fill=(0, 0, 0, 100), font=mem_letter
    )
    im_draw.text(
        (315, 375 + 5), text=f"{user_tag}", fill=(0, 0, 0, 100), font=mem_letter
    )

    im_draw.text(
        (315, 375), text=f"{user_tag}", fill=(255, 255, 255, 200), font=mem_letter
    )

    ###############################################################################
    # Level

    global_level = f"{level_info['global_level']}"
    level = f"{level_info['guild_level']}"

    global_level_post = \
        f"Global LVL {global_level}\n({level_info['remaining_global_xp']:,}/{level_info['global_level_xp']:,})"
    level_post = \
        f"Guild LVL {level}\n({level_info['remaining_guild_xp']:,}/{level_info['guild_level_xp']:,})"

    im_draw.text((315, 500), text=global_level_post, fill=(255, 255, 255, 200), font=stat_font)

    im_draw.text((800, 500), text=level_post, fill=(255, 255, 255, 200), font=stat_font)

    ###############################################################################
    # Badges

    img_draw = badges(im_draw, font, member, owners, is_staff, is_donor, is_dev)

    # im_draw.rectangle((5, 925, 300, 1000), fill=(111, 111, 111, 255))  # Badge Slot 4
    # im_draw.text((((300 - suw) / 2), 928), text=supp, fill=(255, 255, 255, 200), font=badge_letter)

    # im_draw.rectangle((5, 1025, 300, 1100), fill=(69, 69, 69, 255))  # Badge Slot 5
    # im_draw.text((((300 - stw) / 2), 1028), text=staffp, fill=(255, 255, 255, 200), font=badge_letter)

    ##############################################################################

    # Body All Time Rankings

    all_time = "All-Time"

    bunny_post = "Bunnies"
    wolf_post = "Wolves"
    fox_post = "Foxes"
    cat_post = "Cats"
    bunny_amount = f"{user_info['bunniesall']:,}"
    wolf_amount = f"{user_info['wolvesall']:,}"
    fox_amount = f"{user_info['foxesall']:,}"
    cat_amount = f"{user_info['catsall']:,}"

    # im_draw.text((310, 600), text=all_time, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text((550, 600), text=all_time, fill=(255, 255, 255, 200), font=header_font)

    im_draw.text(
        (310, 670), text=bunny_post, fill=(255, 255, 255, 200), font=header_font
    )
    im_draw.text((310, 755), text=wolf_post, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text((310, 830), text=fox_post, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text((310, 910), text=cat_post, fill=(255, 255, 255, 200), font=header_font)

    im_draw.text((550, 670), text=bunny_amount, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text((550, 755), text=wolf_amount, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text((550, 830), text=fox_amount, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text((550, 915), text=cat_amount, fill=(255, 255, 255, 200), font=header_font)

    ##############################################################################

    # Body Current Rankings

    st = "Current"

    current_bunny_post = f"{user_info['bunnies']:,}"
    current_wolf_post = f"{user_info['wolves']:,}"
    current_fox_post = f"{user_info['foxes']:,}"
    current_cat_post = f"{user_info['cats']:,}"

    im_draw.text((800, 600), text=st, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text(
        (800, 670), text=current_bunny_post, fill=(255, 255, 255, 200), font=header_font
    )
    im_draw.text(
        (800, 755), text=current_wolf_post, fill=(255, 255, 255, 200), font=header_font
    )
    im_draw.text((800, 830), text=current_fox_post, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text((800, 915), text=current_cat_post, fill=(255, 255, 255, 200), font=header_font)

    ##############################################################################

    # Body KEY Rankings

    key_t = "Keys"

    key_p = f"{user_info['keys']:,}"

    im_draw.text((1150, 600), text=key_t, fill=(255, 255, 255, 200), font=header_font)

    im_draw.text((1150, 700), text=key_p, fill=(255, 255, 255, 200), font=header_font)

    ##############################################################################

    # Body Boxes Rankings

    key_t = "Boxes"

    key_p = f"{user_info['boxes']:,}"

    im_draw.text((1150, 785), text=key_t, fill=(255, 255, 255, 200), font=header_font)

    im_draw.text((1150, 875), text=key_p, fill=(255, 255, 255, 200), font=header_font)

    ###########################################################################

    # Misc
    misc_letter = ImageFont.truetype(font, size=60)

    coin = f"{user_info['coins']:,}"

    coin_post = f"Coins:"
    im_draw.text((310, 980), text=coin_post, fill=(255, 255, 255, 200), font=misc_letter)
    im_draw.text((310, 1050), text=coin, fill=(255, 255, 255, 200), font=stat_font)

    treat = f"{user_info['treats']:,}"

    treat_post = f"Treats:"
    im_draw.text(
        (710, 980), text=treat_post, fill=(255, 255, 255, 200), font=misc_letter
    )
    im_draw.text((710, 1050), text=treat, fill=(255, 255, 255, 200), font=stat_font)

    pres = f"{user_info['presents']:,}"

    presents_post = f"Presents:"
    im_draw.text(
        (1010, 980), text=presents_post, fill=(255, 255, 255, 200), font=misc_letter
    )
    im_draw.text((1010, 1050), text=pres, fill=(255, 255, 255, 200), font=stat_font)

    im.save(buffer, "png")
    buffer.seek(0)

    return im_draw, im


def pre_renderii(im_draw, im, bg):
    im.paste(bg, (0, 0))

    buffer = BytesIO()
    im.save(buffer, "png")
    buffer.seek(0)

    return im_draw, im, buffer


async def renderii(
        im,
        im_draw,
        buffer,
        member,
        is_dev,
        is_staff,
        is_donor,
        is_vip,
        level_info,
        user_info,
        pfp,
        user_tag,
        font,
        basicfont,
        mem_letter,
        header_font,
        stat_font,
):
    get_award = False
    im.paste(pfp, (140, 155), pfp)  # The PFP

    # Badge Logic
    ###############################################
    if member.id == 139800365393510400:
        award = badge["owner"]
        emblem = await image_render(award[0])
    elif is_dev is True:
        award = badge["dev"]
        emblem = await image_render(award[0])
        emblem = resizer(200, 200, emblem)
    elif member in is_staff:
        award = badge["support"]
        emblem = await image_render(award[0])
        emblem = resizer(200, 200, emblem)
    elif is_vip is True:
        award = badge["vip"]
        emblem = await image_render(award[0])
        emblem = resizer(200, 200, emblem)
    elif is_donor is True:
        award = badge["donor"]
        emblem = await image_render(award[0])
        emblem = resizer(200, 200, emblem)
    else:
        award = badge["default"]
        emblem = await image_render(award[0])
        emblem = resizer(200, 200, emblem)

    im.paste(emblem, (award[1], award[2]), emblem)

    # The Member Name
    wm, _ = im_draw.textsize(f"{user_tag}", font=mem_letter)

    im_draw.text(
        ((((1250 - wm) / 2) + 255) - 2, 85), text=f"{user_tag}", fill=(0, 0, 0, 100), font=mem_letter
    )
    im_draw.text(
        ((((1250 - wm) / 2) + 255) - 2, 85), text=f"{user_tag}", fill=(0, 0, 0, 100), font=mem_letter
    )
    im_draw.text(
        ((((1250 - wm) / 2) + 255), 85 - 2), text=f"{user_tag}", fill=(0, 0, 0, 100), font=mem_letter
    )
    im_draw.text(
        ((((1250 - wm) / 2) + 255), 85 + 2), text=f"{user_tag}", fill=(0, 0, 0, 100), font=mem_letter
    )

    im_draw.text(
        ((((1250 - wm) / 2) + 255), 83), text=f"{user_tag}", fill=(255, 255, 255, 200), font=mem_letter
    )

    ###############################################################################
    # Level

    # glevel = f"{level_info['global_level']}"
    # level = f"{level_info['guild_level']}"

    # global_level_post = f"LVL {glevel}"
    if member.id == 139800365393510400:
        global_level_post = "Sheri's Master"
    else:
        global_level_post = " "
    # levelpost = f"Guild LVL {level}\n({level_info['remaining_guild_xp']:,}/{level_info['guild_level_xp']:,})"
    w, _ = im_draw.textsize(global_level_post, font=stat_font)

    im_draw.text(((((1250 - w) / 2) + 255) - 2, 165), text=global_level_post, fill=(0, 0, 0, 200), font=stat_font)
    im_draw.text(((((1250 - w) / 2) + 255) + 2, 165), text=global_level_post, fill=(0, 0, 0, 200), font=stat_font)
    im_draw.text(((((1250 - w) / 2) + 255), 165 - 2), text=global_level_post, fill=(0, 0, 0, 200), font=stat_font)
    im_draw.text(((((1250 - w) / 2) + 255), 165 + 2), text=global_level_post, fill=(0, 0, 0, 200), font=stat_font)
    im_draw.text(((((1250 - w) / 2) + 255), 163), text=global_level_post, fill=(5, 255, 2, 250), font=stat_font)

    # im_draw.text((800, 500), text=levelpost, fill=(255, 255, 255, 200), font=stat_font)
    ##############################################################################

    # Body KEY Rankings

    key_t = "Keys"

    key_p = f"{user_info['keys']:,}"
    wbt, _ = im_draw.textsize(key_t, font=header_font)
    wbp, _ = im_draw.textsize(key_p, font=header_font)

    im_draw.text(((((1250 - w) / 2) + 255), 300), text=key_t, fill=(255, 255, 255, 250), font=header_font)

    im_draw.text(((((1250 - w) / 2) + 255), 360), text=key_p, fill=(255, 255, 255, 250), font=header_font)

    ##############################################################################

    # Body Boxes Rankings

    key_t = "Boxes"

    key_p = f"{user_info['boxes']:,}"
    wkt, _ = im_draw.textsize(key_t, font=header_font)
    wkp, _ = im_draw.textsize(key_p, font=header_font)

    im_draw.text(((((1250 - w) / 2) + 255), 450), text=key_t, fill=(255, 255, 255, 250), font=header_font)

    im_draw.text(((((1250 - w) / 2) + 255), 510), text=key_p, fill=(255, 255, 255, 250), font=header_font)

    ###########################################################################
    font = "utils/fonts/NOVASQUARE.TTF"
    stat_font_go = ImageFont.truetype(font, size=40)

    # Body All Time Rankings

    all_time = "All-Time"

    all_time_post = f"Bunnies: {user_info['bunniesall']:,}\n" + \
                    f"Wolves: {user_info['wolvesall']:,}\n" + \
                    f"Foxes: {user_info['foxesall']:,}\n" + \
                    f"Cats: {user_info['catsall']:,}\n"

    # im_draw.text((310, 600), text=all_time, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text((105, 750), text=all_time, fill=(255, 255, 255, 55), font=header_font)
    im_draw.text((105, 825), text=all_time_post, fill=(255, 255, 255, 55), font=stat_font_go)

    ##############################################################################

    # Body Current Rankings

    st = "Current"

    cbunnykpost = f"{user_info['bunnies']:,}"
    cwolfpost = f"{user_info['wolves']:,}"
    cfoxpost = f"{user_info['foxes']:,}"

    stc = f"Bunnies: {user_info['bunnies']:,}\n" + \
          f"Wolves: {user_info['wolves']:,}\n" + \
          f"Foxes: {user_info['foxes']:,}\n" + \
          f"Cats: {user_info['cats']:,}\n"

    # im_draw.text((310, 600), text=all_time, fill=(255, 255, 255, 200), font=header_font)
    im_draw.text((105, 1050), text=st, fill=(255, 255, 255, 55), font=header_font)
    im_draw.text((105, 1125), text=stc, fill=(255, 255, 255, 55), font=stat_font_go)

    ##############################################################################
    # Body Inventory Rankings

    coins = "Coins"

    coin_post = f"{user_info['coins']:,}\n"

    im_draw.text((635, 760), text=coins, fill=(255, 255, 255, 55), font=header_font)
    im_draw.text((635, 835), text=coin_post, fill=(255, 255, 255, 55), font=stat_font_go)

    misc = ""

    if user_info['treats'] != 0:
        misc += "Treats\n"
        misc += f"{user_info['treats']:,}\n\n"
    if user_info['presents'] != 0:
        misc += "Presents\n"
        misc += f"{user_info['presents']:,}\n\n"

    if misc != "":
        im_draw.text((635, 900), text=misc, fill=(255, 255, 255, 55), font=header_font)

        ##############################################################################

    im.save(buffer, "png")
    buffer.seek(0)

    return im_draw, im


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.main_guild = 346892627108560901
        self.feedback_channel = 677577723954200619
        bot.remove_command("help")

    @commands.command()
    async def profilecog(self, ctx):
        await ctx.invoke(self.bot.get_command('update'))
        await ctx.invoke(self.bot.get_command('c r'), "general")
        await ctx.invoke(self.bot.get_command('profileii'))

    @commands.command()
    async def profileii(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        async with ctx.bot.pool.acquire() as db:
            data = await db.fetchrow(
                """SELECT * FROM botsettings_user WHERE id=$1""", member.id
            )

            if not data:
                return await ctx.send(f"{member.name} is not in my records!")

            # Create Levels class and get level info so we don't have to duplicate code here
            level_class = Levels(self.bot)
            level_info = await level_class.get_member_info(db, member)

            # Donor check
            is_donor = True if data["premium"] else False

            # Dev Check
            is_dev = data["developer"]
            # VIP Check
            is_vip = data["vip"]

            # Staff checking
            try:
                support_server = self.bot.get_guild(id=346892627108560901)
                staff_role = discord.utils.get(
                    support_server.roles, id=491694625355202564
                )
                # developers = discord.utils.get(
                # support_server.roles, id=418538906057965574
                # )
                vip = discord.utils.get(
                    support_server.roles, id=455064679845330945
                )
                # is_dev = developers.members
                is_staff = staff_role.members
                # is_vip = vip.members
            # Staff and Dev check cannot occur in DMs, If command issued in DMs make False so Profile does not fail. 
            except AttributeError:
                # is_dev = False
                is_staff = False
                # is_vip = False

            # Get spouses from DB info and turn into actual user objects
            spouses = []
            for user_id in data["marry"]:
                try:
                    spouse = self.bot.get_user(int(user_id))
                    spouses.append(str(spouse))
                except discord.HTTPException:
                    spouses.append(f"Unknown spouse (ID: {user_id})")
            spouses_string = ", ".join(spouses)
            if not spouses:
                spouses_string = "💔 Nobody"
            async with aiohttp.ClientSession() as session:
                bg = await image_render(
                    "https://cdn.discordapp.com/attachments/509374698900029445/677248190264901632/unknown.png")
                # if member.id == 139800365393510400:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676619836469673991/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)
                # elif is_dev is True:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676622111573409823/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)
                # elif member in is_staff:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676623867602665491/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)
                # elif is_donor is True:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676625759988613174/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)
                # elif is_vip is True:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676998141559439385/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)

            if member.avatar:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f"{member.avatar_url}?size=1024"
                    ) as raw_response:
                        pfp = BytesIO(await raw_response.read())

                        pfp = Image.open(pfp).convert('RGBA')

                big_size = (pfp.size[0] * 3, pfp.size[1] * 3)
                pfp = pfp.resize((409, 409), Image.BICUBIC)

                mask = Image.new('L', big_size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + big_size, fill=255)
                mask = mask.resize(pfp.size, Image.BICUBIC)
                pfp.putalpha(mask)
                pfp.save(io.BytesIO(), format='PNG')

            ##############################
            #                            #
            #       TEXT AND FONTS       #
            #                            #
            ##############################

            user_tag = f"{member.name}"
            font = "utils/fonts/NOVASQUARE.TTF"
            basicfont = "utils/fonts/ARIALUNI.TTF"

            #################################
            #                               #
            #       Member allocating       #
            #                               #
            #################################

            choose2 = list(member.name)

            # Fonts
            ########################
            header_font = ImageFont.truetype(font, size=60)
            stat_font = ImageFont.truetype(font, size=50)

            if len(choose2) < 16:
                mem_letter = ImageFont.truetype(basicfont, size=80)

            elif len(choose2) < 21:
                mem_letter = ImageFont.truetype(basicfont, size=70)

            elif len(choose2) < 28:
                mem_letter = ImageFont.truetype(basicfont, size=55)

            else:
                mem_letter = ImageFont.truetype(basicfont, size=45)

            im = Image.new("RGBA", (1250, 1500), (0, 0, 169, 75))
            im_draw = ImageDraw.Draw(im)

            im_draw, im, buffer = pre_renderii(im_draw, im, bg)

            #####################################################################################
            #                     THE REAL MODE BEGINS!!! (Adding the text)                     #
            #####################################################################################
            im_draw, im = await renderii(
                im,
                im_draw,
                buffer,
                member,
                is_dev,
                is_staff,
                is_donor,
                is_vip,
                level_info,
                data,
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
                if spouses_string != "💔 Nobody":
                    embed.add_field(name=f"Marriages", value=f"{spouses_string}")

                    embed.set_image(url="attachment://pfp_card.png")
                    if member == ctx.author:
                        await ctx.send(
                            # content=f"Here is your profile, {member}!",
                            file=dFile(fp=buffer, filename="pfp_card.png"),
                            embed=embed,
                        )
                    else:
                        await ctx.send(
                            # content=f"Here is **{member}**'s profile, {ctx.author}!",
                            file=dFile(fp=buffer, filename="pfp_card.png"),
                            embed=embed,
                        )
                else:
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
                        "I can't `Embed Links` or `Attach Files`. Please ensure I have these permissions!"
                    )
                try:
                    await ctx.author.send(
                        "I can't `Send Messages`, `Embed Links`, or `Attach Files`. Please double check my permissions!"
                    )
                except discord.Forbidden:
                    pass

    @commands.command(name="profile")
    @commands.guild_only()
    async def profile(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        async with ctx.bot.pool.acquire() as db:
            data = await db.fetchrow(
                """SELECT * FROM botsettings_user WHERE id=$1""", member.id
            )

            if not data:
                return await ctx.send(
                    f"{member.name} is not in my database! Please let my developers know if this issue persists!")

            # Create Levels class and get level info so we don't have to duplicate code here
            level_class = Levels(self.bot)
            level_info = await level_class.get_member_info(db, member)

            # Donor check
            is_donor = True if data["premium"] else False

            # Dev Check
            is_dev = data["developer"]
            # VIP Check
            is_vip = data["vip"]

            # Staff checking
            try:
                support_server = self.bot.get_guild(id=346892627108560901)
                if not support_server:
                    return await ctx.send("Try Again Later")
                staff_role = discord.utils.get(
                    support_server.roles, id=692569814115418112
                )
                # developers = discord.utils.get(
                # support_server.roles, id=418538906057965574
                # )
                vip = discord.utils.get(
                    support_server.roles, id=455064679845330945
                )
                # is_dev = developers.members
                is_staff = staff_role.members
                # is_vip = vip.members
            # Staff and Dev check cannot occur in DMs, If command issued in DMs make False so Profile does not fail.
            except AttributeError:
                # is_dev = False
                #is_staff = False
                return await ctx.send("Try Again later.")
                # is_vip = False

            # Get spouses from DB info and turn into actual user objects
            spouses = []
            for user_id in data["marry"]:
                try:
                    spouse = self.bot.get_user(int(user_id))
                    spouses.append(str(spouse))
                except discord.HTTPException:
                    spouses.append(f"Unknown spouse (ID: {user_id})")
            spouses_string = ", ".join(spouses)
            if not spouses:
                spouses_string = "💔 Nobody"
            async with aiohttp.ClientSession() as session:
                bg = await image_render(
                    "https://cdn.discordapp.com/attachments/509374698900029445/677248190264901632/unknown.png")
                # if member.id == 139800365393510400:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676619836469673991/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)
                # elif is_dev is True:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676622111573409823/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)
                # elif member in is_staff:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676623867602665491/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)
                # elif is_donor is True:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676625759988613174/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)
                # elif is_vip is True:
                # async with session.get(
                # "https://cdn.discordapp.com/attachments/595813455961784330/676998141559439385/unknown.png"
                # ) as raw_response:
                # bg = BytesIO(await raw_response.read())

                # bg = Image.open(bg)

            if member.avatar:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f"{member.avatar_url}?size=1024"
                    ) as raw_response:
                        pfp = BytesIO(await raw_response.read())

                        pfp = Image.open(pfp).convert('RGBA')

                big_size = (pfp.size[0] * 3, pfp.size[1] * 3)
                pfp = pfp.resize((409, 409), Image.BICUBIC)

                mask = Image.new('L', big_size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + big_size, fill=255)
                mask = mask.resize(pfp.size, Image.BICUBIC)
                pfp.putalpha(mask)
                pfp.save(io.BytesIO(), format='PNG')
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{member.default_avatar_url}"
                    ) as raw_response:
                        pfp = BytesIO(await raw_response.read())

                        pfp = Image.open(pfp).convert('RGBA')

                    big_size = (pfp.size[0] * 3, pfp.size[1] * 3)
                    pfp = pfp.resize((409, 409), Image.BICUBIC)

                    mask = Image.new('L', big_size, 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0) + big_size, fill=255)
                    mask = mask.resize(pfp.size, Image.BICUBIC)
                    pfp.putalpha(mask)
                    pfp.save(io.BytesIO(), format='PNG')

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

            choose2 = list(member.name)

            # Fonts
            ########################
            header_font = ImageFont.truetype(font, size=60)
            stat_font = ImageFont.truetype(font, size=50)

            if len(choose2) < 16:
                mem_letter = ImageFont.truetype(basicfont, size=80)

            elif len(choose2) < 21:
                mem_letter = ImageFont.truetype(basicfont, size=70)

            elif len(choose2) < 28:
                mem_letter = ImageFont.truetype(basicfont, size=55)

            else:
                mem_letter = ImageFont.truetype(basicfont, size=45)

            im = Image.new("RGBA", (1250, 1500), (0, 0, 169, 75))
            im_draw = ImageDraw.Draw(im)

            im_draw, im, buffer = pre_renderii(im_draw, im, bg)

            #####################################################################################
            # THE REAL MODE BEGINS!!! (Adding the text)
            #####################################################################################
            im_draw, im = await renderii(
                im,
                im_draw,
                buffer,
                member,
                is_dev,
                is_staff,
                is_donor,
                is_vip,
                level_info,
                data,
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
                if spouses_string != "💔 Nobody":
                    embed.add_field(name=f"Marriages", value=f"{spouses_string}")

                    embed.set_image(url="attachment://pfp_card.png")
                    if member == ctx.author:
                        await ctx.send(
                            # content=f"Here is your profile, {member}!",
                            file=dFile(fp=buffer, filename="pfp_card.png"),
                            embed=embed,
                        )
                    else:
                        await ctx.send(
                            # content=f"Here is **{member}**'s profile, {ctx.author}!",
                            file=dFile(fp=buffer, filename="pfp_card.png"),
                            embed=embed,
                        )
                else:
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
                        "I can't `Embed Links` or `Attach Files`. Please ensure I have these permissions!"
                    )
                try:
                    await ctx.author.send(
                        "I can't `Send Messages`, `Embed Links`, or `Attach Files`. Please double check my permissions!"
                    )
                except discord.Forbidden:
                    pass

    @commands.command()
    @commands.guild_only()
    async def away(self, ctx, *, message=None):
        async with self.bot.pool.acquire() as db:
            is_away = await db.fetchval(
                "SELECT away FROM botsettings_user WHERE id=$1", ctx.author.id
            )
            if is_away:
                await db.execute(
                    "UPDATE botsettings_user SET away=$1 WHERE id=$2",
                    False,
                    ctx.author.id,
                )
                await send_message(ctx, message=f"Welcome back, {ctx.author.mention}")
            else:
                if message is None:
                    message = "I am away right now"
                await db.execute(
                    "UPDATE botsettings_user SET away=$1, away_message=$2 WHERE id=$3",
                    True,
                    message,
                    ctx.author.id,
                )
                await send_message(ctx, message="Please dun be long ;_;")

    @commands.command(name="help", aliaes=['halp'])
    async def help(self, ctx, *, cmd: str = None):
        paws = CustomEmotes.get_emote(True)
        blank = CustomEmotes.get_utility_emote("blank")
        users = len([member for member in self.bot.users if not member.bot])
        embed = discord.Embed(color=self.bot.color,
                              description="For additional command help:\n"
                                          f"{blank}``furhelp command name``")
        if cmd is None:
            # Image Logic
            if isinstance(ctx.channel, discord.TextChannel):
                if ctx.channel.is_nsfw():
                    embed.set_image(url="")
                else:
                    embed.set_image(url="")
            else:
                embed.set_image(url="")
            embed.add_field(name="🗒️ **Command Help**",
                            value=f"**[Command Documentation](https://sheri.bot/commands)**\n"
                                  f"{blank}``https://sheri.bot/commands``", inline=False)
            embed.add_field(name="🖥️ **API Help**",
                            value=f"**[API Documentation](https://sheri.bot/api/)**\n"
                                  f"{blank}``https://sheri.bot/api``", inline=False)
            if ctx.guild:
                embed.add_field(name="🎛️ **Dashboard**",
                                value=f"**[{ctx.guild.name}'s "
                                      f"Dashboard](https://sheri.bot/settings/guild/{ctx.guild.id})**\n"
                                      f"{blank}``https://sheri.bot/settings``", inline=False)
            embed.add_field(name="📡 **Misc Resources**",
                            value="**[Sheri's Lore](https://sheri.bot/lore)**\n"
                                  f"{blank}``https://sheri.bot/lore``\n"
                                  "**[Sheri's Twitter](https://twitter.sheri.bot/)**\n"
                                  f"{blank}``https://twitter.sheri.bot/``\n"
                                  "**[Sheri's Status](https://status.sheri.bot/)**\n"
                                  f"{blank}``https://status.sheri.bot``")
            embed.add_field(name="💰 **Donate**",
                            value="Hosting isn't cheap!\n"
                                  "By chipping in to help, you ensure that sheri will stay alive 24/7\n"
                                  "**[Sheri's Patreon](https://patreon.sheri.bot/)**\n"
                                  f"{blank}``https://patreon.sheri.bot/``", inline=False)
            if can_send(ctx) and can_embed(ctx):
                await ctx.send(content=f"{paws} Servers: ``{len(self.bot.guilds):,}`` | Members: ``{users:,}`` {paws}",
                               embed=embed)
            elif can_send(ctx):
                return await ctx.send(
                    "I cannot send embedded messages in this channel. "
                    "The `Embed Links` permission is required for the help command to work.\n"
                    "You can also refer to my command documentation at <https://sheri.bot/commands>.")
        else:
            command = self.bot.get_command(cmd)
            if command is None:
                return await ctx.send(f"{cmd} is not a command.")
            if command.aliases != "[]":
                aliases_list = ", ".join(command.aliases)
            else:
                aliases_list = "None"
            if command.help is not None:
                command_help = command.help
            else:
                command_help = f"Help information for {command.name} has not been entered. " \
                               f"Contact my developers with ``furreport bug``"

            embed.set_author(name="")
            embed.add_field(name=f"**Command: {command.name}**",
                            value=f"{command_help}\n"
                                  f"{blank}**Aliases:** {aliases_list}\n"
                                  f"{blank}**Arguments:** {command.signature}")
            await ctx.send(embed=embed)

    @commands.command(name="feedback")
    async def feedback(self, ctx, *, feedback_text: str):
        channel = self.bot.get_guild(346892627108560901).get_channel(677577723954200619)
        embed = discord.Embed(color=self.bot.color,
                              title=f"Feedback from {ctx.author.display_name}",
                              description=feedback_text)
        embed.set_author(name=ctx.guild.name, icon_url=icon_check(ctx.guild)).set_footer(
            text=f"USER ID: {ctx.author.id}")
        embed.set_thumbnail(url=avatar_check(ctx.author))
        await channel.send(content="New Feedback!", embed=embed)
        await ctx.send(
            "Thank you for providing your feedback! "
            "If you want to get directly in touch with us more easily, consider joining <https://discord.gg/sheri>!")


def setup(bot):
    bot.add_cog(General(bot))
