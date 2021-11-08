"""Query Liquipedia API for data updates."""

import os
import logging


from util.players import PlayerList, LiquipediaPlayerList, LiquipediaPlayer

from util.teams import Team, TeamList

from util.data_processor import DataProcessor

from util.error import ProcessingError, PreparationError, LintError

from util.requests import LiquipediaRequest


# DEBUGGING FLAGS

DEBUG = True

CACHE = True


LOGGER = logging.getLogger(__name__)


if __name__ == '__main__':

    #  Setup

    logging.basicConfig(level=logging.INFO)

    # Check for cache hit

    if os.path.exists('cache/liquipedia.json'):

        CACHE_HIT = True

    else:

        CACHE_HIT = False

    # Fetching data from Liquipedia

    LOGGER.info("Starting data update")

    if not CACHE_HIT:

        liquipedia_data = LiquipediaRequest(DEBUG, CACHE, game="aoe2")

        liquipedia_data.fetch()

        if CACHE:

            liquipedia_data.export_to_file(

                file_name="cache/liquipedia", file_type="json")

    else:

        # DEBUGGING/DEVELOPMENT: Use cache for Liquipedia response

        LOGGER.info("CACHE HIT! We use our cached Liquipedia results!")

        liquipedia_data = LiquipediaPlayer()

        liquipedia_data.import_from_file(

            file_name="cache/liquipedia", file_type="json")

    # Handle Caching

    if CACHE_HIT:

        unprocessed_liquipedia_data = LiquipediaPlayerList(

            liquipedia_data.import_data)

    else:

        unprocessed_liquipedia_data = LiquipediaPlayerList(

            liquipedia_data.output)

    # Parsing data from repository

    # TODO: Parsing into PlayerList type

    player_list = PlayerList()

    player_list.import_from_file(file_name="data/players", file_type="yaml")

    player_list.players = player_list.import_data

    imported_team_list = Team()

    imported_team_list.import_from_file(

        file_name="data/teams", file_type="json")

    team_list = TeamList(imported_team_list.import_data)

    # Data processing

    LOGGER.info("Data processing started ...")

    data_processor = DataProcessor()

    data_processor.new_from(player_list,

                            team_list, unprocessed_liquipedia_data)

    LOGGER.info("Linting the data files ...")

    # Linting of data files

    try:
        data_processor.lint()

    except LintError as Err:

        print(f"An error occured in the linting stage: {Err}")

    # Preparation for merge e.g. cleanup of unneeded data

    try:
        data_processor.preprocess()

    except PreparationError as Err:

        print(f"An error occured in the preparation stage: {Err}")

    # Merge data

    try:

        data_processor.merge()

    except ProcessingError as Err:

        print(f"An error occured in the processing stage: {Err}")

    LOGGER.info("Data processing finished.")

    LOGGER.info("Exit.")
