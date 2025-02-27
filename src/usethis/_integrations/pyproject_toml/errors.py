from usethis._integrations.toml.errors import (
    TOMLError,
    TOMLValueAlreadySetError,
    TOMLValueMissingError,
)


class PyprojectTOMLError(TOMLError):
    """Raised when aspects of 'pyproject.toml' are missing, invalid, or unexpected."""


class PyprojectTOMLNotFoundError(PyprojectTOMLError, FileNotFoundError):
    """Raised when a pyproject.toml file is not found."""


class PyprojectTOMLInitError(PyprojectTOMLError):
    """Raised when a pyproject.toml file cannot be created."""


class PyprojectTOMLDecodeError(PyprojectTOMLError):
    """Raised when a pyproject.toml file cannot be decoded."""


class PyprojectTOMLProjectNameError(PyprojectTOMLError):
    """Raised when the 'project.name' key is missing or invalid in 'pyproject.toml'."""


class PyprojectTOMLProjectDescriptionError(PyprojectTOMLError):
    """Raised when the 'project.description' key is missing or invalid in 'pyproject.toml'."""


class PyprojectTOMLProjectSectionError(PyprojectTOMLError):
    """Raised when the 'project' section is missing or invalid in 'pyproject.toml'."""


class PyprojectTOMLValueAlreadySetError(PyprojectTOMLError, TOMLValueAlreadySetError):
    """Raised when a value is unexpectedly already set in the 'pyproject.toml' file."""


class PyprojectTOMLValueMissingError(PyprojectTOMLError, TOMLValueMissingError):
    """Raised when a value is unexpectedly missing from the 'pyproject.toml' file."""
