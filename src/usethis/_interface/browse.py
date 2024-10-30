import typer

from usethis._console import console
from usethis._interface import offline_opt, quiet_opt

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
    with console.set(quiet=quiet):
        _pypi(package=package, browser=browser, offline=offline)


def _pypi(*, package: str, browser: bool = False, offline: bool = False) -> None:
    _ = offline  # Already no network access required

    url = f"https://pypi.org/project/{package}/"
    if browser:
        typer.launch(url)
    else:
        console.box_print(f"Open URL <{url}>.")
