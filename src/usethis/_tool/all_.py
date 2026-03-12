from __future__ import annotations

from typing import TypeAlias

from usethis._tool.impl.base.codespell import CodespellTool
from usethis._tool.impl.base.coverage_py import CoveragePyTool
from usethis._tool.impl.base.deptry import DeptryTool
from usethis._tool.impl.base.import_linter import ImportLinterTool
from usethis._tool.impl.base.mkdocs import MkDocsTool
from usethis._tool.impl.base.pre_commit import PreCommitTool
from usethis._tool.impl.base.pyproject_fmt import PyprojectFmtTool
from usethis._tool.impl.base.pyproject_toml import PyprojectTOMLTool
from usethis._tool.impl.base.pytest import PytestTool
from usethis._tool.impl.base.requirements_txt import RequirementsTxtTool
from usethis._tool.impl.base.ruff import RuffTool

SupportedToolType: TypeAlias = (
    CodespellTool
    | CoveragePyTool
    | DeptryTool
    | ImportLinterTool
    | MkDocsTool
    | PreCommitTool
    | PyprojectFmtTool
    | PyprojectTOMLTool
    | PytestTool
    | RequirementsTxtTool
    | RuffTool
)

ALL_TOOLS: list[SupportedToolType] = [
    # Alphabetical order
    CodespellTool(),
    CoveragePyTool(),
    DeptryTool(),
    ImportLinterTool(),
    MkDocsTool(),
    PreCommitTool(),
    PyprojectFmtTool(),
    PyprojectTOMLTool(),
    PytestTool(),
    RequirementsTxtTool(),
    RuffTool(),
]
