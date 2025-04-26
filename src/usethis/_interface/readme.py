from __future__ import annotations

import typer

from usethis._config import quiet_opt, usethis_config
from usethis._config_file import files_manager
from usethis._console import err_print
from usethis._core.badge import (
    add_badge,
    get_pre_commit_badge,
    get_ruff_badge,
    get_usethis_badge,
    get_uv_badge,
)
from usethis._core.readme import add_readme
from usethis._integrations.uv.used import is_uv_used
from usethis._tool.impl.pre_commit import PreCommitTool
from usethis._tool.impl.ruff import RuffTool
from usethis.errors import UsethisError


def readme(
    quiet: bool = quiet_opt,
    badges: bool = typer.Option(False, "--badges", help="Add relevant badges"),
) -> None:
    with usethis_config.set(quiet=quiet), files_manager():
        try:
            add_readme()

            if badges:
                if RuffTool().is_used():
                    add_badge(get_ruff_badge())

                if PreCommitTool().is_used():
                    add_badge(get_pre_commit_badge())

                if is_uv_used():
                    add_badge(get_uv_badge())

                add_badge(get_usethis_badge())
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
