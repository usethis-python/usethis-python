from __future__ import annotations

from usethis._config_file import files_manager
from usethis._core.list import show_usage_table


def list(  # noqa: A001
) -> None:
    with files_manager():
        show_usage_table()
