import logging
import os
from dataclasses import dataclass

from .index_handler import Indexable
from ..utils.io import Exportable, Importable
from ruamel.yaml.comments import CommentedSeq
from typing import Optional

LOGGER = logging.getLogger(__name__)


@dataclass
class Platform(Indexable):

    id: str
    name: str
    url: str
    match_url: str
    parameters: dict


@dataclass
class PlayerPlatform(object):
    id: str
    platform_ids: list[str]


@dataclass
class PlayerPlatformList(object):
    platforms: list[PlayerPlatform]

    def get_platform_ids_for_platform(
        self, platform_name: str
    ) -> Optional[CommentedSeq]:
        for platform in self.platforms:
            if platform.id == platform_name:
                if isinstance(platform.platform_ids, list):
                    return platform.platform_ids
                else:
                    return list(platform.platform_ids)


@dataclass
class PlatformList(Importable, Exportable):

    id: str
    platforms: list[Platform]

    def new_with_data_file(path="data/platforms.json") -> PlatformList:
        p = PlatformList(None, [])
        file_path, ext = os.path.splitext(path)
        p.import_from_file(file_path, ext)
        p.initialise_list()
        del p.import_data
        return p

    def initialise_list(self) -> None:
        for platform in self.import_data:
            self.platforms.append(
                Platform(
                    platform["id"],
                    platform["name"],
                    platform["url"],
                    platform["match_url"],
                    platform["parameters"]
                    if "parameters" in platform
                    else None,
                )
            )
