"""CI for aoc-reference-data"""

import logging
import sys

from ..domain.data_processor import DataProcessor
from ..commons.errors import (
    LintError,
    print_error_summary_header,
    unpack_error_list,
)
from ..domain.players import PlayerList
from ..domain.teams import TeamList
from ..domain.platforms import PlatformList

# DEBUGGING FLAGS

DEBUG = False
CI = True

LOGGER = logging.getLogger(__name__)


def run_ci():
    #  Setup
    errors = []

    # Importing our data files
    team_list = TeamList.new_with_data_file("data/teams.json")
    player_list = PlayerList.new_with_data_file("data/players.yaml")
    platform_list = PlatformList.new_with_data_file("data/platforms.json")

    LOGGER.debug("Data processing started ...")

    data_processor = DataProcessor(ci=CI)
    data_processor.new_with(player_list, team_list, platform_list, None)

    LOGGER.debug("Linting the data files ...")

    # Indexing and linting of data files
    try:
        err = data_processor.create_global_index()
        if err is not None:
            errors.append(err)
        err = data_processor.lint()
        if err is not None:
            errors.append(err)
    except LintError as Err:
        print(f"An error occured in the linting stage: {Err}")

    # Return errors to user
    err_len = len(errors)

    if err_len > 0:
        LOGGER.error(f"Linting finished with {err_len} error(s).")

        print_error_summary_header()

        for error in errors:
            unpacked_err = unpack_error_list(error)
            while len(unpacked_err) > 0:
                error_message = unpacked_err.pop()
                LOGGER.error(f"{error_message}")
        status = 1
    else:
        LOGGER.info("No errors. Linting finished.")
        status = 0

    LOGGER.info("Exit.")

    sys.exit(status)


if __name__ == "__main__":
    run_ci()
