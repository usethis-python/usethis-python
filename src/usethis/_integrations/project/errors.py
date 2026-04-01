"""Error types for project integration operations."""

from usethis.errors import UsethisError


class ImportGraphBuildFailedError(UsethisError):
    """Raised when the import graph cannot be built."""


class LicenseDetectionError(UsethisError):
    """Raised when the project license cannot be determined."""
