from __future__ import annotations

from usethis.errors import FileDecodeError, UsethisError


class INIError(UsethisError):
    """Base class for INI-related errors."""


class INIValueAlreadySetError(INIError):
    """Raised when a value is unexpectedly already set in the INI file."""


class INIValueMissingError(KeyError, INIError):
    """Raised when a value is unexpectedly missing from the INI file."""


class UnexpectedINIOpenError(INIError):
    """Raised when the INI file is unexpectedly opened."""


class ININotFoundError(FileNotFoundError, INIError):
    """Raised when a INI file is unexpectedly not found."""


class INIDecodeError(FileDecodeError, INIError):
    """Raised when a INI file is unexpectedly not decodable."""


class UnexpectedINIIOError(INIError):
    """Raised when an unexpected attempt is made to read or write the INI file."""


class INIStructureError(INIError):
    """Raised when the INI file has an unexpected structure."""


class InvalidINITypeError(TypeError, INIStructureError):
    """Raised when an invalid type is encountered in the INI file."""


class ININestingError(ValueError, INIStructureError):
    """Raised when there is an unexpected nesting of INI sections."""
