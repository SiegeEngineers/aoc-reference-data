from ruamel.yaml import YAML
from .io import Importable, Exportable
from .index import Indexable
import logging
LOGGER = logging.getLogger(__name__)


class Platform(Indexable):
    def __init__(self, id=None, name=None, url=None, match_url=None):
        self.id = id
        self.name = name
        self.url = url
        self.match_url = match_url


class PlatformList(Platform, Importable, Exportable):
    def __init__(self, teams):
        self.platforms = {}
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
