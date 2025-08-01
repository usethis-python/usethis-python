from __future__ import annotations

from usethis._config import usethis_config
from usethis._integrations.backend.uv import (  # Use this style to allow test mocking
    call,
)
from usethis._integrations.backend.uv.errors import UVInitError, UVSubprocessFailedError
from usethis._integrations.file.pyproject_toml.errors import PyprojectTOMLInitError


def opinionated_uv_init() -> None:
    """Subprocess `uv init` with opinionated arguments.

    It is assumed that the pyproject.toml file doesn't already exist.
    """
    try:
        call.call_uv_subprocess(
            [
                "init",
                "--lib",
                "--build-backend",
                "hatch",
                usethis_config.cpd().as_posix(),
            ],
            change_toml=True,
        )
    except UVSubprocessFailedError as err:
        msg = f"Failed to create a pyproject.toml file and initialize project:\n{err}"
        raise UVInitError(msg) from None


def ensure_pyproject_toml_via_uv(*, author: bool = True) -> None:
    """Create a pyproject.toml file using `uv init --bare`.

    It is assumed that the pyproject.toml file doesn't already exist.
    """
    author_from = "auto" if author else "none"

    try:
        call.call_uv_subprocess(
            [
                "init",
                "--bare",
                "--vcs=none",
                f"--author-from={author_from}",
                "--build-backend",  # https://github.com/usethis-python/usethis-python/issues/347
                "hatch",  # until https://github.com/astral-sh/uv/issues/3957
                usethis_config.cpd().as_posix(),
            ],
            change_toml=True,
        )
    except UVSubprocessFailedError as err:
        msg = f"Failed to create a pyproject.toml file:\n{err}"
        raise PyprojectTOMLInitError(msg) from None
