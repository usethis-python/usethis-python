from __future__ import annotations

import contextlib
from pathlib import Path
from typing import TYPE_CHECKING

from usethis._integrations.file.ini.io_ import INIFileManager
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.file.setup_cfg.io_ import SetupCFGManager
from usethis._integrations.file.toml.io_ import TOMLFileManager

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextlib.contextmanager
def files_manager() -> Iterator[None]:
    with (
        PyprojectTOMLManager(),
        SetupCFGManager(),
        DotRuffTOMLManager(),
        RuffTOMLManager(),
        CodespellRCManager(),
    ):
        yield


class DotRuffTOMLManager(TOMLFileManager):
    """Class to manage the .ruff.toml file."""

    @property
    def relative_path(self) -> Path:
        return Path(".ruff.toml")


class RuffTOMLManager(TOMLFileManager):
    """Class to manage the ruff.toml file."""

    @property
    def relative_path(self) -> Path:
        return Path("ruff.toml")


class CodespellRCManager(INIFileManager):
    """Class to manage the .codespellrc file."""

    @property
    def relative_path(self) -> Path:
        return Path(".codespellrc")
