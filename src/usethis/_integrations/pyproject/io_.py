import tomllib
from pathlib import Path
from typing import Any

import tomlkit

from usethis._integrations.pyproject.errors import (
    PyProjectTOMLDecodeError,
    PyProjectTOMLNotFoundError,
)


def read_pyproject_toml() -> tomlkit.TOMLDocument:
    try:
        return tomlkit.parse((Path.cwd() / "pyproject.toml").read_text())
    except FileNotFoundError:
        msg = "'pyproject.toml' not found in the current directory."
        raise PyProjectTOMLNotFoundError(msg)


def read_pyproject_dict() -> dict[str, Any]:
    try:
        with Path("pyproject.toml").open("rb") as f:
            try:
                return tomllib.load(f)
            except tomllib.TOMLDecodeError as err:
                msg = f"Error decoding 'pyproject.toml': {err}"
                raise PyProjectTOMLDecodeError(msg)

    except FileNotFoundError:
        msg = "'pyproject.toml' not found in the current directory."
        raise PyProjectTOMLNotFoundError(msg)


def write_pyproject_toml(toml_document: tomlkit.TOMLDocument) -> None:
    (Path.cwd() / "pyproject.toml").write_text(tomlkit.dumps(toml_document))
