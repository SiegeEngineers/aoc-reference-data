"""
ard_utility -- A command-line tool to manage and check aoc-reference-data content

Usage:
  ard_utility ci [--verbose]
  ard_utility lp_update [--verbose]
  ard_utility convert [--verbose]
  ard_utility (-h | --help)
  ard_utility --version

Arguments:
  -v, --version     Show version
  -h --help         Show this screen

Options:
  --verbose         Increase verbosity
"""


import sys
import logging

from docopt import docopt  # type: ignore

from .__version__ import __version__

from .functionality.ci import run_ci
from .functionality.convert import run_convert
from .functionality.liquipedia import run_liquipedia_update


def main(argv=None):
    """entry point for the command line interface"""

    args = docopt(
        __doc__, argv=argv, version=__package__ + " v" + __version__, help=True
    )

    if args["--verbose"]:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args["ci"]:
        run_ci()
    if args["convert"]:
        run_convert()
    if args["lp_update"]:
        run_liquipedia_update()

    sys.exit(0)
