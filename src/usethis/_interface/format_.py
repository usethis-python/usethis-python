import typer

from usethis._config import (
    frozen_opt,
    how_opt,
    offline_opt,
    quiet_opt,
    remove_opt,
    usethis_config,
)
from usethis._config_file import files_manager
from usethis._console import err_print
from usethis._toolset.format_ import use_formatters
from usethis.errors import UsethisError


def format_(
    remove: bool = remove_opt,
    how: bool = how_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    """Add recommended formatters to the project."""
    with (
        usethis_config.set(offline=offline, quiet=quiet, frozen=frozen),
        files_manager(),
    ):
        try:
            use_formatters(remove=remove, how=how)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
