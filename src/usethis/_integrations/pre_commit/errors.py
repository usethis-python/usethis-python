from __future__ import annotations

from usethis.errors import UsethisError


class PreCommitError(UsethisError):
    """Used when something goes wrong associated with pre-commit."""


class PreCommitInstallationError(PreCommitError):
    """Used when something goes wrong installing or uninstalling pre-commit hooks."""
