import typer

from usethis._config import usethis_config
from usethis._types.backend import BackendEnum
from usethis._ui.options import backend_opt, frozen_opt, offline_opt, quiet_opt

app = typer.Typer(
    help="Add config for Continuous Integration (CI) pipelines.", add_completion=False
)


@app.command(help="Use Bitbucket Pipelines for CI.")
def bitbucket(
    remove: bool = typer.Option(
        False, "--remove", help="Remove Bitbucket Pipelines CI instead of adding it."
    ),
    matrix_python: bool = typer.Option(
        True,
        "--matrix-python/--no-matrix-python",
        help="Test against multiple Python versions.",
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
    backend: BackendEnum = backend_opt,
) -> None:
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._core.ci import use_ci_bitbucket
    from usethis.errors import UsethisError

    assert isinstance(backend, BackendEnum)

    with (
        usethis_config.set(
            offline=offline,
            quiet=quiet,
            frozen=frozen,
            backend=backend,
        ),
        files_manager(),
    ):
        try:
            use_ci_bitbucket(remove=remove, matrix_python=matrix_python)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
