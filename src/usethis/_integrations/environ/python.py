"""Python version environment queries."""

from __future__ import annotations

import functools

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.python import (
    get_supported_uv_minor_python_versions,
)
from usethis._config import usethis_config
from usethis._console import warn_print
from usethis._file.pyproject_toml.errors import PyprojectTOMLNotFoundError
from usethis._file.pyproject_toml.requires_python import (
    MissingRequiresPythonError,
    get_required_minor_python_versions,
    get_requires_python,
)
from usethis._python.version import PythonVersion, PythonVersionParseError
from usethis._types.backend import BackendEnum


def get_supported_minor_python_versions() -> list[PythonVersion]:
    """Get supported Python versions for the current backend.

    For the uv backend, queries available Python versions from uv. Otherwise, without a
    backend, uses 'requires-python' from 'pyproject.toml' if available, otherwise falls
    back to the .python-version file if present, or the current interpreter.

    Returns:
        Supported Python versions within the requires-python bounds, sorted from lowest
        to highest.
    """
    backend = get_backend()

    if backend is BackendEnum.uv:
        versions = get_supported_uv_minor_python_versions()
    elif backend in (BackendEnum.poetry, BackendEnum.none):
        # When the backend doesn't manage python versions, we can't query for them via subprocess.
        # Instead, we use requires-python if available.
        try:
            versions = get_required_minor_python_versions()
        except (MissingRequiresPythonError, PyprojectTOMLNotFoundError):
            # No requires-python specified, use .python-version file or interpreter
            return [_get_current_python_version()]

        # If no versions match, fall back to .python-version file or interpreter
        if not versions:
            return [_get_current_python_version()]

        # Check if current version is within bounds and warn if not
        try:
            requires_python = get_requires_python()
            current_version = _get_current_python_version()
            if not requires_python.contains(current_version.to_short_string()):
                warn_print(
                    f"Current Python version ({current_version.to_short_string()}) "
                    f"is outside requires-python bounds ({requires_python}). "
                    f"Using lowest supported version ({versions[0].to_short_string()})."
                )
        except (MissingRequiresPythonError, PyprojectTOMLNotFoundError):
            # The warning check is best-effort; silently skip it if the project
            # configuration is unavailable at this point.
            pass
    else:
        assert_never(backend)

    return versions


@functools.cache
def _get_current_python_version() -> PythonVersion:
    """Get the inferred Python version for the current project.

    Prefers the version from the .python-version file if it exists and is valid,
    otherwise falls back to the current interpreter.
    """
    python_version_file = usethis_config.cpd() / ".python-version"
    try:
        return PythonVersion.from_python_version_file(python_version_file)
    except (FileNotFoundError, PythonVersionParseError):
        return PythonVersion.from_interpreter()
