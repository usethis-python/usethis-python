import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._core.browse import browse_pypi

app = typer.Typer(help="Visit important project-related web pages.")


@app.command(help="Visit the PyPI project page for a package.")
def pypi(
    package: str,
    *,
    browser: bool = typer.Option(
        False, "--browser", help="Open the URL in the default web browser."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet):
        browse_pypi(package=package, browser=browser)
