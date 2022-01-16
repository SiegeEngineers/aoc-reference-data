from ruamel.yaml import YAML

from .io import Importable, Exportable, JsonSerializable

from .index import Indexable

from .error import InvalidCountryCodeError
# Liquipedia: from .error import MissingKeyError, InvalidCountryCodeError

from collections import namedtuple

from . import INDEX_LIST_SUFFIX

import pycountry

import logging

LOGGER = logging.getLogger(__name__)


class Player(JsonSerializable):

    def __init__(self, name, liquipedia=None, twitch=None, youtube=None,
                 facebook_gaming=None, team=None):

        self.name = name
        self.liquipedia = liquipedia
        self.youtube = youtube
        self.twitch = twitch
        self.facebook_gaming = facebook_gaming
        self.team = team


class PlayerList(Player, Indexable, Importable, Exportable, JsonSerializable):

    errors = []
    id_list = []

    # Tuple description
    # (field, unique, optional, sub-key-settings)
    # field: indexed keys
    # unique: check for duplicates here
    # optional: Don't throw an exeption for these keys if they are missing
    # sub-key-settings: settings for contained sub-keys
    IndexSetting = namedtuple('IndexSetting',
                              'key unique optional sub_key_settings')

    index_key_settings = [
        IndexSetting('id', True, False, None),
        IndexSetting('name', True, False, None),
        IndexSetting('aoeelo', True, True, None),
        IndexSetting('esportsearnings', True, True, None),
        IndexSetting('platforms', True, True, [
            IndexSetting('rl', True, True, None),
            IndexSetting('voobly', True, True, None)
        ]),
        IndexSetting('liquipedia', True, True, None),
        IndexSetting('country', False, True, None)
    ]

    def __init__(self):

        self.players = {}
        self.yaml = YAML()
        self.yaml.register_class(Player)
        self.yaml.preserve_quotes = True

    def add_player_to_list(self, player):
        """ Append a player to the players list

        Args:
            player (Player): Player object
        """

        self.players.append(player)

    def check_country_names_being_valid(self):
        """ Iterates through the list of country names
            parsed from the 'players.yaml' and checks if
            they are valid

        Returns:
            InvalidCountryCodeError: Contains an error with a recommendation
                                     for a possible country code
        """

        errors = []

        LOGGER.debug("Validating country codes ...")
        attribute_name = f"country_{INDEX_LIST_SUFFIX}"

        merged_country_codes = {c.upper() for c in
                                getattr(self,
                                        attribute_name)}

        for country in merged_country_codes:
            if pycountry.countries.get(alpha_2=country) is None:
                suggestion = (pycountry.countries.lookup(country)).alpha_2
                LOGGER.debug(f"Invalid country code detected: '{country}', "
                             f"try '{suggestion}'")
                errors.append(InvalidCountryCodeError(
                    f"Country '{country}'' is invalid, "
                    f"did you mean '{suggestion}'?")
                )

        LOGGER.debug("Country codes validated.")

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("Country codes validated.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Country codes validated with {err_len} error(s).")
            return errors

    ################################################
    #
    # TODO: Refactor with generalisation in indexing
    #
    ##

    # TODO: For liquipedia.py

    # def create_indizes(self):

    #     LOGGER.debug("Indexing player names ...")

    #     self.lookup_names = []
    #     for player in self.players:
    #         self.lookup_names.append(player.name)
    #     LOGGER.debug("Indexing of names complete.")


#     def index_id_list(self, jump_index=None, recursion=False):

#         if not recursion:
#             LOGGER.debug("Creating fresh ID list for players ...")
#         for index, player in enumerate(self.players):
#             if recursion or (jump_index is not None and jump_index <= index):
#                 continue
#             else:
#                 try:
#                     self.id_list.append(player['id'])
#                 except KeyError:
#                     if ci:
#                         raise MissingKeyError(f"Missing ID key "
#                                               f"for {player['name']}")

#                     elif jump_index is index:

#                         continue

#                     else:

#                         print(f"Missing ID key "

#                               f"for {player['name']}")

#                         # Beware! Recursion happening here
#                         # TODO: Refactor to own method?
#                         player['id'] = self.next_free_id(jump_index=index,

#                                                          recursion=True)

#                         LOGGER.info(f"Gave {player['name']} new ID: "

#                                     f"{player['id']}")

#                         LOGGER.info("Continuing as usual ...")

#                         self.id_list.append(player['id'])

#         return self.id_list


# class LiquipediaPlayer(Exportable, Importable, JsonSerializable):

#     def __init__(self, name=None, liquipedia=None, team=None, twitch=None,

#                  youtube=None, facebook_gaming=None):

#         if name is None:
#             pass

#         else:
#             self.name = name

#             self.liquipedia = liquipedia
#             self.team = team

#             self.twitch = twitch

#             self.youtube = youtube

#             self.facebook_gaming = facebook_gaming


# class LiquipediaPlayerList(Importable, Exportable, JsonSerializable):

#     players = []

#     lookup_names = []

#     def __init__(self, _list):
#         self.players = _list

#         self.create_indizes()

#     # TODO: Refactor with generalisation in indexing
#     def contains_name(self, name) -> bool:

#         if name in self.lookup_names:

#             return True

#         else:

#             return False

#     # TODO: Refactor with generalisation in indexing
#     def create_id_list(self):

#         LOGGER.debug("Creating fresh ID list for players ...")

#         for index, player in enumerate(self.players):

#             self.id_list.append(player.id)
#         return self.id_list

#     # TODO: Refactor with generalisation in indexing
#     def create_indizes(self):

#         LOGGER.debug("Indexing Liquipedia player names ...")

#         for player in self.players:

#             self.lookup_names.append(player.name)

#         LOGGER.debug("Indexing of names complete.")
