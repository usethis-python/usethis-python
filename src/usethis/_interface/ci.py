import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._core.ci import use_ci_bitbucket

app = typer.Typer(help="Add config for Continuous Integration (CI) pipelines.")


@app.command(help="Use Bitbucket pipelines for CI.")
def bitbucket(
    remove: bool = typer.Option(
        False, "--remove", help="Remove Bitbucket pipelines CI instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet):
        use_ci_bitbucket(remove=remove)
