"""CI for aoc-reference-data"""

import logging

import sys

from util.players import PlayerList

from util.teams import Team, TeamList

from util.data_processor import DataProcessor

from util.error import LintError


# DEBUGGING FLAGS

DEBUG = True
CI = True

LOGGER = logging.getLogger(__name__)


if __name__ == '__main__':

    #  Setup
    errors = []
    logging.basicConfig(level=logging.INFO)

    # Parsing data from repository

    # TODO: Parsing into PlayerList type

    player_list = PlayerList()

    player_list.import_from_file(file_name="data/players", file_type="yaml")

    player_list.players = player_list.import_data

    imported_team_list = Team()

    imported_team_list.import_from_file(

        file_name="data/teams", file_type="json")

    team_list = TeamList(imported_team_list.import_data)

    # Linting of data files

    LOGGER.debug("Data processing started ...")

    data_processor = DataProcessor()

    data_processor.new_from(player_list,

                            team_list, None)

    LOGGER.debug("Linting the data files ...")

    try:
        err = data_processor.create_global_index(ci=CI)
        if err is not None:
            errors.append(err)
        err = data_processor.lint(ci=CI)
        if err is not None:
            errors.append(err)
    except LintError as Err:
        print(f"An error occured in the linting stage: {Err}")

    # Return errors to user
    err_len = len(errors)

    if err_len > 0:
        LOGGER.error(f"Linting finished with {err_len} error(s).")
        for error in errors:
            LOGGER.error(f"{error}")
        status = 1
    else:
        LOGGER.info("No errors. Linting finished.")
        status = 0

    LOGGER.info("Exit.")

    sys.exit(status)
