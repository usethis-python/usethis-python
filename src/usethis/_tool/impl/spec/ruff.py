from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from usethis._config import usethis_config
from usethis._config_file import RuffTOMLManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager


class RuffToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Ruff",
            url="https://github.com/astral-sh/ruff",
            managed_files=[Path(".ruff.toml"), Path("ruff.toml")],
        )

    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="ruff")]

    def preferred_file_manager(self) -> KeyValueFileManager:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return RuffTOMLManager()
