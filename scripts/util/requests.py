import json
import requests
import logging
import time
from .io import Importable, Exportable, JsonSerializable
from .players import LiquipediaPlayer

LOGGER = logging.getLogger(__name__)


class LiquipediaRequest(Importable, Exportable, JsonSerializable):

    properties = [
        'Has id',
        'Has team',
        'Has twitch stream',
        'Has youtube channel'
    ]

    url = 'https://liquipedia.net/ageofempires/api.php'
    user_agent = 'https://github.com/SiegeEngineers/aoc-reference-data'

    def __init__(self, debug=None, cache=None, game="aoe2"):

        self.wait_secs = 30
        self.page_size = 200
        self.export_data = []

        if debug is True:
            self.debug = True
        else:
            self.debug = False

        if cache is True:
            self.cache = True
        else:
            self.cache = False

        if game == "aoe2":
            self.conditions = [
                'Category:Age of Empires II Players',
                'Is player::true'
            ]

    def fetch(self):
        """ Fetch data from liquipedia API.
        """

        self.output = []
        offset = 0

        while True:

            LOGGER.debug(f"querying liquipedia at offset {offset}")

            resp = requests.get(self.url, params={
                'action': 'askargs',
                'format': 'json',
                'conditions': '|'.join(self.conditions),
                'printouts': '|'.join(self.properties),
                'parameters': '|'.join([f'offset={offset}',
                                        f'limit={self.page_size}'])
            }, headers={
                'User-Agent': self.user_agent
            })

            if self.debug:
                LOGGER.debug(f"Request url: {resp.request.url}")

            try:
                data = resp.json()
            except json.decoder.JSONDecodeError:
                LOGGER.exception("failed to fetch: %s", resp.content)
            for result in data['query']['results'].values():
                record = result['printouts']
                team = record['Has team'][0]['fulltext'] \
                    if record['Has team'] else None
                name = record['Has id'][0]
                twitch = record['Has twitch stream'][0] \
                    if record['Has twitch stream'] else None
                youtube = record['Has youtube channel'][0] \
                    if record['Has youtube channel'] else None

                # TODO: Query for Facebook Gaming as well
                facebook_gaming = None

                self.output.append(
                    LiquipediaPlayer(
                        name=name.lower(),
                        liquipedia=name,
                        team=team,
                        twitch=twitch,
                        youtube=youtube,
                        facebook_gaming=facebook_gaming
                    )
                )

            offset = data.get('query-continue-offset')

            if not offset:
                break

            time.sleep(self.wait_secs)

        if self.cache:
            self.export_data = self.output
