from __future__ import annotations

from usethis.errors import UsethisError


class INIError(UsethisError):
    """Base class for INI-related errors."""


class INIValueAlreadySetError(INIError):
    """Raised when a value is unexpectedly already set in the INI file."""


class UnexpectedINIOpenError(INIError):
    """Raised when the INI file is unexpectedly opened."""


class ININotFoundError(FileNotFoundError, INIError):
    """Raised when a INI file is unexpectedly not found."""


class INIDecodeError(INIError):
    """Raised when a INI file is unexpectedly not decodable."""


class UnexpectedINIIOError(INIError):
    """Raised when an unexpected attempt is made to read or write the INI file."""
