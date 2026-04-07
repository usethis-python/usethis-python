"""Project source directory layout detection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._config import usethis_config

if TYPE_CHECKING:
    from typing import Literal


def get_source_dir_str() -> Literal["src", "."]:
    """Get the source directory as a string ('src' or '.')."""
    src_dir = usethis_config.cpd() / "src"

    if src_dir.exists() and src_dir.is_dir():
        return "src"
    return "."


def get_tests_dir_str() -> str:
    """Get the tests directory name ('tests' or 'test').

    Uses heuristics to detect the name of the tests directory. If a 'tests' directory
    exists, returns 'tests'. If a 'test' directory exists, returns 'test'. Otherwise,
    defaults to 'tests' (the most common convention).
    """
    cpd = usethis_config.cpd()

    # Check for 'tests' directory first (most common)
    if (cpd / "tests").is_dir():
        return "tests"

    # Check for 'test' directory (alternative naming convention)
    if (cpd / "test").is_dir():
        return "test"

    # Default to 'tests' if neither exists
    return "tests"
