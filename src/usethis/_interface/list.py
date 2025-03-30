from __future__ import annotations

from usethis._config import quiet_opt
from usethis._config_file import files_manager
from usethis._core.list import show_usage_table


def list(  # noqa: A001
    quiet: bool = quiet_opt,
) -> None:
    if quiet:
        return

    with files_manager():
        show_usage_table()
