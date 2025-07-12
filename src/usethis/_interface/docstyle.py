from __future__ import annotations

import typer

from usethis._core.enums.docstyle import DocStyleEnum
from usethis._options import frozen_opt, offline_opt, quiet_opt


def docstyle(
    style: DocStyleEnum = typer.Argument(
        default="google", help="Docstring style to enforce."
    ),
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    from usethis._config import usethis_config
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._core.docstyle import use_docstyle
    from usethis.errors import UsethisError

    assert isinstance(style, DocStyleEnum)

    with (
        usethis_config.set(offline=offline, quiet=quiet, frozen=frozen),
        files_manager(),
    ):
        try:
            use_docstyle(style)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
