import json
import logging
import time
from collections import namedtuple

import requests

from ..utils.io import Exportable, Importable, JsonSerializable
from .players import Player

LOGGER = logging.getLogger(__name__)

LiquipediaRequestSettings = namedtuple(
    "LiquipediaRequestSettings", "game conditions"
)


class LiquipediaRequest(Importable, Exportable, JsonSerializable):

    properties = [
        "Has id",
        "Has team",
        "Has twitch stream",
        "Has youtube channel",
    ]

    players = {}

    liquipedia_request_settings = [
        LiquipediaRequestSettings(
            "aoe1",
            [
                "Category:Age of Empires I Players",
                "Is player::true",
            ],
        ),
        LiquipediaRequestSettings(
            "aoe2",
            [
                "Category:Age of Empires II Players",
                "Is player::true",
            ],
        ),
        LiquipediaRequestSettings(
            "aoe3",
            [
                "Category:Age of Empires III Players",
                "Is player::true",
            ],
        ),
        LiquipediaRequestSettings(
            "aoe4",
            [
                "Category:Age of Empires IV Players",
                "Is player::true",
            ],
        ),
    ]

    url = "https://liquipedia.net/ageofempires/api.php"
    user_agent = "https://github.com/SiegeEngineers/aoc-reference-data"

    def __init__(self, debug=None, save_cache=None):

        self.wait_secs = 30
        self.page_size = 200
        self.export_data = []

        if debug is True:
            self.debug = True
        else:
            self.debug = False

        if save_cache is True:
            self.save_cache = True
        else:
            self.save_cache = False

    def fetch(self):
        """Fetch data from liquipedia API."""

        for game, conditions in self.liquipedia_request_settings:

            self.players[game] = []
            offset = 0

            while True:
                LOGGER.debug(f"querying liquipedia at offset {offset}")

                resp = requests.get(
                    self.url,
                    params={
                        "action": "askargs",
                        "format": "json",
                        "formatversion": "2",
                        "api_version": "3",
                        "conditions": "|".join(conditions),
                        "printouts": "|".join(self.properties),
                        "parameters": "|".join(
                            [f"offset={offset}", f"limit={self.page_size}"]
                        ),
                    },
                    headers={"User-Agent": self.user_agent},
                )

                if self.debug:
                    LOGGER.debug(f"Request url: {resp.request.url}")

                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except json.decoder.JSONDecodeError:
                        LOGGER.exception(f"failed to fetch: {resp.content}")

                    # data["query"]["results"] is a list containing dicts
                    for result in data["query"]["results"]:

                        # result is a dictionary with the new API
                        # { <name>: <printout> }
                        _, item = result.popitem()
                        record = item["printouts"]

                        team = (
                            record["Has team"][0]["fulltext"]
                            if record["Has team"]
                            else None
                        )
                        name = record["Has id"][0]
                        twitch = (
                            record["Has twitch stream"][0]
                            if record["Has twitch stream"]
                            else None
                        )
                        youtube = (
                            record["Has youtube channel"][0]
                            if record["Has youtube channel"]
                            else None
                        )

                        # TODO: Query for Facebook Gaming as well
                        # Liquipedia doesn't have a field for it though
                        # afaics
                        facebook_gaming = None

                        self.players[game].append(
                            Player(
                                id=None,
                                name=name.lower(),
                                aka=None,
                                country=None,
                                platforms=None,
                                notability={game: True},
                                liquipedia=name,
                                team=team,
                                aoeelo=None,
                                esportsearnings=None,
                                twitch=twitch,
                                youtube=youtube,
                                facebook_gaming=facebook_gaming,
                            )
                        )

                    offset = data.get("query-continue-offset")

                    if not offset:
                        break

                    time.sleep(self.wait_secs)

                else:
                    LOGGER.exception(f"failed to fetch: {resp.content}")

        if self.save_cache:
            self.export_data = self.players
