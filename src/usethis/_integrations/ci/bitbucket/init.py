from __future__ import annotations

from usethis._config import usethis_config
from usethis._console import tick_print


def ensure_bitbucket_pipelines_config_exists() -> None:
    """Ensure 'bitbucket-pipelines.yml' exists with minimal valid content."""
    name = "bitbucket-pipelines.yml"
    path = usethis_config.cpd() / name

    if not path.exists():
        tick_print(f"Writing '{name}'.")
        # N.B. where necessary, we can opt to use a different image from this default
        # on a per-step basis, so this is safe even when we want to use Python images.
        path.write_text("image: atlassian/default-image:3\n", encoding="utf-8")
