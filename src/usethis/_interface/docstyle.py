from __future__ import annotations

import typer

from usethis._config import quiet_opt, usethis_config
from usethis._config_file import files_manager
from usethis._console import err_print
from usethis._core.docstyle import UnknownDocstringStyleError, use_docstyle
from usethis.errors import UsethisError


def docstyle(
    style: str = typer.Argument(
        default=None,
        help="Docstring style to enforce. Options: 'numpy', 'google', 'pep257'",
    ),
    quiet: bool = quiet_opt,
) -> None:
    try:
        if style not in ("numpy", "google", "pep257"):
            msg = f"Invalid docstring style: {style}. Choose from 'numpy', 'google', or 'pep257'."
            raise UnknownDocstringStyleError(msg)
    except UnknownDocstringStyleError as err:
        err_print(err)
        raise typer.Exit(code=1) from None

    with usethis_config.set(quiet=quiet), files_manager():
        try:
            use_docstyle(style)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
