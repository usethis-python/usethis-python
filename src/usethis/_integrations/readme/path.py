from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._config import usethis_config
from usethis._console import warn_print
from usethis.errors import UsethisError

if TYPE_CHECKING:
    from pathlib import Path


class NonMarkdownREADMEError(UsethisError):
    """Raised when the README file is not Markdown based on its extension."""


def get_readme_path():
    path_readme_md = usethis_config.cpd() / "README.md"
    path_readme = usethis_config.cpd() / "README"

    if path_readme_md.exists() and path_readme_md.is_file():
        return path_readme_md
    elif path_readme.exists() and path_readme.is_file():
        return path_readme

    for path in usethis_config.cpd().glob("README*"):
        if path.is_file() and path.stem == "README":
            return path

    msg = "No README file found."
    raise FileNotFoundError(msg)


def get_markdown_readme_path() -> Path:
    path = get_readme_path()

    if path.name == "README.md":
        pass
    elif path.name == "README":
        warn_print("Assuming 'README' file is Markdown.")
    else:
        msg = f"README file '{path.name}' is not Markdown based on its extension."
        raise NonMarkdownREADMEError(msg)

    return path
