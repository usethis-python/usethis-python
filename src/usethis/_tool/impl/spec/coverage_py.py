from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from usethis._config import usethis_config
from usethis._config_file import (
    DotCoverageRCManager,
)
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager


class CoveragePyToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Coverage.py",
            url="https://github.com/nedbat/coveragepy",
            managed_files=[Path(".coveragerc"), Path(".coveragerc.toml")],
        )

    def test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        from usethis._tool.impl.base.pytest import (  # to avoid circularity; # noqa: PLC0415
            PytestTool,
        )

        deps = [Dependency(name="coverage", extras=frozenset({"toml"}))]
        if unconditional or PytestTool().is_used():
            deps += [Dependency(name="pytest-cov")]
        return deps

    def preferred_file_manager(self) -> KeyValueFileManager:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return DotCoverageRCManager()
