"""Initialize reference data."""

import argparse
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aocref.bootstrap import bootstrap
from aocref.model import BASE


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument('url', default=os.environ.get('MGZ_DB'), help='database url')
    args = parser.parse_args()

    engine = create_engine(args.url, echo=False)
    session = sessionmaker(bind=engine)()
    BASE.metadata.create_all(engine)
    bootstrap(session)


if __name__ == '__main__':
    main()
