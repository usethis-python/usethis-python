from __future__ import annotations

import typer

from usethis._options import backend_opt, quiet_opt
from usethis._types.backend import BackendEnum
from usethis._types.docstyle import DocStyleEnum


def docstyle(
    style: DocStyleEnum = typer.Argument(
        default="google", help="Docstring style to enforce."
    ),
    quiet: bool = quiet_opt,
    backend: BackendEnum = backend_opt,
) -> None:
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._core.docstyle import use_docstyle
    from usethis.errors import UsethisError

    assert isinstance(style, DocStyleEnum)
    assert isinstance(backend, BackendEnum)

    with usethis_config.set(quiet=quiet, backend=backend), files_manager():
        try:
            use_docstyle(style)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
