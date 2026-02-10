from __future__ import annotations

from usethis.errors import FileDecodeError, UsethisError


class YAMLError(UsethisError):
    """Base class for YAML-related errors."""


class YAMLValueAlreadySetError(YAMLError):
    """Raised when a value is unexpectedly already set in the YAML file."""


class UnexpectedYAMLValueError(YAMLError):
    """Raised when an unexpected value is encountered in the YAML file."""


class YAMLValueMissingError(KeyError, YAMLError):
    """Raised when a value is unexpectedly missing from the YAML file."""


class YAMLNotFoundError(FileNotFoundError, YAMLError):
    """Raised when a YAML file is unexpectedly not found."""


class YAMLDecodeError(FileDecodeError, YAMLError):
    """Raised when a YAML file is unexpectedly not decodable."""


class UnexpectedYAMLOpenError(YAMLError):
    """Raised when the YAML file is unexpectedly opened."""


class UnexpectedYAMLIOError(YAMLError):
    """Raised when an unexpected attempt is made to read or write the YAML file."""
