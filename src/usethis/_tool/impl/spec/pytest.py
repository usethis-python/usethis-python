from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from usethis._config import usethis_config
from usethis._config_file import PytestINIManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.rule import RuleConfig
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager

_PYTEST_PIP_CMD = "pip install pytest"


class PytestToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="pytest",
            url="https://github.com/pytest-dev/pytest",
            managed_files=[
                Path(".pytest.ini"),
                Path("pytest.ini"),
                Path("tests/conftest.py"),
            ],
            rule_config=RuleConfig(selected=["PT"], nontests_unmanaged_ignored=["PT"]),
        )

    def raw_cmd(self) -> str:
        return "pytest"

    def test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="pytest")]

    def preferred_file_manager(self) -> KeyValueFileManager:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return PytestINIManager()
