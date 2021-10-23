from dataclasses import dataclass
from Functions.errors import InvalidEndpoint, NSFWEndpoint
endpoints_nsfw = [
    "lesbian",
    "gay",
    "nboop",
    "nbound",
    "nbrony",
    "nbulge",
    "ncomics",
    "dick",
    "dp",
    "yiff",
    "nfemboy",
    "nfuta",
    "ngroup",
    "npokemon",
    "pussy",
    "nseduce",
    "nsolo",
    "nspank",
    "ntease",
    "ntrap",
    "nhug",
    "nkiss",
    "nhold",
    "ncuddle",
    "nlick",
    "finger",
    "suck",
    "bang",
    "gif",
    "cuntboy",
    "christmas",
    "fcreampie",
    "mcreampie",
    "pregnant",
    "cumflation",
    'booty',
    'fsolo',
    'msolo',
    'boob',
    'ride',
    'mbound',
    'fbound',
    '69',
    'ftease',
    'mtease',
    'anal',
    'fseduce',
    'mseduce',
    'tentacles',
    'petplay',
    'fpresentation',
    'maws'
]
endpoints_sfw = [
    "bunny",
    "fox",
    "hold",
    "hug",
    "kiss",
    "lick",
    "mur",
    "nature",
    "pig",
    "snep",
    "trickortreat",
    "wolves",
    "husky",
    'shiba',
    'cat',
    'paws'
]


@dataclass
class Endpoints:

    @staticmethod
    def check_endpoint(endpoint: str, channel_is_nsfw: bool):
        # Check to see if the endpoint is valid
        if endpoint not in endpoints_nsfw + endpoints_sfw:
            return [False, "unknown", f"``{endpoint}`` is not a valid endpoint!"]
        # check to see if the endpoint is in the channel and if its nsfw, If it is, then return true...
        if endpoint in endpoints_nsfw:
            if channel_is_nsfw is False:
                return [False, 'error', f"``{endpoint}`` is a nsfw endpoint and it cannot be used in sfw channels. Sorry!"]
            else:
                return [True, "NSFW"]
        if endpoint in endpoints_sfw:
            return [True, "SFW"]

    @staticmethod
    def list_endpoints(sfw: bool, nsfw: bool):
        if nsfw is True and sfw is True:
            nsfw_endpoint_list = ", ".join(endpoints_nsfw)
            sfw_endpoint_list = ", ".join(endpoints_sfw)
            return [sfw_endpoint_list, nsfw_endpoint_list]
        if nsfw:
            nsfw_endpoint_list = ", ".join(endpoints_nsfw)
            return nsfw_endpoint_list
        else:
            sfw_endpoint_list = ", ".join(endpoints_sfw)
            return sfw_endpoint_list






