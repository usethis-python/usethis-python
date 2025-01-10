import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._core.badge import add_ruff_badge

app = typer.Typer(help="Add badges to the top of the README.md file.")


@app.command(help="Visit the PyPI project page for a package.")
def ruff(
    *,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet):
        add_ruff_badge()
