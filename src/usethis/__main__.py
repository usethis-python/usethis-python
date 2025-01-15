"""The Typer application for usethis."""

import sys

import typer

import usethis._interface.badge
import usethis._interface.browse
import usethis._interface.ci
import usethis._interface.show
import usethis._interface.tool
from usethis._config import quiet_opt, usethis_config
from usethis._core.badge import add_pre_commit_badge, add_ruff_badge
from usethis._core.readme import add_readme
from usethis._tool import PreCommitTool, RuffTool

try:
    from usethis._version import __version__
except ImportError:
    __version__ = None

app = typer.Typer(
    help=(
        "Automate Python package and project setup tasks that are otherwise "
        "performed manually."
    )
)
app.add_typer(usethis._interface.badge.app, name="badge")
app.add_typer(usethis._interface.browse.app, name="browse")
app.add_typer(usethis._interface.ci.app, name="ci")
app.add_typer(usethis._interface.show.app, name="show")
app.add_typer(usethis._interface.tool.app, name="tool")


@app.command(help="Add a README.md file to the project.")
def readme(
    quiet: bool = quiet_opt,
    badges: bool = typer.Option(False, "--badges", help="Add relevant badges"),
) -> None:
    with usethis_config.set(quiet=quiet):
        add_readme()

        if badges:
            if RuffTool().is_used():
                add_ruff_badge()

            if PreCommitTool().is_used():
                add_pre_commit_badge()


@app.command(help="Display the version of usethis.")
def version() -> None:
    if __version__ is not None:
        print(__version__)
    else:
        sys.exit(1)


app(prog_name="usethis")


__all__ = ["app"]
