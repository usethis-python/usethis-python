"""Project initialization via Poetry."""

from __future__ import annotations

import sys

from usethis._backend.poetry.call import call_poetry_subprocess
from usethis._backend.poetry.errors import PoetryInitError, PoetrySubprocessFailedError
from usethis._file.dir import get_project_name_from_dir
from usethis._file.pyproject_toml.errors import PyprojectTOMLInitError


def _get_poetry_python_constraint() -> str:
    """Get a bounded Python version constraint for Poetry projects.

    Poetry's dependency resolver requires an upper-bounded `requires-python`
    to avoid conflicts with packages that declare `python_requires < 4.0`.
    """
    minor = sys.version_info.minor
    return f">=3.{minor},<4.0"


def ensure_pyproject_toml_via_poetry(*, author: bool = True) -> None:
    """Create a pyproject.toml file using `poetry init`.

    Poetry does not support controlling author inclusion via CLI flags,
    so the `author` parameter is accepted for API compatibility but ignored.

    It is assumed that the pyproject.toml file doesn't already exist.
    """
    _ = author
    args = [
        "init",
        "--name",
        get_project_name_from_dir(),
        "--python",
        _get_poetry_python_constraint(),
    ]

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
                get_project_name_from_dir(),
                "--python",
                _get_poetry_python_constraint(),
            ],
            change_toml=True,
        )
    except PoetrySubprocessFailedError as err:
        msg = f"Failed to create a pyproject.toml file and initialize project:\n{err}"
        raise PoetryInitError(msg) from None
