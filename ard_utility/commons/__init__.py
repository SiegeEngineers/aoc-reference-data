from collections import defaultdict

INDEX_LIST_SUFFIX = "list"
GAMES = ["aoe1", "aoe2", "aoe3", "aoe4"]
LIQUIPEDIA_CACHE_FILE = "cache/liquipedia.json"


def handle_mixed_fields(input, field):
    if field in input and isinstance(input[field], list):
        if isinstance(input[field], list) and len(input[field]) == 1:
            return list(input[field])
        else:
            return set([item for item in input[field]])
    elif field in input and isinstance(input[field], int):
        return input[field]
    else:
        return None


def initialise_defaultdict_recursive():
    return defaultdict(initialise_defaultdict_recursive)
