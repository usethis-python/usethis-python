from __future__ import annotations

from usethis._config import usethis_config
from usethis._console import tick_print


def ensure_pre_commit_config_exists() -> None:
    """Ensure '.pre-commit-config.yaml' exists with minimal valid content."""
    name = ".pre-commit-config.yaml"
    path = usethis_config.cpd() / name

    if not path.exists():
        tick_print(f"Writing '{name}'.")
        path.write_text("repos: []\n", encoding="utf-8")
