from functools import cache
from pathlib import Path

from tomlkit.api import dumps, parse
from tomlkit.exceptions import TOMLKitError
from tomlkit.toml_document import TOMLDocument

from usethis._integrations.pyproject.errors import (
    PyProjectTOMLDecodeError,
    PyProjectTOMLNotFoundError,
)


def read_pyproject_toml() -> TOMLDocument:
    return read_pyproject_toml_from_path(Path.cwd() / "pyproject.toml")


@cache
def read_pyproject_toml_from_path(path: Path) -> TOMLDocument:
    try:
        return parse(path.read_text())
    except FileNotFoundError:
        msg = "'pyproject.toml' not found in the current directory."
        raise PyProjectTOMLNotFoundError(msg)
    except TOMLKitError as err:
        msg = f"Failed to decode 'pyproject.toml': {err}"
        raise PyProjectTOMLDecodeError(msg) from None


def write_pyproject_toml(toml_document: TOMLDocument) -> None:
    read_pyproject_toml_from_path.cache_clear()
    (Path.cwd() / "pyproject.toml").write_text(dumps(toml_document))
