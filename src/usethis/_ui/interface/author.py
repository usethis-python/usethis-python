from __future__ import annotations

import typer

from usethis._config import usethis_config
from usethis._types.backend import BackendEnum
from usethis._ui.options import (
    author_email_opt,
    author_name_opt,
    author_overwrite_opt,
    backend_opt,
    quiet_opt,
)


def author(
    name: str = author_name_opt,
    email: str = author_email_opt,
    overwrite: bool = author_overwrite_opt,
    quiet: bool = quiet_opt,
    backend: BackendEnum = backend_opt,
) -> None:
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._core.author import add_author
    from usethis.errors import UsethisError

    assert isinstance(backend, BackendEnum)

    if not email:
        email_arg = None
    else:
        email_arg = email

    with usethis_config.set(quiet=quiet, backend=backend), files_manager():
        try:
            add_author(name=name, email=email_arg, overwrite=overwrite)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
