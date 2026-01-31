# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pydantic",
#     "vdf",
# ]
# ///

import csv
import platform
from pathlib import Path
from typing import Annotated, Literal

import vdf

from pydantic import BaseModel, ConfigDict, Field


class DEMap(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    data_name: str
    const_name: str | None = None
    name_string_id: int
    rollover_string_id: str | int
    icon_reference: str
    map_icon_filename: str
    mappool_icon_filename: str | None = None
    script_filename: str
    scenario_filename: str | None = None
    storage_id: int
    style: str
    land: bool = False
    open: bool = False
    random_map: bool = False
    death_match: bool = False
    regicide: bool = False
    king_of_the_hill: bool = False
    capture_the_relic: bool = False
    sudden_death: bool = False
    wonder_race: bool = False
    empire_wars: bool = False
    mixed: bool = False
    defend_the_wonder: bool = False
    nomad: bool = False
    closed: bool = False
    water: bool = False
    migration: bool = False
    battle_royale: bool = False
    prohibited_game_mode: str | None = None


class DEMaps(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    default_map_type: int
    default_nomad_map_type: int
    default_battle_royale_map_type: int
    map_list: list[DEMap]


class DECivBuilding(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    age_id: Annotated[int, Field(alias="Age ID")]
    building_id: Annotated[int, Field(alias="Building ID")]
    building_new_column: Annotated[bool, Field(alias="Building in new column")]
    building_upgraded_from_id: Annotated[int, Field(alias="Building upgraded from ID")]
    draw_node_type: Annotated[str, Field(alias="Draw Node Type")]
    help_string_id: Annotated[int, Field(alias="Help String ID")]
    link_id: Annotated[int, Field(alias="Link ID")]
    link_node_type: Annotated[str, Field(alias="Link Node Type")]
    name: Annotated[str, Field(alias="Name")]
    name_string_id: Annotated[int, Field(alias="Name String ID")]
    node_id: Annotated[int, Field(alias="Node ID")]
    node_status: Annotated[str, Field(alias="Node Status")]
    node_type: Annotated[str, Field(alias="Node Type")]
    picture_index: Annotated[int, Field(alias="Picture Index")]
    prerequisite_ids: Annotated[list[int], Field(alias="Prerequisite IDs")]
    prerequisite_types: Annotated[list[str], Field(alias="Prerequisite Types")]
    trigger_tech_id: Annotated[int, Field(alias="Trigger Tech ID")]
    use_type: Annotated[str, Field(alias="Use Type")]


class DECivUnit(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    age_id: Annotated[int, Field(alias="Age ID")]
    building_id: Annotated[int, Field(alias="Building ID")]
    building_new_column: Annotated[bool, Field(alias="Building in new column")] = False
    building_upgraded_from_id: Annotated[
        int, Field(alias="Building upgraded from ID")
    ] = -1
    draw_node_type: Annotated[str, Field(alias="Draw Node Type")]
    help_string_id: Annotated[int, Field(alias="Help String ID")]
    link_id: Annotated[int, Field(alias="Link ID")]
    link_node_type: Annotated[str, Field(alias="Link Node Type")]
    name: Annotated[str, Field(alias="Name")]
    name_string_id: Annotated[int, Field(alias="Name String ID")]
    node_id: Annotated[int, Field(alias="Node ID")]
    node_status: Annotated[str, Field(alias="Node Status")]
    node_type: Annotated[str, Field(alias="Node Type")]
    picture_index: Annotated[int, Field(alias="Picture Index")]
    prerequisite_ids: Annotated[list[int], Field(alias="Prerequisite IDs")]
    prerequisite_types: Annotated[list[str], Field(alias="Prerequisite Types")]
    trigger_tech_id: Annotated[int, Field(alias="Trigger Tech ID")]
    use_type: Annotated[str, Field(alias="Use Type")]


class DECivTechTree(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    civ_id: str
    civ_techs_buildings: list[DECivBuilding]
    civ_techs_units: list[DECivUnit]


class DECivTechTrees(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    civs: list[DECivTechTree]


class UnitStringIds(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    name: int
    description: int


class DECivilization(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    internal_name: str
    tech_tree_name: str
    data_name: str
    hud_style: str
    tech_tree_image_path: Path | None = None
    emblem_image_path: Path | None = None
    unique_unit_image_paths: Annotated[list[Path], Field(default_factory=list[Path])]
    name_string_id: int
    computer_name_string_table_offset: int = -1
    unique_tech_id_1: int = -1
    unique_tech_id_2: int = -1
    unique_unit_line: int = -1
    unique_unit_upgrade_id: int = -1
    unique_unit_id: int = -1
    elite_unique_unit_id: int = -1
    unique_unit_string_ids: Annotated[
        list[UnitStringIds], Field(default_factory=list[UnitStringIds])
    ]
    era: Literal["base"] | Literal["antiquity"]


class DECivilizations(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    civilization_list: list[DECivilization]


class AoCDatasetMeta(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    version: str
    name: str


class AoCDataset(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    dataset: AoCDatasetMeta
    civilizations: dict[str, dict[str, str | int]]  # TODO
    maps: dict[str, str]
    technologies: dict[str, str]
    terrain: dict[str, dict[str, str | dict[str, str]]]  # TODO
    objects: dict[str, str]

    def with_maps(self, maps: DEMaps, key_values: dict[str, str]):
        new_maps = {
            **{
                str(map.storage_id): key_values.get(
                    str(map.name_string_id),
                    map.const_name if map.const_name is not None else map.data_name,
                )
                for map in maps.map_list
            },
            **{
                str(map.name_string_id): key_values.get(
                    str(map.name_string_id),
                    map.const_name if map.const_name is not None else map.data_name,
                )
                for map in maps.map_list
            },
        }
        new_dataset = self.model_copy(
            update={
                "maps": {
                    str(map_name): new_maps[str(map_name)]
                    for map_name in sorted([int(k) for k in new_maps.keys()])
                }
            }
        )
        return new_dataset

    def with_civ_techs(self, civs: list[DECivTechTree], key_values: dict[str, str]):
        new_techs = {
            **self.technologies,
            **{
                str(unit.trigger_tech_id): key_values.get(
                    str(unit.name_string_id), unit.name
                ).replace("E.", "Elite")
                for civ in civs
                for unit in civ.civ_techs_units
                if unit.trigger_tech_id != -1
            },
            **{
                str(unit.node_id): key_values.get(
                    str(unit.name_string_id), unit.name
                ).replace("E.", "Elite")
                for civ in civs
                for unit in civ.civ_techs_units
                if unit.node_type == "Research"
            },
        }
        new_dataset = self.model_copy(
            update={
                "technologies": {
                    str(tech_name): new_techs[str(tech_name)]
                    for tech_name in sorted([int(k) for k in new_techs.keys()])
                }
            }
        )
        return new_dataset


def get_steam_path() -> Path:
    if platform.system() == "Windows":
        return get_steam_path_windows()
    else:
        return get_steam_path_linux()


def get_steam_path_windows() -> Path:
    import winreg

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Valve\\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        steam_path = Path(steam_path)
        winreg.CloseKey(key)
    except FileNotFoundError:
        raise FileNotFoundError("ERROR: Steam is not installed.")

    if not steam_path.exists():
        raise FileNotFoundError(
            "ERROR: The Steam path does not exist or is not accessible."
        )

    return steam_path


def get_steam_path_linux() -> Path:
    return Path("~/.local/share/Steam/").expanduser()


def get_app_path(steam_path: Path, app_id: str) -> Path:
    vdf_file_path = steam_path / "steamapps" / "libraryfolders.vdf"

    with vdf_file_path.open("r") as file:
        data = file.read()
    parsed = vdf.loads(data)

    libraryfolders = parsed.get("libraryfolders", {})
    app_path = None

    for folder in libraryfolders.values():
        if isinstance(folder, dict) and "apps" in folder and app_id in folder["apps"]:
            app_path = folder.get("path")
            if app_path is None:
                continue
            app_path = Path(app_path)
            if app_path.exists():
                break

    if app_path is None:
        raise FileNotFoundError(
            f"ERROR: Could not find the installation path for app {app_id}."
        )

    return app_path


def get_game_path(steam_path: Path, app_id: str, game_name: str) -> Path:
    app_path = get_app_path(steam_path, app_id)
    game_path = app_path / "steamapps" / "common" / game_name

    if not game_path.exists():
        raise FileNotFoundError(
            f"ERROR: The game path does not exist. Check if the game name '{game_name}' is correct and the game is properly installed."
        )

    return game_path


def read_english_strings(resources_dir: Path) -> dict[str, str]:
    strings_file = (
        resources_dir / "en" / "strings" / "key-value" / "key-value-strings-utf8.txt"
    )
    key_values = {}
    with strings_file.open("rt", newline="\r\n") as file:
        for line in file:
            line = line.replace("\\n", " ")
            if line.lstrip().startswith("//") or line.strip() == "":
                continue
            if "//" in line:
                line = line[: line.find("//")]
            delimiter = None
            for char in line:
                if not char.isspace():
                    continue
                delimiter = char
                break
            if delimiter is None:
                print(line)
                raise Exception("Could not find a delimiter")
            reader = csv.reader([line], escapechar="\\", delimiter=delimiter)
            for row in reader:
                if len(row) > 2:
                    row = [p for p in row if not (p.isspace() or p == "")]
                if len(row) > 2:
                    row = [row[0], " ".join(row[1:])]
                if len(row) == 1:
                    row = [*row, ""]
                if len(row) != 2:
                    print(row)
                    continue
                key, value = row

                if key in key_values and value != key_values[key]:
                    non_unique = [
                        "13170",
                        "13171",
                        "200040",
                        "IDS_EVENT_CHALLENGE_TRAIN_ANY_UNIT_HELP_TEXT",
                        "120201",
                        "120202",
                        "120198",
                        "120199",
                        "120200",
                        "5323",
                        "6897",
                        "8084",
                        "28084",
                    ]
                    if key in non_unique:
                        continue
                    raise Exception(
                        f"Key {key} is not unique: {value=} - {key_values[key]=}"
                    )
                key_values[key] = value.strip().replace('"', "").replace("\n", " ")

    return key_values


def read_civ_tech_tree(resources_dir: Path):
    civ_json = resources_dir / "_common" / "dat" / "civTechTrees.json"
    return DECivTechTrees.model_validate_json(civ_json.read_text(encoding="utf8"))


def read_civilizations(resources_dir: Path):
    civ_json = resources_dir / "_common" / "dat" / "civilizations.json"
    return DECivilizations.model_validate_json(civ_json.read_text(encoding="utf8"))


def read_maps(resources_dir: Path):
    maps_json = resources_dir / "_common" / "dat" / "maps.json"
    return DEMaps.model_validate_json(maps_json.read_text(encoding="utf8"))


def load_dataset():
    dataset_file = Path("../data/datasets/100.json")
    return AoCDataset.model_validate_json(dataset_file.read_text(encoding="utf8"))


def main() -> None:
    dataset = load_dataset()
    game_dir = get_game_path(get_steam_path(), "813780", "AoE2DE")
    resources_dir = game_dir / "resources"
    key_values = read_english_strings(resources_dir)
    maps = read_maps(resources_dir)
    civs = read_civilizations(resources_dir)
    tech_tree = read_civ_tech_tree(resources_dir)

    aoe2_civs = {
        civ.tech_tree_name for civ in civs.civilization_list if civ.era == "base"
    }
    filtered_civs = [civ for civ in tech_tree.civs if civ.civ_id in aoe2_civs]
    new_dataset = dataset.with_maps(maps, key_values).with_civ_techs(
        filtered_civs, key_values
    )

    print(new_dataset.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
