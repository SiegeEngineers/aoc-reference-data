from typing import List, Any
from collections.abc import Iterable


def flatten(items: List[Any], ignore_types=(str, bytes)) -> Any:
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignore_types):
            yield from flatten(x, ignore_types)
        else:
            yield x
