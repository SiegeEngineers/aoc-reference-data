from ruamel.yaml import YAML
from .io import Importable, Exportable, JsonSerializable
from .index import Indexable
# from .error import MissingKeyError
from collections import namedtuple

import logging
LOGGER = logging.getLogger(__name__)


class Team(Exportable, Importable, JsonSerializable):
    def __init__(self, name=None, abbreviation=None, players=None, id=None):
        if name is None:
            pass
        else:
            self.name = name
            self.abbreviation = abbreviation
            self.players = players
            self.id = id


class TeamList(Indexable, Importable, Exportable, JsonSerializable):

    errors = []
    teams = []
    id_list = []

    # Tuple description
    # (field, unique, optional, sub-key-settings)
    # field: indexed keys
    # unique: don't check for duplicates here
    # optional: Don't throw an exeption for these keys if they are missing
    # sub-key-settings: settings for contained sub-keys
    IndexSetting = namedtuple('IndexSetting',
                              'key unique optional sub_key_settings'
                              )
    index_key_settings = [
        IndexSetting('id', True, False, None),
        IndexSetting('name', True, False, None),
    ]

    def __init__(self, _list=list):
        self.teams = _list
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

    # def get_id_from_team_name(self, name):
    #     lookup_team_name = {t['name']: t['id'] for t in self.teams}

    #     try:
    #         return lookup_team_name[name]
    #     except KeyError:
    #         return -1

    # def index_id_list(self):
    #     LOGGER.info("Creating fresh ID list for teams ...")
    #     for index, team in enumerate(self.teams):
    #         try:
    #             self.id_list.append(team.id)
    #         except KeyError:
    #             raise MissingKeyError(f"Missing ID key "
    #                                   f"for '{team.name}'")

    #     return self.id_list

    # def create_and_append_new_team_to_teams_list(self, name=None,
    #                                              abbreviation=None,
    #                                              players=None, id=None):
    #     if id is None:
    #         self.next_free_id()

    #     self.teams.append(Team(name, abbreviation, players, id))
