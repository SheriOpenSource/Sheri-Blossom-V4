import asyncio
import itertools
import random
from enum import Enum

import discord
from discord.ext import commands

from Functions.randomization import advchoice

NUM_ENC = "\N{COMBINING ENCLOSING KEYCAP}"


class SMReel(Enum):
    seven = "7⃣"
    cookie = "🍪"
    paw = "🐾"
    flc = "🍀"
    fox = "🦊"
    cat = "🐱"
    wolf = "🐺"
    diamond = "💠"
    heart = "💙"
    snowflake = "❄"


PAYOUTS = {
    (SMReel.paw, SMReel.paw, SMReel.paw): {
        "payout": lambda x: x * 2500,
        "phrase": "__**JACKPOT!**__ **Triple Paw Prints! Your bid has been multiplied** __**x2500!**__",
    },
    (SMReel.flc, SMReel.flc, SMReel.flc): {
        "payout": lambda x: x + 1000,
        "phrase": "__**4LC! +1000!**__",
    },
    (SMReel.seven, SMReel.seven, SMReel.seven): {
        "payout": lambda x: x + 777,
        "phrase": "__**Tripple seven! +777!**__",
    },
    (SMReel.paw, SMReel.wolf): {
        "payout": lambda x: x * 4,
        "phrase": "__**Paw Prints + Wolf!**__ **Your bid has been multiplied** __**x4!**__",
    },
    (SMReel.paw, SMReel.fox): {
        "payout": lambda x: x * 4,
        "phrase": "__**Paw Prints + Fox!**__ **Your bid has been multiplied** __**x4!**__",
    },
    (SMReel.paw, SMReel.cat): {
        "payout": lambda x: x * 4,
        "phrase": "__**Paw Prints + Cat!**__ **Your bid has been multiplied** __**x4!**__",
    },
    (SMReel.seven, SMReel.seven): {
        "payout": lambda x: x * 3,
        "phrase": "__**Double sevens!**__ **Your bid has been multiplied** __**x3!**__",
    },
    "3 symbols": {
        "payout": lambda x: x + 500,
        "phrase": "__**Three symbols! +500!**__",
    },
    "2 symbols": {
        "payout": lambda x: x * 2,
        "phrase": "__**Two consecutive symbols!**__ **Your bid has been multiplied** __**x2!**__",
    },
}

