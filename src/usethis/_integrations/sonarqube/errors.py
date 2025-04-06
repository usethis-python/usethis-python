from __future__ import annotations

from usethis.errors import UsethisError


class SonarQubeError(UsethisError):
    """Base class for SonarQube errors."""


class MissingProjectKeyError(SonarQubeError):
    """Raised when the project key is missing from pyproject.toml."""


class InvalidSonarQubeProjectKeyError(SonarQubeError):
    """Raised when the project key is invalid for SonarQube."""


class CoverageReportConfigNotFoundError(SonarQubeError):
    """Raised when the XML coverage report configuration is missing."""
