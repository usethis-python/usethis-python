from pathlib import Path

import tomlkit


class PyProjectTOMLNotFoundError(Exception):
    """Raised when a pyproject.toml file is not found."""


def read_pyproject_toml() -> tomlkit.TOMLDocument:
    try:
        return tomlkit.parse((Path.cwd() / "pyproject.toml").read_text())
    except FileNotFoundError:
        raise PyProjectTOMLNotFoundError(
            "'pyproject.toml' not found in the current directory."
        )


def write_pyproject_toml(toml_document: tomlkit.TOMLDocument) -> None:
    (Path.cwd() / "pyproject.toml").write_text(tomlkit.dumps(toml_document))
