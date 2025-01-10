import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._core.badge import add_pre_commit_badge, add_ruff_badge

app = typer.Typer(help="Add badges to the top of the README.md file.")


@app.command(help="Add a badge for the Ruff linter.")
def ruff(
    *,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet):
        add_ruff_badge()


@app.command(help="Add a badge for the pre-commit framework.")
def pre_commit(
    *,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet):
        add_pre_commit_badge()
