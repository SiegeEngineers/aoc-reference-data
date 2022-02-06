"""Query Liquipedia API for data updates."""

import logging
import os
import sys

from ..commons import LIQUIPEDIA_CACHE_FILE
from ..commons.errors import (
    LintError,
    PreparationError,
    ProcessingError,
    print_error_summary_header,
    unpack_error_list,
)
from ..domain.data_processor import DataProcessor
from ..domain.platforms import PlatformList
from ..domain.players import PlayerList
from ..domain.request_handler import LiquipediaRequest
from ..domain.teams import TeamList

# DEBUGGING FLAGS
DEBUG = True
USE_CACHE = True
SAVE_CACHE = True
CI = True


def run_liquipedia_update():

    LOGGER = logging.getLogger(__name__)

    #  Setup
    errors = []

    # Parsing data from repository
    # Do this first so we have easy access to the unique ids
    # of each player

    # Importing our data files
    platform_list = PlatformList.new_with_data_file("data/platforms.json")
    team_list = TeamList.new_with_data_file("data/teams.json")
    player_list = PlayerList.new_with_data_file("data/players.yaml")

    # Check for cache hit
    if USE_CACHE and os.path.exists(LIQUIPEDIA_CACHE_FILE):
        CACHE_HIT = True
    else:
        CACHE_HIT = False

    LOGGER.debug("Starting data update")

    lp_player_list = None

    if not CACHE_HIT:
        # Fetch player data for all games
        liquipedia_req = LiquipediaRequest(DEBUG, SAVE_CACHE)
        liquipedia_req.fetch()

        # Save cache file
        if SAVE_CACHE:
            os.makedirs(os.path.dirname(LIQUIPEDIA_CACHE_FILE), exist_ok=True)
            file_path, ext = os.path.splitext(LIQUIPEDIA_CACHE_FILE)
            liquipedia_req.export_to_file(file_name=file_path, file_type=ext)

        lp_player_list = PlayerList.new_from_liquipedia_result(
            liquipedia_req.players
        )

    else:
        # DEBUGGING/DEVELOPMENT: Use cache for Liquipedia response
        LOGGER.debug("CACHE HIT! We use our cached Liquipedia results!")

        lp_player_list = PlayerList.new_from_liquipedia_cache(
            LIQUIPEDIA_CACHE_FILE
        )

    # Data processing
    LOGGER.debug("Data processing started ...")

    data_processor = DataProcessor(ci=CI)
    data_processor.new_with(
        player_list, team_list, platform_list, lp_player_list
    )

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

    # Preparation for merge e.g. cleanup of unneeded data

    try:
        err = data_processor.preprocess()
        if err is not None:
            errors.append(err)
    except PreparationError as Err:
        print(f"An error occured in the preparation stage: {Err}")

    # Merge data

    try:
        err = data_processor.merge()
        if err is not None:
            errors.append(err)
    except ProcessingError as Err:
        print(f"An error occured in the processing stage: {Err}")

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
    run_liquipedia_update()
