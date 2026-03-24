import typer

from usethis._config import usethis_config
from usethis._types.backend import BackendEnum
from usethis._ui.options import (
    backend_opt,
    ci_remove_opt,
    frozen_opt,
    matrix_python_opt,
    offline_opt,
    quiet_opt,
)

app = typer.Typer(
    help="Add config for Continuous Integration (CI) pipelines.",
    add_completion=False,
    deprecated=True,
)


@app.command(help="Use Bitbucket Pipelines for CI.")
def bitbucket(
    remove: bool = ci_remove_opt,
    matrix_python: bool = matrix_python_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
    backend: BackendEnum = backend_opt,
) -> None:
    from usethis._config_file import files_manager
    from usethis._console import err_print, warn_print
    from usethis._core.ci import use_ci_bitbucket
    from usethis.errors import UsethisError

    assert isinstance(backend, BackendEnum)

    warn_print("'usethis ci' is deprecated and will be removed in v0.20.0.")

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