SLOT_PAYOUTS_MSG = (
    "Slot machine payouts:\n"
    "{paw.value} {paw.value} {paw.value} Bet * 2500\n"
    "{flc.value} {flc.value} {flc.value} +1000\n"
    "{seven.value} {seven.value} {seven.value} +800\n"
    "{paw.value} {wolf.value} Bet * 4\n"
    "{paw.value} {fox.value} Bet * 4\n"
    "{paw.value} {cat.value} Bet * 4\n"
    "{seven.value} {seven.value} Bet * 3\n\n"
    "Three symbols: +500\n"
    "Two symbols: Bet * 2".format(**SMReel.__dict__)
)


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="roll")
    async def roll_index(self, ctx):
        """Roll some dice!"""
        if ctx.invoked_subcommand is None:
            return await ctx.send("choose between 6d or 20d")

    async def get_balance(self, user):
        async with self.bot.pool.acquire() as db:
            balance = await db.fetchrow(
                "SELECT coins FROM botsettings_user WHERE id=$1", user.id
            )
            return balance

    @roll_index.command(name="20d", aliases=["d20"])
    @commands.max_concurrency(1, commands.BucketType.user)
    async def d20(self, ctx, dices: str = None):
        """Roles dice that goes up to 20"""
        if dices is None:
            dices = "1"
        if dices.isdigit():
            if int(dices) > 3:
                dices = "3"
            msg1 = await ctx.send(
                "<a:ooh:473963385269125130> Rolling the dice <a:ooh:473963385269125130>"
            )
            await asyncio.sleep(2)
            msg = ""
            counter = 0
            for i in range(int(dices)):
                counter += 1
                dice = random.randint(1, 20)
                msg += f"🎲 {counter} : {dice}\n"

            await msg1.edit(content="Done!\n" f"{msg}")
        else:
            await ctx.send("Hey, provide a number, not words k?")

    @roll_index.command(name="6d", aliases=["d6"])
    @commands.max_concurrency(1, commands.BucketType.user)
    async def d6(self, ctx, dices: str = None):
        """Roll the dice"""
        if dices is None:
            dices = "1"
        if dices.isdigit():
            if int(dices) > 3:
                dices = "3"
            msg1 = await ctx.send(
                "<a:ooh:473963385269125130> Rolling the dice <a:ooh:473963385269125130>"
            )
            await asyncio.sleep(2)
            msg = ""
            counter = 0
            for i in range(int(dices)):
                counter += 1
                dice = random.randint(1, 6)
                msg += f"🎲 {counter} : {dice}\n"
                await asyncio.sleep(1)
                await msg1.edit(
                    content=f"<a:ooh:473963385269125130> Rolling the dice <a:ooh:473963385269125130>\n"
                            f"{msg}"
                )
            await msg1.edit(content="Done!\n" f"{msg}")
        else:
            await ctx.send("Hey, provide a number, not words k?")

    @commands.command(aliases=["wheel"])
    async def wheeloffortune(self, ctx, *, bid: int):
        """Bet your currency on the wheel of fortune"""
        try:
            async with self.bot.pool.acquire() as db:
                author = ctx.message.author
                values = [0.1, 0.2, 0.3, 0.5, 1.2, 1.5, 1.7, 2.4]
                bal = await db.fetchrow(
                    "SELECT coins FROM botsettings_user WHERE id=$1", author.id
                )
                coins = old_bal = bal["coins"]
                # coins = bal["coins"]
                fortune = random.choice(values)
                if bid < 10:
                    return await ctx.send("Bid must be at least 10!")
                if bal["coins"] >= bid:
                    coins -= bid
                    if fortune == 0.1:
                        arrow = ":arrow_lower_left:"
                        color = 0xFF0000
                    elif fortune == 0.2:
                        arrow = ":arrow_left:"
                        color = 0xFF0000
                    elif fortune == 0.3:
                        arrow = ":arrow_down:"
                        color = 0xFF0000
                    elif fortune == 0.5:
                        arrow = ":arrow_lower_right:"
                        color = 0xFF0000
                    elif fortune == 1.2:
                        arrow = ":arrow_right:"
                        color = 0x80F5FF
                    elif fortune == 1.5:
                        arrow = ":arrow_upper_left:"
                        color = 0x80F5FF
                    elif fortune == 1.7:
                        arrow = ":arrow_up:"
                        color = 0x80F5FF
                    else:
                        arrow = ":arrow_upper_right:"
                        color = 0x80F5FF
                    winning = int(round(bid * fortune))
                    new_bal = coins + winning
                    # old_bal += winning
                    desc = "__**Your Bid**__**={}**\n__**Reward**__**={}**".format(
                        bid, winning
                    )
                    em = discord.Embed(description=desc, color=color)
                    em.add_field(
                        name="Wheel:",
                        value="『1.5』『1.7』『2.4』\n\n"
                              "『0.2』   {}   『1.2』\n\n"
                              "『0.1』『0.3』『0.5』".format(arrow),
                    )
                    em.add_field(
                        name="Wheel Result:",
                        value="**Your bid has been multiplied by {}!**".format(fortune),
                        inline=False,
                    )
                    em.set_author(name="Wheel of Fortune!")
                    em.set_thumbnail(url=author.avatar_url)
                    em.set_footer(text=f"Balance: Before={old_bal:,} Now={new_bal:,}")
                    await ctx.send(embed=em)
                    await db.execute(
                        "UPDATE botsettings_user SET coins=$1 WHERE id=$2",
                        new_bal,
                        author.id,
                    )
                else:
                    desc = "You don't have enough coins!"
                    em = discord.Embed(description=desc, color=0xFF0000)
                    await ctx.send(embed=em)
        except Exception as e:
            await ctx.send("Oops, Logged in sentry")
            self.bot.sentry.capture_exception(e)

    @commands.command(aliases=["fight"], hidden=True)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def duel(self, ctx, user: discord.Member = None):
        """Duel with other people."""
        # return
        if not user:
            return await ctx.send("You need to mention someone to duel!")

        if user == ctx.author:
            return await ctx.send("Stop hitting yourself!")

        weapons_variants = {
            "Shuriken": [
                "Bloody Shuriken",
                "Fluffy Shuriken",
                "Crooked Shuriken",
                "Poisoned Shuriken",
                "Silly Shuriken"
            ],
            "Long Sword": [
                "Bloody Long Sword",
                "Fluffy Long Sword",
                "Charged Long Sword",
                "Sour Apple Long Sword",
                "Silly Long Sword"
            ],
            "Sniper": [
                "7.62 Tkiv 85",
                "Amr-2",
                "Armalite AR-50",
                "Barrett M82",
                "Barrett M90",
                "Barrett M95",
                "Barrett 98B",
                "Barrett M99",
                "Barrett XM109",
                "Blaser R93",
                "Blaser 93 Tactical",
                "Bor rifle",
                "C14 Timberwolf",
                "CheyTac Intervention",
                "Denel NTW-20",
                "Desert Tech SRS",
                "Dragunov sniper rifle",
                "Dragon SVU",
                "DSR-Precision",
                "EDM Arms Windrunner",
                "Falcon (sniper rifle)",
                "FN Ballista",
                "FR F1",
                "Gewehr 98", "M14 rifle"],
            "Carbine": [
                "9A-91",
                "AGM-1 Carbine",
                "AK-101",
                "AK-102",
                "AK-103",
                "AK-104",
                "AK-105",
                "AKMSU",
                "AKS-74U",
                "Amogh carbine",
                "AO-46",
                "AR-57",
                "Beretta Cx4 Storm",
                "Berthier carbine",
                "Burnside carbine",
                "CETME Model LC carbine",
                "Chapina carbine",
                "Colt Model 1839 Carbine",
                "FR8",
                "FX-05 XiuhcoatI carbine",
                "G13 carbine",
                "Grendel R31",
                "HK416A5",
                "HK G36C",
                "Hi-Point 995",
                "HIW VSL",
                "K31",
                "Karabinek wz. 91/98/23",
                "Karabiner 98k",
                "Kbk wz. 1996 Mini-Beryl",
                "Kel-Tec SUB-2000",
                "Krag–Jørgensen (M-1899 Carbine)",
                "L22 Carbine",
                "M1 carbine"
            ],
            "Rocket Launcher": [
                "Cookie Launcher",
                "Plushie Launcher",
                "Air Launcher",
                "Underwear Launcher",
                "Fuzzy Launcher",
                "Snow Launcher",
                "Leaf Launcher",
                "9K38 Igla",
                "AT4",
                "Bazooka",
                "C-100",
                "C90-CR (M3)",
                "Dard 120",
                "FIM-43 Redeye",
                "FIM-92 Stinger",
                "FHJ-84",
                "GROM",
                "LAW 80",
                "LRAC F1",
                "M202A1 FLASH",
                "M92 LAW",
                "Nexter WASP 58 Light Anti-Armour Weapon",
                "Panzerfaust 3",
                "Panzerschreck",
                "PF-89", "PF-98", "RPG",
                "Type 70", "SA-7", "SA-14",
                "VE-NILANGAL"
            ],
            "Food": [
                "Apple", "Banana", "Peach", "Sour Apple", "Raisin", "Paw Bean"
            ],
            "Objects": [
                "Frying Pan",
                "Baseball",
                "Clothes",
                "Stink Bomb",
                "Rock",
                "Scissors",
                "Paw Bean"
            ]

        }
        battle_data = {
            "Battle Lines": [
                "{0} slaps {1} with a {2}.",
                "{0} nommed on {1}",
                "{0} flips {1}",
                "{0} ties {1} up with a {2}.",
                "{0} launches {1} with a {2}.",
                "{0} tickles {1}.",
                "{0} force feeds {1}",
                "{0} pins {1} down with a {2}",
                "{0} pukes on {1}",
                "{0} screams at {1}",
                "{0} charges at {1} with a {2}",
                "{0} gases out {1}",
                "{0} shoots {1} with a {2}",
                "{0} muffles {1}",
                "{0} makes {1} puke",
                "{0} nags {1}",
                "{0} annoys {1} with a {2}",
                "{0} makes {1} cry",
                "{0} makes {1} laugh",
                "{0} throws a {2} at {1}",

            ],
            "Sniper Lines": [
                "{0} snipes {1} from a window with a {2}",
                "{0} decides to snipe {1} with a {2}",
                "{0} fires a {2}, hitting {1}"],
            "Rocket Lines": [
                "{0} blasts {1} off the face of the earth with a {2}",
                "{0} burns {1} when they fired a {2}",
                "{0} put {1} in a fireball when they fired a {2}"],
            "Carbine Lines": [
                "{0} blows holes into {1} with a {2}",
                "{0} decided to pull out their {2} and fire at {1}",
                "{0} went ahead, without mercy, fires at {1} with a {2}"],
            "Weapons": {
                "Shuriken": {
                    "damage": advchoice(range(9, 15)),
                    "name": advchoice(weapons_variants["Shuriken"]),
                },
                "Long Sword": {
                    "damage": advchoice(range(4, 25)),
                    "name": advchoice(weapons_variants["Long Sword"]),
                },
                "Rocket Launcher": {
                    "damage": advchoice(range(3, 20)),
                    "name": advchoice(weapons_variants['Rocket Launcher'])
                },
                "Sniper": {
                    "damage": advchoice(range(12, 30)),
                    "name": advchoice(weapons_variants["Sniper"])
                },
                "Carbine": {
                    "damage": advchoice(range(2, 11)),
                    "name": advchoice(weapons_variants["Carbine"])
                },
                "Food": {
                    "damage": advchoice(range(1, 10)),
                    "name": advchoice(weapons_variants['Food'])
                },
                "Objects": {
                    "damage": advchoice(range(3, 10)),
                    "name": advchoice(weapons_variants['Objects'])
                }
            },
        }

        weapons_directory = [
            battle_data["Weapons"]["Shuriken"],
            battle_data["Weapons"]["Long Sword"],
            battle_data['Weapons']['Rocket Launcher'],
            battle_data['Weapons']['Sniper'],
            battle_data['Weapons']['Carbine'],
            battle_data['Weapons']['Food'],
            battle_data['Weapons']['Objects']
        ]
        attacker = ctx.author.name
        attacker_hp = 100
        defender = user.name
        defender_hp = 100
        moves = 1
        attackers = [attacker, defender]
        victim = [defender, attacker]

        rng2 = itertools.cycle(attackers)
        rng3 = itertools.cycle(victim)
        battle_log = ""
        msg = await ctx.send(f"**{attacker}** has started attacking **{defender}**")
        while defender_hp > 0 and attacker_hp > 0:
            moves += 1
            # rng = advchoice(battle_data["Battle Lines"])

            atk = next(rng2)
            vic = next(rng3)
            # print(f"{atk} attacker")
            # print(f"{vic}  victim")
            weapons = random.choice(weapons_directory)
            # Battle Dialouge
            if weapons == battle_data['Weapons']['Rocket Launcher']:
                rng = advchoice(battle_data["Rocket Lines"])
            elif weapons == battle_data['Weapons']['Sniper']:
                rng = advchoice(battle_data["Sniper Lines"])
            elif weapons == battle_data['Weapons']['Carbine']:
                rng = advchoice(battle_data["Carbine Lines"])
            else:
                rng = advchoice(battle_data["Battle Lines"])
            # Battle Damage
            if atk == attacker:
                defender_hp -= weapons["damage"]
            if atk == defender:
                attacker_hp -= weapons["damage"]
            battle_log += f"{rng.format(atk, vic, weapons['name'])}\n"
            embed = discord.Embed(description=battle_log, color=self.bot.color)
            embed.add_field(
                name=attacker, value=f"Current Health: {attacker_hp}"
            )
            embed.add_field(name=defender, value=f"Current Health: {defender_hp}")
            try:
                await msg.edit(embed=embed)
            except (discord.Forbidden, discord.NotFound):
                return
            
            await asyncio.sleep(2.5)
        if defender_hp >= 0:
            await ctx.send(f"{defender} Won the duel!")
        elif attacker_hp >= 0:
            await ctx.send(f"{attacker} Won the duel!")

    @commands.command(name="betroll", aliases=["br"])
    async def bet_roll(self, ctx, *, bid: int):
        """ Bet your currency on a roll """
        async with self.bot.pool.acquire() as db:
            author = ctx.message.author
            bal = await db.fetchrow(
                "SELECT coins FROM botsettings_user WHERE id=$1", author.id
            )
            old_bal = bal["coins"]
            coins = bal["coins"]
            num = random.randint(0, 100)
            if bid <= 0:
                return await ctx.send("Bid must be more than 0!")
            if bal["coins"] >= bid:
                coins -= bid
                if num == 100:
                    result = bid * 10
                    color = 0x80F5FF
                    message = (
                        "**Your bet has been multiplied by** __**10**__**!:crown:**"
                    )
                elif num >= 90:
                    result = bid * 4
                    color = 0x80F5FF
                    message = "**Your bet has been multiplied by** __**4**__**!**"
                elif num >= 66:
                    result = bid * 2
                    color = 0x80F5FF
                    message = "**Your bet has been multiplied by** __**2**__**!**"
                else:
                    result = bid * 0
                    color = 0xFF0000
                    message = "__**You have lost!**__"
                new_bal = coins + result
                coins += result
                if num == 100:
                    top_num = "---"
                    bottom_num = "99"
                elif num == 0:
                    top_num = "1"
                    bottom_num = "---"
                else:
                    top_num = num + 1
                    bottom_num = num - 1
                desc = "__**Your Bid**__**={}**\n__**Reward**__**={}**".format(
                    bid, result
                )
                em = discord.Embed(description=desc, color=color)
                em.add_field(
                    name="Roll:",
                    value="-{}-\n**>{}<**\n-{}-".format(top_num, num, bottom_num),
                )
                em.add_field(name="Roll Result:", value=message, inline=False)
                em.set_author(name="Bet Roll!")
                em.set_thumbnail(url=author.avatar_url)
                em.set_footer(text=f"Balance: Before={old_bal:,} Now={new_bal:,}")
                await ctx.send(embed=em)
                await db.execute(
                    "UPDATE botsettings_user SET coins=$1 WHERE id=$2",
                    new_bal,
                    author.id,
                )
            else:
                desc = "You don't have enough coins!"
                em = discord.Embed(description=desc, color=0xFF0000)
                await ctx.send(embed=em)

    @commands.command(aliases=["flip"])
    async def coin(self, ctx):
        res = random.randint(1, 2)

        if res == 1:
            await ctx.send("Coin says heads, better luck next time tails.")
        elif res == 2:
            await ctx.send("Coin says tails, better luck next time heads.")


def setup(bot):
    bot.add_cog(Games(bot))
