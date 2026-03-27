"""Error types for the Poetry backend."""

from __future__ import annotations

from usethis.errors import (
    BackendSubprocessFailedError as _BackendSubprocessFailedError,
)
from usethis.errors import (
    DepGroupError,
    UsethisError,
)


class PoetryError(UsethisError):
    """Base class for exceptions relating to Poetry."""


class PoetryDepGroupError(DepGroupError):
    """Raised when adding or removing a dependency from a group fails."""


class PoetrySubprocessFailedError(PoetryError, _BackendSubprocessFailedError):
    """Raised when a subprocess call to Poetry fails."""


class PoetryInitError(PoetrySubprocessFailedError):
    """Raised when the Poetry init command fails to create a pyproject.toml file."""
