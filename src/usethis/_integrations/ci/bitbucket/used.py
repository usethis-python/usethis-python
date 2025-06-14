from __future__ import annotations

from usethis._config import usethis_config


def is_bitbucket_used() -> bool:
    return (usethis_config.cpd() / "bitbucket-pipelines.yml").exists()
