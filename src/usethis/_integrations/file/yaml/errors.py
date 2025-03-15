from __future__ import annotations

from usethis.errors import UsethisError


class InvalidYAMLError(UsethisError):
    """Raised when an invalid YAML is encountered."""
