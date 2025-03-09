from __future__ import annotations

from usethis.errors import UsethisError


class UnexpectedImportPipelineError(UsethisError):
    """Raised when an import pipeline is unexpectedly encountered."""
