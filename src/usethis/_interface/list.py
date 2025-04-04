from __future__ import annotations

import typer

from usethis._config_file import files_manager
from usethis._console import err_print
from usethis._core.list import show_usage_table
from usethis.errors import UsethisError


def list(  # noqa: A001
) -> None:
    with files_manager():
        try:
            show_usage_table()
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
