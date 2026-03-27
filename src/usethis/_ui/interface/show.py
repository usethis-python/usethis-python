from pathlib import Path

import typer

from usethis._config import usethis_config
from usethis._ui.options import offline_opt, output_file_opt, quiet_opt

app = typer.Typer(
    help="Show information about the current project.", add_completion=False
)

# show sonarqube options
project_key_opt = typer.Option(
    None,
    "--project-key",
    help="SonarQube project key. If not provided, will be read from 'tool.usethis.sonarqube.project-key' in 'pyproject.toml'.",
)


@app.command(help="Show the inferred project manager backend, e.g. 'uv' or 'none'.")
def backend(
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    output_file: Path | None = output_file_opt,
) -> None:
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._core.show import show_backend
    from usethis.errors import UsethisError

    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        try:
            show_backend(output_file=output_file)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None


@app.command(help="Show the name of the project")
def name(
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    output_file: Path | None = output_file_opt,
) -> None:
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._core.show import show_name
    from usethis.errors import UsethisError

    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        try:
            show_name(output_file=output_file)
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
    project_key: str | None = project_key_opt,
    output_file: Path | None = output_file_opt,
) -> None:
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._core.show import show_sonarqube_config
    from usethis.errors import UsethisError

    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        try:
            show_sonarqube_config(project_key=project_key, output_file=output_file)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
