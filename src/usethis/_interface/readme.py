import typer

from usethis._config import quiet_opt, usethis_config
from usethis._core.badge import add_pre_commit_badge, add_ruff_badge
from usethis._core.readme import add_readme
from usethis._integrations.pyproject.io_ import pyproject_toml_io_manager
from usethis._tool import PreCommitTool, RuffTool


def readme(
    quiet: bool = quiet_opt,
    badges: bool = typer.Option(False, "--badges", help="Add relevant badges"),
) -> None:
    with usethis_config.set(quiet=quiet), pyproject_toml_io_manager.open():
        add_readme()

        if badges:
            if RuffTool().is_used():
                add_ruff_badge()

            if PreCommitTool().is_used():
                add_pre_commit_badge()
