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
