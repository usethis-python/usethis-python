from __future__ import annotations

from typing import Literal

from usethis._config import usethis_config
from usethis._console import warn_print
from usethis._integrations.backend.poetry.used import is_poetry_used
from usethis._integrations.backend.uv.available import is_uv_available
from usethis._integrations.backend.uv.used import is_uv_used
from usethis._types.backend import BackendEnum


def get_backend() -> Literal[BackendEnum.uv, BackendEnum.none]:
    # Effectively we cache the inference, storing it in usethis_config.
    if usethis_config.inferred_backend is not None:
        return usethis_config.inferred_backend

    if usethis_config.backend is not BackendEnum.auto:
        usethis_config.inferred_backend = usethis_config.backend
    elif is_poetry_used():
        warn_print(
            "This project is using Poetry, which is not fully supported by usethis."
        )
        usethis_config.inferred_backend = BackendEnum.none
    elif is_uv_used():
        usethis_config.inferred_backend = BackendEnum.uv
    elif not (usethis_config.cpd() / "pyproject.toml").exists() and is_uv_available():
        # If there's not likely to be a backend in use yet, and uv is available.
        usethis_config.inferred_backend = BackendEnum.uv
    else:
        usethis_config.inferred_backend = BackendEnum.none

    return usethis_config.inferred_backend
