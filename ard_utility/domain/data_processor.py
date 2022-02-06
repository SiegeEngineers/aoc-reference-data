import logging
from .platforms import PlatformList
from .players import PlayerList
from .teams import TeamList
from ..commons.errors import unpack_error_list

LOGGER = logging.getLogger(__name__)


class DataProcessor(object):

    player_list: PlayerList
    platform_list: PlatformList
    team_list: TeamList
    lp_player_list: PlayerList

    def __init__(self, ci=False):

        self.ci = ci
        self.errors = []
        self.player_list = []
        self.platform_list = []
        self.team_list = []
        self.lp_player_list = []
        self.overwrite_logic = [
            ("liquipedia", False),
            ("twitch", False),
            ("youtube", False),
            ("team", True),
        ]

    def new_with(self, player_list, team_list, platform_list, lp_player_list):
        """Create new DataProcessor object from data lists

        Args:
            player_list (PlayerList):       A list of players already contained
                                            in the repository
            team_list (TeamList):           A list of teams already
                                            contained in the repository
            platform_list (PlatformList):   A list of platforms already
                                            contained in the repository
            lp_player_list (PlayerList):    A list of teams already
                                            contained in the repository
        """

        self.player_list = player_list
        self.team_list = team_list
        self.platform_list = platform_list
        self.lp_player_list = lp_player_list

    def preprocess(self):

        # TODO:
        #

        pass

    def handle_player_team_relations(self, player_list, team_list):
        pass

    def map_team_ids_to_lp_players(self, team_list) -> int:
        if self.input_source == "cache" or self.input_source == "response":
            # We are a Liquipedia Player
            for idx, player in enumerate(self.players):
                if (
                    player.team is not None
                    and player.team.lower() in team_list.team_name_lookup
                ):
                    player.team = team_list.team_name_lookup[
                        player.team.lower()
                    ]["team_id"]
                    return -1
                elif player.team is None:
                    pass
                else:
                    return idx

    def map_player_ids_to_lp_players(self, player_list):
        if self.input_source == "cache" or self.input_source == "response":
            # We are a Liquipedia Player
            for player in self.players:
                if player.liquipedia.lower() in player_list.lp_lookup:
                    player.id = player_list.lp_lookup[
                        player.liquipedia.lower()
                    ]["player_id"]

    def merge(self):

        # TODO: Merge diff into the players and teams lists
        pass

    def create_global_index(self):
        """Create indizes for internal handling."""

        LOGGER.debug("Indexing ...")
        errors = []
        err = self.index_team_keys()
        if err is not None:
            errors.append(err)

        err = self.index_player_keys()
        if err is not None:
            errors.append(err)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("Indexing finished.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Indexing finished with {err_len} error(s).")
            return errors

    def lint(self):
        errors = []

        LOGGER.debug("Linting teams ...")
        err = self.check_for_doublettes_in_teams()
        if err is not None:
            errors.append(err)
        LOGGER.debug("Linting teams done.")

        LOGGER.debug("Linting players ...")
        err = self.check_for_doublettes_in_players()
        if err is not None:
            errors.append(err)
        err = self.player_list.check_country_names_being_valid()
        if err is not None:
            errors.append(err)
        LOGGER.debug("Linting players done.")

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("Linting finished.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Linting finished with {err_len} error(s).")
            return errors

    def check_for_doublettes_in_teams(self):

        LOGGER.debug("Checking if keys are present and unique ...")
        errors = self.team_list.check_for_doublettes()

        # Flatten the errors in between to show
        # more precise error count
        errors = unpack_error_list(errors)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug(
                "No errors. Checking for duplicates in teams " "finished."
            )
            return None
        elif err_len > 0:
            LOGGER.error(
                f"Checking for duplicates in teams finished with "
                f"{err_len} error(s)."
            )
            return errors

    def check_for_doublettes_in_players(self):

        LOGGER.debug("Checking if keys are present and unique ...")

        errors = self.player_list.check_for_doublettes()

        # Flatten the errors in between to show
        # more precise error count
        errors = unpack_error_list(errors)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug(
                "No errors. Checking for duplicates in players " "finished."
            )
            return None
        elif err_len > 0:
            LOGGER.error(
                f"Checking for duplicates in players finished with "
                f"{err_len} error(s)."
            )
            return errors

    def index_team_keys(self):
        errors = []

        for (
            key,
            unique,
            optional,
            sub_key_settings,
        ) in self.team_list.index_key_settings:
            err = self.team_list.index_key(
                attr="teams",
                key=key,
                sub_key_settings=sub_key_settings,
                optional=optional,
            )

            if err is not None:
                errors.append(err)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("No errors. Indexing team keys finished.")
            return None
        elif err_len > 0:
            LOGGER.error(
                f"Indexing team keys finished with {err_len} " "error(s)."
            )
            return errors

    def index_player_keys(self):
        errors = []

        for (
            key,
            unique,
            optional,
            sub_key_settings,
        ) in self.player_list.index_key_settings:
            err = self.player_list.index_key(
                attr="players",
                key=key,
                optional=optional,
                sub_key_settings=sub_key_settings,
            )

            if err is not None:
                errors.append(err)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("No errors. Indexing player keys finished.")
            return None
        elif err_len > 0:
            LOGGER.error(
                f"Indexing player keys finished with {err_len} " "error(s)."
            )
            return errors
