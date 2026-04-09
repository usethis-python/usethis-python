"""Error types for SonarQube operations."""

from __future__ import annotations

from usethis.errors import UsethisError


class MissingProjectKeyError(UsethisError):
    """Raised when the project key is missing from pyproject.toml."""


class InvalidSonarQubeProjectKeyError(UsethisError):
    """Raised when the project key is invalid for SonarQube."""


class CoverageReportConfigNotFoundError(UsethisError):
    """Raised when the XML coverage report configuration is missing."""
