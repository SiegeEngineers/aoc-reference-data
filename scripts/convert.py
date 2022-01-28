import json
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

with open("data/players.yaml", encoding="utf8", mode="r") as handle:
    convert = yaml.load(handle)

with open("data/auto_generated/players.json", "w") as handle:
    # Could also be
    # json.dump(convert, handle, indent=4)
    # but that doubles the file size
    # since readability is achieved by using yaml
    # we go for the smaller file size
    json.dump(convert, handle)
