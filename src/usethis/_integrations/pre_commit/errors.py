from __future__ import annotations

from usethis.errors import FileConfigError, UsethisError


class PreCommitError(UsethisError):
    """Used when something goes wrong associated with pre-commit."""


class PreCommitInstallationError(PreCommitError):
    """Used when something goes wrong installing or uninstalling pre-commit hooks."""


class PreCommitConfigYAMLConfigError(FileConfigError):
    """Raised when there the '.pre-commit-config.yaml' file does not conform to the expected schema."""

    @property
    def name(self) -> str:
        """The name of the file that has a configuration error."""
        return ".pre-commit-config.yaml"
