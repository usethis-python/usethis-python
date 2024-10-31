import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._console import box_print

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
        _pypi(package=package, browser=browser)


def _pypi(*, package: str, browser: bool = False) -> None:
    url = f"https://pypi.org/project/{package}/"
    if browser:
        typer.launch(url)
    else:
        box_print(f"Open URL <{url}>.")
