"""Query Liquipedia API for data updates."""

from util.requests import LiquipediaRequest

import os

import sys

import logging

from util.players import PlayerList, LiquipediaPlayerList, LiquipediaPlayer

from util.teams import Team, TeamList

from util.data_processor import DataProcessor

from util.error import ProcessingError, PreparationError, LintError, \
    unpack_error_list, print_error_summary_header

# DEBUGGING FLAGS
DEBUG = True
SAVE_CACHE = True
CI = True

LOGGER = logging.getLogger(__name__)


if __name__ == '__main__':

    #  Setup
    errors = []

    # Set Debug logging if necessary
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    elif not DEBUG:
        logging.basicConfig(level=logging.INFO)

    # Parsing data from repository
    # Do this first so we have easy access to the unique ids
    # of each player

    # TODO: Parsing into PlayerList type

    player_list = PlayerList()
    player_list.import_from_file(file_name="data/players", file_type="yaml")
    player_list.players = player_list.import_data

    imported_team_list = Team()
    imported_team_list.import_from_file(
        file_name="data/teams", file_type="json"
        )
    team_list = TeamList(imported_team_list.import_data)

    # Check for cache hit
    if os.path.exists('cache/liquipedia.json'):
        CACHE_HIT = True
    else:
        CACHE_HIT = False

    LOGGER.debug("Starting data update")

    if not CACHE_HIT:
        # Fetching data from Liquipedia
        liquipedia_data = LiquipediaRequest(
                DEBUG,
                SAVE_CACHE,
                game="aoe2"
            )
        liquipedia_data.fetch()

        unprocessed_liquipedia_data = LiquipediaPlayerList(
            liquipedia_data.output
            )

        # Add our own player list ids to Liquipedia players for
        # easier handling of Liquipedia data in the future
        unprocessed_liquipedia_data.map_ids_from(player_list.players)

        # Save cache file
        if SAVE_CACHE:
            liquipedia_data.export_to_file(
                    file_name="cache/liquipedia",
                    file_type="json"
                )
    else:
        # DEBUGGING/DEVELOPMENT: Use cache for Liquipedia response
        LOGGER.debug("CACHE HIT! We use our cached Liquipedia results!")

        liquipedia_data = LiquipediaPlayer()

        liquipedia_data.import_from_file(
            file_name="cache/liquipedia",
            file_type="json"
            )

        unprocessed_liquipedia_data = LiquipediaPlayerList(
            liquipedia_data.import_data)

    # Data processing
    LOGGER.debug("Data processing started ...")

    data_processor = DataProcessor(ci=CI)
    data_processor.new_from(player_list,
                            team_list, unprocessed_liquipedia_data)

    LOGGER.debug("Linting the data files ...")

    # Linting of data files

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
