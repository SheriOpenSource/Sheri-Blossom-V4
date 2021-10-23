# Apis not managed by us.
import os

from requests import HTTPError

from Formats.formats import pagify

user_agent = {"User-Agent": "Sheri Blossom V4"}

base_urls = {
    "neko": "https://nekos.life/api/v2/img/",
    "boobbot": "https://boob.bot/api/v2/img/",
    "furbot": "https://fur.im/",
    "ducks": "https://random-d.uk/api",
    "random": "https://some-random-api.ml/",
    "alexflipnote": "https://api.alexflipnote.dev/",
    "and-here-is-my-code": "https://and-here-is-my-code.glitch.me/"
}

authorization_keys = {
    "boobbot": {"key": os.environ["BOOBBOT_API_KEY"], "User-Agent": "Sheri Blossom V4"},
}

downtime_image = "https://sheri.bot/media/service-unavaliable.png"

cat_traits = [
    "Experimental",
    "Hairless",
    "Natural",
    "Rare",
    "Rex",
    "Suppressed tail",
    "Short legs",
    "Hypoallergenic",
    "Indoor",
    "Lap"
]

cat_scale = [
    "Adaptability",
    "Affection level",
    "Child friendly",
    "Dog friendly",
    "Energy level",
    "Grooming",
    "Health issues",
    "Intelligence",
    "Shedding level",
    "Social needs",
    "Stranger friendly",
    "Vocalisation"
]


