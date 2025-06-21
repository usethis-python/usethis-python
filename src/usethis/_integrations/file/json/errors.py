from __future__ import annotations

from usethis.errors import FileDecodeError, UsethisError


class JSONError(UsethisError):
    """Base class for JSON-related errors."""


class UnexpectedJSONOpenError(JSONError):
    """Raised when the JSON file is unexpectedly opened."""


class JSONNotFoundError(FileNotFoundError, JSONError):
    """Raised when a JSON file is unexpectedly not found."""


class JSONDecodeError(FileDecodeError, JSONError):
    """Raised when a JSON file is unexpectedly not decodable."""


class UnexpectedJSONIOError(JSONError):
    """Raised when an unexpected attempt is made to read or write the JSON file."""
