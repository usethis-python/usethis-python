from __future__ import annotations

from usethis._config import usethis_config


def is_bitbucket_used() -> bool:
    """Detect if Bitbucket Pipelines is used in the current project."""
    return (usethis_config.cpd() / "bitbucket-pipelines.yml").exists()
