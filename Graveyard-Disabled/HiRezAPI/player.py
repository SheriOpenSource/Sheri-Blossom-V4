from typing import Union, List, Optional, SupportsInt

from .enumerations import Language, Platform, Region
from .exceptions import Private
from .items import Loadout
from .match import PartialMatch
from .stats import Stats, RankedStats, ChampionStats
from .status import PlayerStatus
from .utils import convert_timestamp, Duration


class PartialPlayer:
    """
    This object stores basic information about a player, such as their Player ID, Player Name
    and their Platform. Depending on the way it was created, only the Player ID is guaranteed
    to exist - both ``name`` and ``platform`` can be an empty string and `Platform.Unknown`
    respectively.

    To ensure all attributes are filled up correctly before processing, use the `expand` method.

    Attributes
    ----------
    id : int
        ID of the player.
    name : str
        Name of the player.
    platform : Platform
        The player's platform.
    """
    def __init__(self, api, *, id: SupportsInt, name: str = '', platform: Union[str, int] = 0):
        self._api = api
        self.id = int(id)
        self.name = name
        if type(platform) == str and platform.isdecimal():
            platform = int(platform)
        self.platform = Platform.get(platform) or Platform(0)

    def __eq__(self, other) -> bool:
        assert isinstance(other, self.__class__)
        return self.id != 0 and other.id != 0 and self.id == other.id

    def __repr__(self):
        platform = self.platform.name if self.platform else None
        return "{0.__class__.__name__}: {0.name}({0.id} / {1})".format(self, platform)

    @property
    def private(self) -> bool:
        """
        Checks to see if this profile is Private or not.

        Trying to fetch any information for a Private profile will raise the `Private` exception.

        Returns
        -------
        bool
            `True` if this player profile is considered Private, `False` otherwise.
        """
        return self.id == 0

    async def expand(self) -> Optional['Player']:
        """
        Expands and refreshes the information stored inside this object.

        Uses up a single request.

        Returns
        -------
        Optional[Player]
            A full player object with all fields filled up, for the same player.\n
            `None` is returned if this player could not be found.

        Raises
        ------
        Private
            The player's profile was Private.
        """
        if self.private:
            raise Private
        response = await self._api.request("getplayer", self.id)
        if response:
            return Player(self._api, response[0])

    async def get_status(self) -> Optional[PlayerStatus]:
        """
        Fetches the player's current status.

        Uses up a single request.

        Returns
        -------
        Optional[PlayerStatus]
            The player's status.\n
            `None` is returned if this player could not be found.

        Raises
        ------
        Private
            The player's profile was Private.
        """
        if self.private:
            raise Private
        response = await self._api.request("getplayerstatus", self.id)
        if response and response[0]["status"] != 5:
            return PlayerStatus(self, response[0])

    async def get_friends(self) -> List['PartialPlayer']:
        """
        Fetches the player's friend list.

        Uses up a single request.

        Returns
        -------
        List[PartialPlayer]
            A list of players this player is friends with.

        Raises
        ------
        Private
            The player's profile was Private.
        """
        if self.private:
            raise Private
        response = await self._api.request("getfriends", self.id)
        return [PartialPlayer(self._api, id=p["player_id"], name=p["name"]) for p in response]

    async def get_loadouts(self, language: Language = Language.English) -> List[Loadout]:
        """
        Fetches the player's loadouts.

        Uses up a single request.

        Parameters
        ----------
        language : Language
            The `Language` you want to fetch the information in.
            Defaults to `Language.English`

        Returns
        -------
        List[Loadout]
            A list of player's loadouts.

        Raises
        ------
        Private
            The player's profile was Private.
        """
        assert isinstance(language, Language)
        if self.private:
            raise Private
        # ensure we have champion information first
        await self._api.get_champion_info(language)
        response = await self._api.request("getplayerloadouts", self.id, language.value)
        if not response or response and not response[0]["playerId"]:
            return []
        return [Loadout(self, language, l) for l in response]

    async def get_champion_stats(
        self, language: Language = Language.English
    ) -> List[ChampionStats]:
        """
        Fetches the player's champion statistics.

        Uses up a single request.

        Parameters
        ----------
        language : Language
            The `Language` you want to fetch the information in.
            Defaults to `Language.English`

        Returns
        -------
        List[ChampionStats]
            A list of champion statistics objects, one for each played champion.

        Raises
        ------
        Private
            The player's profile was Private.
        """
        assert isinstance(language, Language)
        if self.private:
            raise Private
        # ensure we have champion information first
        await self._api.get_champion_info(language)
        response = await self._api.request("getgodranks", self.id)
        return [ChampionStats(self, language, s) for s in response]

    async def get_match_history(self, language: Language = Language.English) -> List[PartialMatch]:
        """
        Fetches player's match history.

        Uses up a single request.

        Parameters
        ----------
        language : Language
            The `Language` you want to fetch the information in.
            Defaults to `Language.English`

        Returns
        -------
        List[PartialMatch]
            A list of partial matches, containing statistics for the current player only.

        Raises
        ------
        Private
            The player's profile was Private.
        """
        assert isinstance(language, Language)
        if self.private:
            raise Private
        # ensure we have champion information first
        await self._api.get_champion_info(language)
        response = await self._api.request("getmatchhistory", self.id)
        if not response or response and response[0]["ret_msg"]:
            return []
        return [PartialMatch(self, language, m) for m in response]


