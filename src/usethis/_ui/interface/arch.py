"""CLI commands for architecture enforcement tools."""

import typer

from usethis._config import usethis_config
from usethis._types.backend import BackendEnum
from usethis._ui.options import (
    backend_opt,
    frozen_opt,
    how_opt,
    no_sync_opt,
    offline_opt,
    quiet_opt,
    remove_opt,
)


def arch(
    remove: bool = remove_opt,
    how: bool = how_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
    no_sync: bool = no_sync_opt,
    backend: BackendEnum = backend_opt,
) -> None:
    """Add recommended architecture analysis tools to the project."""
    from usethis._config_file import files_manager
    from usethis._console import err_print
    from usethis._toolset.arch import use_arch_tools
    from usethis.errors import UsethisError

    with (
        usethis_config.set(
            offline=offline,
            quiet=quiet,
            frozen=frozen,
            no_sync=no_sync,
            backend=backend,
        ),
        files_manager(),
    ):
        try:
            use_arch_tools(remove=remove, how=how)
        except UsethisError as err:
            err_print(err)
            raise typer.Exit(code=1) from None
