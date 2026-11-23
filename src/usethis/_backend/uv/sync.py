"""Syncing of the uv environment."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._backend.uv.call import call_uv_subprocess
from usethis._config import usethis_config

if TYPE_CHECKING:
    from pathlib import Path


def sync_environment_via_uv(
    groups: list[str], *, path: Path, inexact: bool = True
) -> None:
    """Sync the environment of a project using uv, including the given dependency groups.

    Raises:
        UVSubprocessFailedError: If the sync fails.
    """
    # Inexact, so that packages which aren't part of the project are not removed
    with usethis_config.set(project_dir=path):
        call_uv_subprocess(
            ["sync", *(["--inexact"] if inexact else [])],
            change_toml=False,
            groups=groups,
        )
