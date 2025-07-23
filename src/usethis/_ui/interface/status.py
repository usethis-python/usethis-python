from __future__ import annotations

import typer

from usethis._types.backend import BackendEnum
from usethis._types.status import DevelopmentStatusEnum
from usethis._ui.options import backend_opt, quiet_opt


def status(
    status: DevelopmentStatusEnum = typer.Argument(
        default=..., help="Docstring style to enforce."
    ),
    quiet: bool = quiet_opt,
    backend: BackendEnum = backend_opt,
) -> None:
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._core.status import use_development_status
    from usethis.errors import UsethisError

    assert isinstance(status, DevelopmentStatusEnum)
    assert isinstance(backend, BackendEnum)

    with usethis_config.set(quiet=quiet, backend=backend), files_manager():
        try:
            use_development_status(status)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
