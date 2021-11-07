class PreparationError(Exception):
    """ Base class for errors in the preparation stage """
    pass


class ProcessingError(Exception):
    """ Base class for errors in the processing stage """
    pass


class LintError(Exception):
    """  Base class for errors in the linting stage """
    pass


class InvalidCountryCodeError(LintError):
    """ Raised when a country with an invalid ISO 3166-alpha2 code was detected """


class DoubletteFoundError(PreparationError):
    """ Raised when a doublette was found """
    pass


class MissingKeyError(PreparationError):
    """ Raised when a key is missing e.g. no ID key """
    pass
