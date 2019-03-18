"""AoC Reference Data."""

import os
import pkg_resources


PACKAGE_NAME = 'aocref'
DATA_PATH = 'data'


def get_metadata(filename):
    """Get metadata file path."""
    return pkg_resources.resource_filename(PACKAGE_NAME, os.path.join(DATA_PATH, filename))


def list_metadata(path):
    """List metadata at path."""
    return pkg_resources.resource_listdir(PACKAGE_NAME, os.path.join(DATA_PATH, path))


def get_class_by_tablename(base, tablename):
    """Return class reference mapped to table.

    https://stackoverflow.com/a/23754464
    """
    for c in base._decl_class_registry.values():
        if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
            return c
