import logging
import os
from collections import namedtuple
from dataclasses import dataclass

import pycountry
from ruamel.yaml import YAML

from ..commons import (
    INDEX_LIST_SUFFIX,
    handle_mixed_fields,
    initialise_defaultdict_recursive,
)
from ..commons.errors import InvalidCountryCodeError
from ..utils.io import Exportable, Importable, JsonSerializable
from .index_handler import Indexable
from .platforms import PlayerPlatform, PlayerPlatformList


LOGGER = logging.getLogger(__name__)


@dataclass
class Player(JsonSerializable):

    id: int
    name: str
    aka: str
    country: object
    platforms: object
    notability: dict
    liquipedia: str
    team: list[int]
    aoeelo: int
    esportsearnings: int
    twitch: list[str]
    youtube: list[str]
    facebook_gaming: list[str]

    def update_from(self, update_player):
        # NOTE: Do other fields need to be implemented?
        # Should be the same data as it's basically one profile
        # on Liquipedia only with different games
        if self.notability != update_player.notability:
            key, value = update_player.notability.popitem()
            self.notability[key] = value


class PlayerList(Indexable, Importable, Exportable, JsonSerializable):

    # Tuple description
    # (field, unique, optional, sub-key-settings)
    # field: indexed keys
    # unique: check for duplicates here
    # optional: Don't throw an exeption for these keys if they are missing
    # sub-key-settings: settings for contained sub-keys
    IndexSetting = namedtuple(
        "IndexSetting", "key unique optional sub_key_settings"
    )

    index_key_settings = [
        IndexSetting("id", True, False, None),
        IndexSetting("name", True, False, None),
        IndexSetting("aoeelo", True, True, None),
        IndexSetting("esportsearnings", True, True, None),
        IndexSetting(
            "platforms",
            True,
            True,
            [
                IndexSetting("rl", True, True, None),
                IndexSetting("voobly", True, True, None),
                IndexSetting("vooblycn", True, True, None),
            ],
        ),
        IndexSetting("liquipedia", True, True, None),
        IndexSetting("country", False, True, None),
    ]

    def __init__(self, input_source):
        self.players = []
        self.input_source = input_source
        self.errors = []

        self.yaml = YAML()
        self.yaml.register_class(Player)
        self.yaml.preserve_quotes = True

    def get_new_unique_id(self, offset=1):
        ids = [player.id for player in self.players]
        return max(ids) + offset

    def initialise_list(self):
        if self.input_source == "file":
            for player in self.import_data:
                self.players.append(
                    Player(
                        player["id"],
                        player["name"],
                        player["aka"] if "aka" in player else None,
                        player["country"] if "country" in player else None,
                        PlayerPlatformList(
                            [
                                PlayerPlatform(
                                    platform, player["platforms"][platform]
                                )
                                for platform in player["platforms"].keys()
                            ]
                        )
                        if "platforms" in player
                        else None,
                        player["notability"],
                        player["liquipedia"]
                        if "liquipedia" in player
                        else None,
                        handle_mixed_fields(player, "team"),
                        player["aoeelo"] if "aoeelo" in player else None,
                        player["esportsearnings"]
                        if "esportsearnings" in player
                        else None,
                        [url for url in player["twitch"]]
                        if "twitch" in player
                        else None,
                        [url for url in player["youtube"]]
                        if "youtube" in player
                        else None,
                        [url for url in player["facebook_gaming"]]
                        if "facebook_gaming" in player
                        else None,
                    )
                )
        else:
            imported_players = initialise_defaultdict_recursive()

            for game, players in self.import_data.items():
                for player in players:

                    import_player = None

                    # Either parse player dict if from file/cache
                    # or directly use the player from the liquipedia
                    # response
                    if self.input_source == "cache":
                        import_player = Player(
                            player["id"],
                            player["name"],
                            player["aka"],
                            player["country"],
                            player["platforms"],
                            player["notability"],
                            player["liquipedia"],
                            player["team"],
                            player["aoeelo"],
                            player["esportsearnings"],
                            player["twitch"],
                            player["youtube"],
                            player["facebook_gaming"],
                        )
                    elif self.input_source == "response":
                        import_player = player

                    # The player is first being added to the list
                    if import_player.liquipedia not in imported_players:
                        imported_players[
                            import_player.liquipedia
                        ] = import_player
                    else:
                        if (
                            imported_players[import_player.liquipedia]
                            != import_player
                        ):
                            old_player = imported_players[
                                import_player.liquipedia
                            ]
                            old_player.update_from(import_player)
                            imported_players[
                                old_player.liquipedia
                            ] = old_player
                        else:
                            pass

            self.players = [player for player in imported_players.values()]

    def new_with_data_file(path="data/players.yaml"):
        p = PlayerList(input_source="file")
        file_path, ext = os.path.splitext(path)
        p.import_from_file(file_path, ext)
        p.initialise_list()
        del p.import_data
        return p

    def new_from_liquipedia_cache(path="cache/liquipedia.json"):
        p = PlayerList(input_source="cache")
        file_path, ext = os.path.splitext(path)
        p.import_from_file(file_path, ext)
        p.initialise_list()
        del p.import_data
        return p

    def new_from_liquipedia_result(result):
        p = PlayerList(input_source="response")
        p.import_data = result
        p.initialise_list()
        del p.import_data
        return p

    def create_lp_lookup(self):
        if self.input_source == "file":
            for idx, player in enumerate(self.players):
                name = (
                    player.liquipedia.lower()
                    if player.liquipedia is not None
                    else player.name.lower()
                )
                self.lp_lookup[name] = {"index": idx, "player_id": player.id}
        else:
            raise NotImplementedError

    def create_id_lookup(self):
        """To later access the player_list fast by index"""
        if self.input_source == "file":
            for idx, player in enumerate(self.players):
                if player.id not in self.id_lookup:
                    self.id_lookup[player.id] = idx
                else:
                    raise KeyError(
                        f"Double player id: {player.id} in our players.yaml"
                    )
        elif self.input_source == "cache" or self.input_source == "response":
            for idx, player in enumerate(self.players):
                if player.id not in self.id_lookup:
                    if player.id is not None:
                        self.id_lookup[player.id] = idx
                    else:
                        self.id_lookup[player.liquipedia.lower()] = idx
                else:
                    raise KeyError(
                        f"Double player id: {player.id} in Liquipedia Cache."
                    )
        else:
            raise NotImplementedError

    def create_indizes(self):
        self.create_id_lookup()
        self.create_lp_lookup()

    def add_player_to_list(self, player):
        """Append a player to the players list

        Args:
            player (Player): Player object
        """

        self.players.append(player)

    def check_country_names_being_valid(self):
        """Iterates through the list of country names
            parsed from the 'players.yaml' and checks if
            they are valid

        Returns:
            InvalidCountryCodeError: Contains an error with a recommendation
                                     for a possible country code
        """

        errors = []

        LOGGER.debug("Validating country codes ...")
        attribute_name = f"country_{INDEX_LIST_SUFFIX}"

        merged_country_codes = {
            c.upper() for _, _, c in getattr(self, attribute_name)
        }

        for country in merged_country_codes:
            if pycountry.countries.get(alpha_2=country) is None:
                suggestion = (pycountry.countries.lookup(country)).alpha_2
                LOGGER.debug(
                    f"Invalid country code detected: '{country}', "
                    f"try '{suggestion}'"
                )
                errors.append(
                    InvalidCountryCodeError(
                        f"Country '{country}'' is invalid, "
                        f"did you mean '{suggestion}'?"
                    )
                )

        LOGGER.debug("Country codes validated.")

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("Country codes validated.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Country codes validated with {err_len} error(s).")
            return errors
