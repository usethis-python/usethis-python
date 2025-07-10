from __future__ import annotations

from usethis.errors import FileDecodeError, UsethisError


class TOMLError(UsethisError):
    """Base class for TOML-related errors."""


class TOMLValueAlreadySetError(TOMLError):
    """Raised when a value is unexpectedly already set in the TOML file."""


class TOMLValueMissingError(KeyError, TOMLError):
    """Raised when a value is unexpectedly missing from the TOML file."""


class TOMLValueInvalidError(TOMLError):
    """Raised when a value in the TOML file is unexpectedly invalid."""


class TOMLNotFoundError(FileNotFoundError, TOMLError):
    """Raised when a TOML file is unexpectedly not found."""


class TOMLDecodeError(FileDecodeError, TOMLError):
    """Raised when a TOML file is unexpectedly not decodable."""


class UnexpectedTOMLOpenError(TOMLError):
    """Raised when the TOML file is unexpectedly opened."""


class UnexpectedTOMLIOError(TOMLError):
    """Raised when an unexpected attempt is made to read or write the TOML file."""
