from usethis.errors import UsethisError


class TOMLError(UsethisError):
    """Base class for TOML-related errors."""


class TOMLValueAlreadySetError(TOMLError):
    """Raised when a value is unexpectedly already set in the TOML file."""


class TOMLValueMissingError(TOMLError):
    """Raised when a value is unexpectedly missing from the TOML file."""
