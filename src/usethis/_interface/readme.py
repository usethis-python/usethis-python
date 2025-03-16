from __future__ import annotations

import typer

from usethis._config import quiet_opt, usethis_config
from usethis._config_file import files_manager
from usethis._core.badge import (
    add_badge,
    get_pre_commit_badge,
    get_ruff_badge,
)
from usethis._core.readme import add_readme
from usethis._tool import PreCommitTool, RuffTool


def readme(
    quiet: bool = quiet_opt,
    badges: bool = typer.Option(False, "--badges", help="Add relevant badges"),
) -> None:
    with usethis_config.set(quiet=quiet), files_manager():
        add_readme()

        if badges:
            if RuffTool().is_used():
                add_badge(get_ruff_badge())

            if PreCommitTool().is_used():
                add_badge(get_pre_commit_badge())