class External_Retrieval:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session

    async def neko_api(self, endpoint):
        async with self.session.get(base_urls["neko"] + endpoint,
                                    headers=user_agent) as resp:
            if resp.status == 200:
                json = await resp.json()
                return json
            else:
                return {"url": downtime_image}

    async def some_random_api_img(self, endpoint):
        async with self.session.get(
                base_urls["random"] + "/img/" + endpoint,
                headers=user_agent,
        ) as resp:
            if resp.status == 200:
                json = await resp.json()
                return json
            else:
                return {"url": downtime_image}

    async def boob_api(self, endpoint):
        async with self.session.get(
                base_urls["boobbot"] + endpoint, headers=authorization_keys["boobbot"]
        ) as resp:
            if resp.status == 200:
                json = await resp.json()
                return json
            else:
                return {"url": downtime_image}

    async def furbot_api(self, endpoint):
        async with self.session.get(
                base_urls["furbot"] + endpoint, headers=user_agent
        ) as resp:
            if resp.status == 200:
                json = await resp.json(content_type="text/html")
                return json
            else:
                return {"file": downtime_image}

    async def duck_api(self, endpoint):
        async with self.session.get(
                base_urls["ducks"] + "/random" + endpoint,
                headers=user_agent,
        ) as resp:
            if resp.status == 200:
                json = await resp.json()
                return json
            else:
                return {"url": downtime_image}

    async def alexflipnote_api(self, endpoint):
        async with self.session.get(
                base_urls["alexflipnote"] + endpoint,
                headers=user_agent,
        ) as resp:
            if resp.status == 200:
                json = await resp.json()
                return json
            elif resp.status == 500:
                raise AttributeError
            elif resp.status == 404:
                raise ValueError

    async def dog(self, breed: str = None):
        url = "https://api.thedogapi.com/v1/images/search?has_breeds=1"
        if breed:
                breeds = {}
                async with self.session.get(
                        url="https://api.thedogapi.com/v1/breeds",
                        headers={"x-api-key": os.getenv("DOG")}
                ) as breed_list:
                    breed_list = await breed_list.json()
                for x in breed_list:
                    breeds[x["name"].lower()] = x["id"]
                if breed.lower() not in breeds:
                    return None, None, None
                url += f"&breed_id={breeds[breed.lower()]}"

        async with self.session.get(
                url=url,
                headers={"x-api-key": os.getenv("DOG")}
        ) as resp:
            if resp.status == 200:
                try:
                    resp = (await resp.json())[0]
                except IndexError:
                    return None, None, None
                
                details = ""
                for x, y in resp["breeds"][0].items():
                    if x not in ["id", "name"]:
                        x = x.capitalize().replace('_', ' ')
                        if x == "Height":
                            height = f"**{x}:** {y['imperial']}in ({y['metric']}cm)\n"
                            continue
                        if x == "Weight":
                            weight = f"**{x}:** {y['imperial']}lb ({y['metric']}kg)\n"
                            continue
                        details += f"**{x}:** {y}\n"
                details += height + weight
                return resp["url"], resp["breeds"][0]["name"], details
            return raise_for_status(resp)

    async def dog_breeds(self):
        async with self.session.get(
                url="https://api.thedogapi.com/v1/breeds",
                headers={"x-api-key": os.getenv("DOG")}
        ) as breed_list:
            breed_list = await breed_list.json()
        breeds = [x["name"] for x in breed_list]
        breed_count = len(breeds)
        breeds = ", ".join(breeds)
        pages = pagify(breeds, delims=[" "], page_length=2048)
        pages = [x for x in pages]
        return pages, breed_count

    async def cat(self, breed: str = None):
        url = "https://api.thecatapi.com/v1/images/search?has_breeds=1"
        if breed:
            breeds = {}
            async with self.session.get(
                    url="https://api.thecatapi.com/v1/breeds",
                    headers={"x-api-key": os.getenv("CAT")}
            ) as breed_list:
                breed_list = await breed_list.json()
            for x in breed_list:
                breeds[x["name"].lower()] = x["id"]
            if breed.lower() not in breeds:
                return None, None, None
            url += f"&breed_id={breeds[breed.lower()]}"
        async with self.session.get(
                url=url,
                headers={"x-api-key": os.getenv("CAT")}
        ) as resp:
            if resp.status == 200:
                resp = (await resp.json())[0]
                details = ""
                traits = []
                urls = {}
                for x, y in resp["breeds"][0].items():
                    if x not in ["id", "name", "country_codes", "country_code"]:
                        x = x.capitalize().replace("_", " ")
                        if x in ["Cfa url", "Vetstreet url", "Vcahospitals url", "Wikipedia url"]:
                            urls[x.split(" ")[0]] = y.replace("(", "").replace(")", "")
                            continue
                        if x == "Origin":
                            origin = f"**{x}:** {y} ({resp['breeds'][0]['country_code']})\n"
                            continue
                        if x == "Weight":
                            weight = f"**{x}:** {y['imperial']}lb ({y['metric']}kg)\n"
                            continue
                        if x == "Life span":
                            details += f"**{x}:** {y} years\n"
                            continue
                        if x in cat_traits:
                            if y == 1:
                                traits.append(x)
                            continue
                        if x in cat_scale:
                            y = str(y).replace("1", "Bad").replace("2", "Poor").replace("3", "Average") \
                                .replace("4", "Above average").replace("5", "Good")
                            details += f"**{x}:** {y}\n"
                            continue
                        if y:
                            details += f"**{x}:** {y}\n"
                details = origin + details
                details += f"**Traits:** {', '.join(traits)}\n" if traits else ""
                details += weight
                if urls:
                    details += f"**URLs:** {' • '.join([f'[{x}]({y})' for x, y in urls.items()])}"
                return resp["url"], resp["breeds"][0]["name"], details
            return raise_for_status(resp)

    async def cat_breeds(self):
        async with self.session.get(
                url="https://api.thecatapi.com/v1/breeds",
                headers={"x-api-key": os.getenv("CAT")}
        ) as breed_list:
            breed_list = await breed_list.json()
        breeds = [x["name"] for x in breed_list]
        breed_count = len(breeds)
        breeds = ", ".join(breeds)
        pages = pagify(breeds, delims=[" "], page_length=2048)
        pages = [x for x in pages]
        return pages, breed_count

    async def and_here_is_my_code_api(self, endpoint, img: bool = True, facts: bool = False):
        if img:
            async with self.session.get(base_urls["and-here-is-my-code"] + "img/" + endpoint) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    return json
                else:
                    return {"Link": downtime_image}


def raise_for_status(response, reason: str = None, status: str = None):
    reason = reason or response.reason
    status = status or response.status
    http_error_msg = ""

    if isinstance(reason, bytes):
        try:
            reason = reason.decode("utf-8")
        except UnicodeDecodeError:
            reason = reason.decode("iso-8859-1")

    if 400 <= status < 500:
        http_error_msg = f"{status} Client Error: {reason} for url: {response.url}"

    elif 500 <= status < 600:
        http_error_msg = f"{status} Server Error: {reason} for url: {response.url}"

    if http_error_msg:
        raise HTTPError(http_error_msg, response=response)
