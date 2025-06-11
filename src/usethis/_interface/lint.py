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
from usethis._toolset.lint import use_linters
from usethis.errors import UsethisError


def lint(
    remove: bool = remove_opt,
    how: bool = how_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    """Add recommended linters to the project."""
    with (
        usethis_config.set(offline=offline, quiet=quiet, frozen=frozen),
        files_manager(),
    ):
        try:
            use_linters(remove=remove, how=how)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
