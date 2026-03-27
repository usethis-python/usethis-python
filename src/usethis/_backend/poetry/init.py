"""Project initialization via Poetry."""

from __future__ import annotations

from usethis._backend.poetry.call import call_poetry_subprocess
from usethis._backend.poetry.errors import PoetryInitError, PoetrySubprocessFailedError
from usethis._config import usethis_config
from usethis._file.pyproject_toml.errors import PyprojectTOMLInitError


def ensure_pyproject_toml_via_poetry(*, author: bool = True) -> None:
    """Create a pyproject.toml file using `poetry init`.

    It is assumed that the pyproject.toml file doesn't already exist.
    """
    args = [
        "init",
        "--name",
        usethis_config.cpd().name,
    ]
    if not author:
        args.append("--author=none")

    try:
        call_poetry_subprocess(args, change_toml=True)
    except PoetrySubprocessFailedError as err:
        msg = f"Failed to create a pyproject.toml file:\n{err}"
        raise PyprojectTOMLInitError(msg) from None


def opinionated_poetry_init() -> None:
    """Subprocess `poetry init` with opinionated arguments.

    It is assumed that the pyproject.toml file doesn't already exist.
    """
    try:
        call_poetry_subprocess(
            [
                "init",
                "--name",
                usethis_config.cpd().name,
            ],
            change_toml=True,
        )
    except PoetrySubprocessFailedError as err:
        msg = f"Failed to create a pyproject.toml file and initialize project:\n{err}"
        raise PoetryInitError(msg) from None
