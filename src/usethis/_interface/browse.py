import typer

from usethis._console import console

app = typer.Typer(help="Visit important project-related web pages.")


@app.command(help="Visit the PyPI project page for a package.")
def pypi(
    package: str,
    *,
    browser: bool = typer.Option(
        False, "--browser", help="Open the URL in the default web browser."
    ),
) -> None:
    _pypi(package=package, browser=browser)


def _pypi(*, package: str, browser: bool = False) -> None:
    url = f"https://pypi.org/project/{package}/"
    if browser:
        typer.launch(url)
    else:
        console.print(f"☐ Open URL <{url}>.", style="blue")
