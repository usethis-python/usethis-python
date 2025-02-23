from usethis.errors import UsethisError


class TOMLError(UsethisError):
    """Base class for TOML-related errors."""


class TOMLValueMissingError(TOMLError):
    """Raised when a value is unexpectedly missing from the TOML file."""
