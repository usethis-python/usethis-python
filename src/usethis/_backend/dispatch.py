"""Backend selection and dispatch logic."""

from __future__ import annotations

from typing import Literal

from typing_extensions import assert_never

from usethis._backend.poetry.call import call_poetry_subprocess
from usethis._backend.poetry.detect import is_poetry_used
from usethis._backend.uv.available import is_uv_available
from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.detect import is_uv_used
from usethis._config import usethis_config
from usethis._types.backend import BackendEnum


def get_backend() -> Literal[BackendEnum.uv, BackendEnum.poetry, BackendEnum.none]:
    """Get the current package manager backend."""
    # Effectively we cache the inference, storing it in usethis_config.
    if usethis_config.inferred_backend is not None:
        return usethis_config.inferred_backend

    if usethis_config.backend is not BackendEnum.auto:
        usethis_config.inferred_backend = usethis_config.backend
    elif is_poetry_used():
        usethis_config.inferred_backend = BackendEnum.poetry
    elif is_uv_used():
        usethis_config.inferred_backend = BackendEnum.uv
    elif not (usethis_config.cpd() / "pyproject.toml").exists() and is_uv_available():
        # If there's not likely to be a backend in use yet, and uv is available.
        usethis_config.inferred_backend = BackendEnum.uv
    else:
        usethis_config.inferred_backend = BackendEnum.none

    return usethis_config.inferred_backend


def call_backend_subprocess(
    args: list[str],
    *,
    change_toml: bool,
    backend: Literal[BackendEnum.uv, BackendEnum.poetry, BackendEnum.none],
) -> str:
    """Dispatch a subprocess call to the appropriate backend.

    Raises:
        BackendSubprocessFailedError: If the subprocess fails (via the
            backend-specific subclass).
    """
    if backend is BackendEnum.uv:
        return call_uv_subprocess(args, change_toml=change_toml)
    elif backend is BackendEnum.poetry:
        return call_poetry_subprocess(args, change_toml=change_toml)
    elif backend is BackendEnum.none:
        msg = "Cannot call a backend subprocess when no backend is active."
        raise ValueError(msg)
    else:
        assert_never(backend)
