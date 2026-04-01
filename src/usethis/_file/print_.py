"""Pretty-printing helpers for configuration file keys."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from typing_extensions import assert_never

if TYPE_CHECKING:
    from collections.abc import Sequence

    from usethis._file.types_ import Key


def print_keys(keys: Sequence[Key]) -> str:
    r"""Convert a list of keys to a string.

    Args:
        keys: A list of keys.

    Returns:
        A string representation of the keys.

    Examples:
        >>> print_keys(["tool", "ruff", "line-length"])
        'tool.ruff.line-length'
        >>> print_keys([re.compile(r"importlinter:contracts:.*")])
        '<REGEX("importlinter:contracts:.*")>'
    """
    components: list[str] = []
    for key in keys:
        if isinstance(key, str):
            components.append(key)
        elif isinstance(key, re.Pattern):
            components.append(f'<REGEX("{key.pattern}")>')
        else:
            assert_never(key)

    return ".".join(components)
