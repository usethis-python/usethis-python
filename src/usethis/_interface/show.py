import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._config_file import files_manager
from usethis._console import err_print
from usethis._core.show import show_name, show_sonarqube_config
from usethis.errors import UsethisError

app = typer.Typer(
    help="Show information about the current project.", add_completion=False
)


@app.command(help="Show the name of the project")
def name(
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        try:
            show_name()
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None


@app.command(
    name="sonarqube",
    help="Show the sonar-projects.properties file for SonarQube.",
)
def sonarqube(
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        try:
            show_sonarqube_config()
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