class Player(PartialPlayer):
    """
    A full Player object, containing all the information about a player.

    This inherits from `PartialPlayer`, so all it's methods should be present here as well.

    Attributes
    ----------
    id : int
        ID of the player.
    name : str
        Name of the player.
    platform : Platform
        The player's platform.
    active_player : Optional[PartialPlayer]
        The current active player between merged profiles.\n
        `None` if the current profile is the active profile.
    merged_players : List[PartialPlayer]
        A list of all merged profiles.
    created_at : datetime
        A timestamp of the profile's creation date.
    last_login : datetime
        A timestamp of the profile's last successful in-game login.
    level : int
        The in-game level of this profile.
    playtime : Duration
        The amount of time spent playing on this profile.
    champions_count : int
        The amount of champions this player unlocked.
    region : Region
        The player's currently set Region.
    total_achievements : int
        The amount of achievements the player has.
    total_exp : int
        The total amount of experience the player has.
    casual : Stats
        Player's casual statistics
    ranked_keyboard : RankedStats
        Player's ranked keyboard statistics
    ranked_controller : RankedStats
        Player's ranked controller statistics
    """
    def __init__(self, api, player_data):
        super().__init__(
            api,
            id=player_data["Id"],
            name=player_data["Name"],
            platform=player_data["Platform"],
        )
        if player_data["ActivePlayerId"] != self.id:
            self.active_player = PartialPlayer(api, id=player_data["ActivePlayerId"])
        else:
            self.active_player = None
        self.merged_players = []
        if player_data["MergedPlayers"]:
            for p in player_data["MergedPlayers"]:
                self.merged_players.append(
                    PartialPlayer(api, id=p["playerId"], platform=p["portalId"])
                )
        self.created_at = convert_timestamp(player_data["Created_Datetime"])
        self.last_login = convert_timestamp(player_data["Last_Login_Datetime"])
        self.level = player_data["Level"]
        self.playtime = Duration(hours=player_data["HoursPlayed"])
        self.champions_count = player_data["MasteryLevel"]
        self.region = Region.get(player_data["Region"]) or Region(0)
        self.total_achievements = player_data["Total_Achievements"]
        self.total_exp = player_data["Total_Worshippers"]
        self.hz_gamer_tag = player_data["hz_gamer_tag"]
        self.hz_player_name = player_data["hz_player_name"]
        self.casual = Stats(player_data)
        self.ranked_keyboard = RankedStats("Keyboard", player_data["RankedKBM"])
        self.ranked_controller = RankedStats("Controller", player_data["RankedController"])

    @property
    def ranked_best(self) -> RankedStats:
        """
        Returns the best ranked stats between the keyboard and controller ones.

        If the rank is the same, winrate is used to determine the one returned.
        """
        if self.ranked_controller.rank == self.ranked_keyboard.rank:
            return max(self.ranked_keyboard, self.ranked_controller, key=lambda r: r.winrate)
        return max(self.ranked_keyboard, self.ranked_controller, key=lambda r: r.rank)
