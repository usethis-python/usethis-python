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
