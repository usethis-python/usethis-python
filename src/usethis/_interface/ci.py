import typer

from usethis._options import frozen_opt, offline_opt, quiet_opt

app = typer.Typer(
    help="Add config for Continuous Integration (CI) pipelines.", add_completion=False
)


@app.command(help="Use Bitbucket pipelines for CI.")
def bitbucket(
    remove: bool = typer.Option(
        False, "--remove", help="Remove Bitbucket pipelines CI instead of adding it."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._core.ci import use_ci_bitbucket
    from usethis.errors import UsethisError

    with (
        usethis_config.set(offline=offline, quiet=quiet, frozen=frozen),
        files_manager(),
    ):
        try:
            use_ci_bitbucket(remove=remove)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
