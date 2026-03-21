from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any, TypeVar

T = TypeVar("T", bound=MutableMapping[Any, Any])


def _deep_merge(target: T, source: MutableMapping[Any, Any]) -> T:
    """Recursively merge source into target in place, returning target.

    For keys present in both mappings, if both values are mappings the merge is
    applied recursively; otherwise the source value replaces the target value.
    """
    for key, value in source.items():
        if (
            key in target
            and isinstance(target[key], MutableMapping)
            and isinstance(value, MutableMapping)
        ):
            _deep_merge(target[key], value)
        else:
            target[key] = value
    return target
