from __future__ import annotations

from typing import Literal

from usethis._config import usethis_config
from usethis._console import warn_print
from usethis._integrations.backend.poetry.used import is_poetry_used
from usethis._integrations.backend.uv.available import is_uv_available
from usethis._integrations.backend.uv.used import is_uv_used
from usethis._types.backend import BackendEnum


def get_backend() -> Literal[BackendEnum.uv, BackendEnum.none]:
    if usethis_config.backend is not BackendEnum.auto:
        return usethis_config.backend

    if is_poetry_used():
        warn_print(
            "This project is using Poetry, which is not fully supported by usethis."
        )
        return BackendEnum.none

    if is_uv_used() or is_uv_available():
        return BackendEnum.uv

    return BackendEnum.none
