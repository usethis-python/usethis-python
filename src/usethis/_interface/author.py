from __future__ import annotations

import typer

from usethis._config import quiet_opt, usethis_config
from usethis._config_file import files_manager
from usethis._core.author import add_author


def author(
    name: str = typer.Option(..., "--name", help="Author name"),
    email: str | None = typer.Option(None, "--email", help="Author email"),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite any existing authors"
    ),
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(quiet=quiet), files_manager():
        add_author(
            name=name,
            email=email,
            overwrite=overwrite,
        )
