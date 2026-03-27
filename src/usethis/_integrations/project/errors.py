"""Error types for project integration operations."""

from usethis.errors import UsethisError


class ImportGraphBuildFailedError(UsethisError):
    """Raised when the import graph cannot be built."""
