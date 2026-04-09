"""Error types for SonarQube operations."""

from __future__ import annotations

from usethis.errors import UsethisError


class SonarQubeError(UsethisError):
    """Base error for SonarQube operations."""


class MissingProjectKeyError(SonarQubeError):
    """Raised when the project key is missing from pyproject.toml."""


class InvalidSonarQubeProjectKeyError(SonarQubeError):
    """Raised when the project key is invalid for SonarQube."""


class CoverageReportConfigNotFoundError(SonarQubeError):
    """Raised when the XML coverage report configuration is missing."""
