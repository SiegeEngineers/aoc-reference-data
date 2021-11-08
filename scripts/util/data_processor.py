import logging


LOGGER = logging.getLogger(__name__)


class DataProcessor(object):

    def __init__(self, ci=False):

        self.ci = ci
        self.errors = []
        self.player_list = []
        self.team_list = []
        self.liquipedia_player_list = []
        self.overwrite_logic = [
            ('liquipedia', False),
            ('twitch', False),
            ('youtube', False),
            ('team', True)
        ]

    def new_from(self, player_list, team_list, liquipedia_player_list):
        """ Create new DataProcessor object from data lists

        Args:
            player_list (PlayerList): A list of players already contained in
            the repository team_list (TeamList): A list of teams already
            contained in the repository result_list (Dictionary):
            The result of LiquipediaRequest
        """

        self.player_list = player_list
        self.team_list = team_list
        self.liquipedia_player_list = liquipedia_player_list

    def preprocess(self):

        # TODO: Clean-up a copy of the player list from
        # items not being able to be updated by Liquipedia

        self.remove_non_liquipedia_from_player_list()

        # TODO: Check for changes to player_list

        # from updates in result_list for early exit

        # TODO: Otherwise create diff from changes

        # and write them to self.player_diff or self.teams_diff

        # alike

    def merge(self):

        # TODO: Merge diff into the players and teams lists

        pass

    def create_global_index(self):
        """ Create indizes for internal handling. """

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
        errors = []

        # Actually checking for duplicates in IDs
        # AND if a team doesn't have an ID key at all
        # raises MissingKeyError in that case
        # Duplicate IDs raise DoubletteFoundError
        for key, unique, optional, sub_key_settings in \
                self.team_list.index_key_settings:
            if unique:
                err = self.team_list.check_for_doublettes(
                    key=key,
                    optional=optional
                )

                if err is not None:
                    errors.append(err)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("No errors. Checking for duplicates in teams "
                         "finished.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Checking for duplicates in teams finished with "
                         f"{err_len} error(s).")
            return errors

    def check_for_doublettes_in_players(self):
        errors = []

        # Actually checking for duplicates in IDs
        # AND if a player doesn't have an ID at all
        # raises MissingKeyError in that case
        # Duplicate IDs raise DoubletteFoundError
        LOGGER.debug("Checking if keys are present and unique ...")
        for key, unique, optional, sub_key_settings in \
                self.player_list.index_key_settings:
            if unique:
                err = self.player_list.check_for_doublettes(
                    key=key,
                    optional=optional,
                    sub_key_settings=sub_key_settings
                )
                if err is not None:
                    errors.append(err)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("No errors. Checking for duplicates in players "
                         "finished.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Checking for duplicates in players finished with "
                         f"{err_len} error(s).")
            return errors

    def index_team_keys(self):
        errors = []

        for key, unique, optional, sub_key_settings in \
                self.team_list.index_key_settings:
            err = self.team_list.index_key(
                attr="teams", key=key,
                sub_key_settings=sub_key_settings,
                optional=optional
            )

            if err is not None:
                errors.append(err)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("No errors. Indexing team keys finished.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Indexing team keys finished with {err_len} "
                         "error(s).")
            return errors

    def index_player_keys(self):
        errors = []

        for key, unique, optional, sub_key_settings in \
                self.player_list.index_key_settings:
            err = self.player_list.index_key(
                attr="players", key=key,
                optional=optional,
                sub_key_settings=sub_key_settings
            )

            if err is not None:
                errors.append(err)

        err_len = len(errors)

        if err_len == 0:
            LOGGER.debug("No errors. Indexing player keys finished.")
            return None
        elif err_len > 0:
            LOGGER.error(f"Indexing player keys finished with {err_len} "
                         "error(s).")
            return errors

    # def remove_non_liquipedia_from_player_list(self):
    #     """ Cleanup of non-mergable/non-updated values """

    #     self.copy_player_list = self.player_list

    #     LOGGER.debug("Searching for values to be deleted ...")

    #     removed_values = 0

    #     for index, player in enumerate(self.copy_player_list):
    #         name = player.get('liquipedia', player['name']).lower()

    #         # Remove players where we can't get information from Liquipedia
    #         if not self.liquipedia_player_list.contains_name(name):
    #             removed_values += 1
    #             self.copy_player_list.pop(index)

    #             continue

    #     LOGGER.info(f"We removed {removed_values} values.")
