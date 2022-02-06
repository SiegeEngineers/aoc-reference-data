import logging

LOGGER = logging.getLogger(__name__)


class PreparationError(Exception):
    """Base class for errors in the preparation stage"""

    pass


class ProcessingError(Exception):
    """Base class for errors in the processing stage"""

    pass


class IndexingError(Exception):
    """Base class for errors in the indexing stage"""

    pass


class LintError(Exception):
    """Base class for errors in the linting stage"""

    pass


class InvalidCountryCodeError(LintError):
    """
    Raised when a country with an invalid ISO 3166-alpha2code was detected
    """


class DoubletteFoundError(PreparationError):
    """Raised when a doublette was found"""

    pass


class MissingKeyError(PreparationError):
    """Raised when a key is missing e.g. no ID key"""

    pass


class GenericIndexingError(IndexingError):
    """Generic Error thrown when it's still unsure what happened"""

    pass


def unpack_error_list(err_list):
    if len(err_list) == 0:
        return err_list
    if isinstance(err_list[0], list):
        return unpack_error_list(err_list[0]) + unpack_error_list(err_list[1:])
    return err_list[:1] + unpack_error_list(err_list[1:])


def raise_error(error_message: str = "We experienced an error!"):
    raise SystemExit(error_message)


def print_error_summary_header():
    LOGGER.fatal(
        """
############################################################
###################### ERROR SUMMARY #######################
############################################################
"""
    )
