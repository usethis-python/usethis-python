import typer

from usethis._ui.options import offline_opt, quiet_opt

app = typer.Typer(
    help="Visit important project-related web pages.", add_completion=False
)


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
    from usethis._config import usethis_config
    from usethis._console import err_print
    from usethis._core.browse import browse_pypi
    from usethis.errors import UsethisError

    with usethis_config.set(offline=offline, quiet=quiet):
        try:
            browse_pypi(package=package, browser=browser)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
