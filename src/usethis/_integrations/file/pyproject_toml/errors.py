from __future__ import annotations

from usethis._integrations.file.toml.errors import (
    TOMLDecodeError,
    TOMLError,
    TOMLNotFoundError,
    TOMLValueAlreadySetError,
    TOMLValueMissingError,
    UnexpectedTOMLIOError,
    UnexpectedTOMLOpenError,
)
from usethis.errors import FileConfigError


class PyprojectTOMLError(TOMLError):
    """Raised when aspects of 'pyproject.toml' are missing, invalid, or unexpected."""


class PyprojectTOMLNotFoundError(PyprojectTOMLError, TOMLNotFoundError):
    """Raised when a pyproject.toml file is not found."""


class PyprojectTOMLInitError(PyprojectTOMLError):
    """Raised when a pyproject.toml file cannot be created."""


class PyprojectTOMLDecodeError(TOMLDecodeError, PyprojectTOMLError):
    """Raised when a pyproject.toml file cannot be decoded."""

    @property
    def name(self) -> str:
        """The name of the file that could not be decoded."""
        return "pyproject.toml"


class UnexpectedPyprojectTOMLOpenError(PyprojectTOMLError, UnexpectedTOMLOpenError):
    """Raised when the pyproject.toml file is unexpectedly opened."""


class UnexpectedPyprojectTOMLIOError(PyprojectTOMLError, UnexpectedTOMLIOError):
    """Raised when an unexpected attempt is made to read or write the pyproject.toml file."""


class PyprojectTOMLProjectSectionError(FileConfigError, PyprojectTOMLError):
    """Raised when the 'project' section is missing or invalid in 'pyproject.toml'."""

    @property
    def name(self) -> str:
        """The name of the file that has a configuration error."""
        return "pyproject.toml"


class PyprojectTOMLProjectNameError(PyprojectTOMLProjectSectionError):
    """Raised when the 'project.name' key is missing or invalid in 'pyproject.toml'."""


class PyprojectTOMLProjectDescriptionError(PyprojectTOMLProjectSectionError):
    """Raised when the 'project.description' key is missing or invalid in 'pyproject.toml'."""


class PyprojectTOMLValueAlreadySetError(PyprojectTOMLError, TOMLValueAlreadySetError):
    """Raised when a value is unexpectedly already set in the 'pyproject.toml' file."""


class PyprojectTOMLValueMissingError(PyprojectTOMLError, TOMLValueMissingError):
    """Raised when a value is unexpectedly missing from the 'pyproject.toml' file."""
