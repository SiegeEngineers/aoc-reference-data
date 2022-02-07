import logging
import os

# from .error import MissingKeyError
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum

from ..commons import handle_mixed_fields
from ..utils.io import Exportable, Importable, JsonSerializable
from .index_handler import Indexable

LOGGER = logging.getLogger(__name__)


class TeamReturnValues(Enum):
    PLAYER_EXISTS_IN_TEAM = 1
    PLAYER_DOESNT_EXIST_IN_TEAM = 2
    TEAM_DOESNT_EXIST = 3
    TEAM_EXISTS = 4


@dataclass
class Team(Exportable, Importable, JsonSerializable):

    id: int
    name: str
    abbreviation: str
    players: list[int]


class TeamList(Indexable, Importable, Exportable, JsonSerializable):

    # Tuple description
    # (field, unique, optional, sub-key-settings)
    # field: indexed keys
    # unique: don't check for duplicates here
    # optional: Don't throw an exeption for these keys if they are missing
    # sub-key-settings: settings for contained sub-keys
    IndexSetting = namedtuple(
        "IndexSetting", "key unique optional sub_key_settings"
    )
    index_key_settings = [
        IndexSetting("id", True, False, None),
        IndexSetting("name", True, False, None),
        IndexSetting("players", False, False, None),
    ]

    def __init__(self) -> None:
        self.errors = []
        self.teams = []

    def get_new_unique_id(self, offset=1):
        ids = [team.id for team in self.teams]
        return max(ids) + offset

    def initialise_list(self) -> None:
        for team in self.import_data:
            self.teams.append(
                Team(
                    team["id"],
                    team["name"],
                    team["abbreviation"],
                    handle_mixed_fields(team, "players"),
                )
            )

    def new_with_data_file(path="data/teams.json") -> TeamList:
        t = TeamList()
        file_path, ext = os.path.splitext(path)
        t.import_from_file(file_path, ext)
        t.initialise_list()
        del t.import_data
        return t

    def create_team_id_lookup(self):
        for idx, team in enumerate(self.teams):
            self.team_id_lookup[team.id] = idx

    def create_team_name_lookup(self):
        for idx, team in enumerate(self.teams):
            self.team_name_lookup[team.name.lower()] = {
                "index": idx,
                "team_id": team.id,
            }

    def create_team_member_lookup(self):
        for idx, team in enumerate(self.teams):
            for player in team.players:
                if player not in self.member_lookup:
                    self.member_lookup[player] = {
                        "index": idx,
                        "team_id": team.id,
                    }
                else:
                    LOGGER.fatal("Players in two teams are not implemented.")
                    raise NotImplementedError()

    def team_exists(self, team_id) -> TeamReturnValues:
        if team_id in self.team_id_lookup:
            return TeamReturnValues.TEAM_EXISTS
        else:
            return TeamReturnValues.TEAM_DOESNT_EXIST

    def check_for_player_in_team(
        self, player_id_cmp, team_id_cmp
    ) -> TeamReturnValues:
        if player_id_cmp not in self.member_lookup:
            # TODO: Handle this case gracefully
            # We don't have this player id connected to any team
            # meaning we should probably believe the LP result
            # and connect it
            # Reasons can be:
            # A player joined a team
            # There is a new team, we haven't saved
            ret = self.team_exists(team_id_cmp)
            if ret == TeamReturnValues.PLAYER_DOESNT_EXIST_IN_TEAM:
                pass
            elif ret == TeamReturnValues.TE:
                pass
        elif self.member_lookup[player_id_cmp]["team_id"] != team_id_cmp:
            # TODO: Handle this case gracefully
            # We have connected this player to a team, but
            # the team ID doesn't correspond the the actual
            # team we got from the LP result
            # Reasons can be:
            # A player joined a different team, our data is
            # outdated
            # There is a new team, we haven't saved
            raise NotImplementedError
        elif self.member_lookup[player_id_cmp]["team_id"] == team_id_cmp:
            return True

    def create_indizes(self):
        self.create_team_member_lookup()
        self.create_team_id_lookup()
        self.create_team_name_lookup()

    def get_next_free_team_id(self) -> int:
        return self.team_id_lookup.max() + 1

    def create_new_team(self, name, initial_members=[]):
        team = Team(self.get_next_free_team_id(), name, None, initial_members)
        self.teams.append(team)

        # RERUN INDEXING
        self.create_indizes()

    def add_new_members_to_existing_team(self, team_id, new_members=[]):
        if team_id is not None and len(new_members) > 0:
            team_index = self.team_id_lookup[team_id]
            self.teams[team_index].players.append(
                member for member in new_members
            )
        elif team_id is None:
            raise NotImplementedError(
                f"This team_id {team_id} is not existing."
            )
        elif len(new_members) == 0:
            print(f"There are no new members to add to team {team_id}.")

        # RERUN INDEXING
        self.create_indizes()
