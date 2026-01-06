from __future__ import annotations

from typing_extensions import assert_never

from usethis._console import warn_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.backend.uv.python import (
    get_supported_uv_minor_python_versions,
)
from usethis._integrations.file.pyproject_toml.errors import PyprojectTOMLNotFoundError
from usethis._integrations.file.pyproject_toml.requires_python import (
    MissingRequiresPythonError,
    get_required_minor_python_versions,
    get_requires_python,
)
from usethis._integrations.python.version import PythonVersion
from usethis._types.backend import BackendEnum


def get_supported_minor_python_versions() -> list[PythonVersion]:
    """Get supported Python versions for the current backend.

    For the uv backend, queries available Python versions from uv. Otherwise, without a
    backend, uses 'requires-python' from 'pyproject.toml' if available, otherwise falls
    back to current interpreter.

    Returns:
        Supported Python versions within the requires-python bounds, sorted from lowest
        to highest.
    """
    backend = get_backend()

    if backend is BackendEnum.uv:
        versions = get_supported_uv_minor_python_versions()
    elif backend is BackendEnum.none:
        # When no build backend is available, we can't query for available Python versions.
        # Instead, we use requires-python if available.
        try:
            versions = get_required_minor_python_versions()
        except (MissingRequiresPythonError, PyprojectTOMLNotFoundError):
            # No requires-python specified, use current interpreter
            return [PythonVersion.from_interpreter()]

        # If no versions match, fall back to current interpreter
        if not versions:
            return [PythonVersion.from_interpreter()]

        # Check if current interpreter is within bounds and warn if not
        try:
            requires_python = get_requires_python()
            current_version = PythonVersion.from_interpreter()
            if not requires_python.contains(current_version.to_short_string()):
                warn_print(
                    f"Current Python interpreter ({current_version.to_short_string()}) "
                    f"is outside requires-python bounds ({requires_python}). "
                    f"Using lowest supported version ({versions[0].to_short_string()})."
                )
        except (MissingRequiresPythonError, PyprojectTOMLNotFoundError):
            pass
    else:
        assert_never(backend)

    return versions
