from __future__ import annotations

from typing_extensions import assert_never

from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.backend.uv.python import (
    get_supported_uv_minor_python_versions,
)
from usethis._integrations.python.version import PythonVersion
from usethis._types.backend import BackendEnum


def get_supported_minor_python_versions() -> list[PythonVersion]:
    backend = get_backend()

    if backend is BackendEnum.uv:
        versions = get_supported_uv_minor_python_versions()
    elif backend is BackendEnum.none:
        versions = [PythonVersion.from_interpreter()]
    else:
        assert_never(backend)

    return versions
