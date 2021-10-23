import discord
from discord.ext import commands

from Functions.core import send_message

from API.HiRezAPI import *
from Lines.custom_emotes import paladins_ranks

DEV_ID = "3429"  # Your Developer ID (example)
AUTH_KEY = "80212A1130304A67AAB41DF9BABA1BA7"  # Your Auth Key (example)


class Hirez(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hirezapi = PaladinsAPI(DEV_ID, AUTH_KEY)

    def cog_unload(self):
        self.bot.loop.create_task(self.hirezapi.close())

    @commands.group(name='paladin', aliases=['paladins', 'pal'])
    async def paladins_index(self, ctx):
        if not ctx.invoked_subcommand:
            return await ctx.send("WIP")

    @paladins_index.command(name='player', aliases=['stats'])
    async def paladins_player(self, ctx, player_name: str, platform: str = None):
        if not player_name:
            return await ctx.send("You need to provide a name for me to search for.")
        if platform:
            p = Platform.get(platform)
        else:
            p = Platform.get('PC')
        player_list = await self.hirezapi.search_players(player_name, p)
        if player_list:
            if len(player_list) > 1:
                return await send_message(ctx, message="Multiple players have been found with this name and platform.\n"
                                                       f"Number of players with same name and platform: "
                                                       f"{len(player_list):,}\n"
                                                       f"Please redo the command using your player ID, "
                                                       f"which can be found by going to your in-game Profile, at the bottom-right.")
            player = await player_list[0].expand()
            if player is None:
                await send_message(ctx, message="Are you sure this player exists? I can't seem to find this user.\n"
                                                "If the player you are searching for exists,"
                                                " please make sure your profile is set to public"
                                                " in the in-game settings.")
        else:
            return await send_message(ctx, message="Are you sure this player exists? I can't seem to find this user.\n"
                                                   "If the player you are searching for exists,"
                                                   " please make sure your profile is set to public"
                                                   " in the in-game settings.")

        embed = discord.Embed(color=discord.Colour.teal(), title=player.name + f" [{player.platform.name}]",
                              description=f"Level: ``{player.level}``\n"
                                          f"Region: ``{player.region}``\n"
                                          f"Total EXP: ``{str(player.total_exp)}``\n"
                                          f"Total Achievements: ``{player.total_achievements}``\n"
                                          f"Total Champions: ``{[player.champions_count]}``\n"
                                          f"Last Login: ``{player.last_login}``\n"
                                          f"Hours Played: ``{player.playtime.total_hours()}`` Hours\n"
                                          f"Created: ``{player.created_at.date()}``")
        if player.ranked_best is not None:
            embed.add_field(name=f"**Ranked Stat**",
                            value=f"Ranked Type: ``{player.ranked_best.type}``\n"
                                  f"Rank: ``{player.ranked_best.rank.name}``\n"
                                  f"Points: ``{player.ranked_best.points} / 100``\n"
                                  f"Wins / Losses: Wins: ``{player.ranked_best.wins}`` "
                                  f"Losses: ``{player.ranked_best.losses}``\n"
                                  f"Winrate: ``{player.ranked_best.winrate_text}``\n"
                                  f"Leaves: ``{player.ranked_best.leaves}``",
                            inline=False)
            embed.set_thumbnail(
                url=f"https://sheri.bot/media/paladins/rank_icons/{player.ranked_best.rank.value}.png")
        else:
            embed.set_thumbnail(
                url=f"https://sheri.bot/media/paladins/rank_icons/0.png")
        embed.add_field(name="**Casual Stats**",
                        value=f"Total Matches: ``{player.casual.matches_played:,}``\n"
                              f"Total Wins / Losses: W: ``{player.casual.wins:,}`` / L: ``{player.casual.losses:,}``\n"
                              f"Winrate: ``{player.casual.winrate_text}``\n"
                              f"Total Leaves: ``{player.casual.leaves}``",
                        inline=True)
        await send_message(ctx, embed=embed)

    @paladins_index.command(name="current")
    async def paladins_current(self, ctx, player_name: str = None, platform: str = None):
        player = None
        if player_name:
            if platform:
                p = Platform.get(platform)
            else:
                p = Platform.get('PC')
            player_list = await self.hirezapi.search_players(player_name, p)
            if player_list:
                if len(player_list) > 1:
                    return await send_message(ctx,
                                              message="Multiple players have been found with this name and platform.\n"
                                                      f"Number of players with same name and platform: "
                                                      f"{len(player_list):,}\n"
                                                      f"Please redo the command using your player ID, "
                                                      f"which can be found by going to your in-game Profile, at the bottom-right.")
                player = await player_list[0].expand()
                if player is None:
                    await send_message(ctx, message="Are you sure this player exists? I can't seem to find this user.\n"
                                                    "If the player you are searching for exists,"
                                                    " please make sure your profile is set to public"
                                                    " in the in-game settings.")
        else:
            player = await self.hirezapi.get_from_platform(ctx.author.id, platform=Platform.Discord)
            await player.expand()

        if player:
            status = await player.get_status()
            if status:
                try:
                    match = await status.get_live_match()
                    ranked_queues = (Queue.get("kb_comp"), Queue.get("cn_comp"))
                    if match.queue in ranked_queues:
                        team1ids = [lp.player.id for lp in match.team1]
                        team2ids = [lp.player.id for lp in match.team2]
                        team1 = ""
                        team2 = ""
                        obj1 = await self.hirezapi.get_players(team1ids)
                        obj2 = await self.hirezapi.get_players(team2ids)
                        for gamer in obj1:
                            string = f"{paladins_ranks[str(gamer.ranked_best.rank.value)]}{gamer.name}:  " \
                                     f"W: ``{gamer.ranked_best.wins}``, " \
                                     f"L: ``{gamer.ranked_best.losses}``, " \
                                     f"Levs: ``{gamer.ranked_best.leaves}\n"
                            team1 += string
                        for gamer in obj2:
                            string = f"{paladins_ranks[str(gamer.ranked_best.rank.value)]}{gamer.name}: " \
                                     f"W: {gamer.ranked_best.wins}, " \
                                     f"L: {gamer.ranked_best.losses}, " \
                                     f"Levs: {gamer.ranked_best.leaves}\n"
                            team2 += string

                        embed = discord.Embed(color=discord.Colour.teal(), title="Ranked Match (Live)",
                                              description=f"MatchID: {match.id}\n"
                                                          f"Map: {match.map_name}\n"
                                                          f"Region: {match.region}\n")
                        embed.add_field(name="**Red Team**",
                                        value=team1,
                                        inline=True)
                        embed.add_field(name="**Blue Team**",
                                        value=f"{team2}",
                                        inline=True)
                        await send_message(ctx, embed=embed)
                except AttributeError:
                    return await send_message(ctx, message=f"**{player.name}** is not in a match")


def setup(bot):
    bot.add_cog(Hirez(bot))
