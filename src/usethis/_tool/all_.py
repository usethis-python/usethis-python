"""Registry of all available tools."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

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
from usethis._tool.impl.base.tach import TachTool
from usethis._tool.impl.base.ty import TyTool

if TYPE_CHECKING:
    from usethis._tool.base import Tool

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
    | TachTool
    | TyTool
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
    TachTool(),
    TyTool(),
]

# All tools except PyprojectTOMLTool, in the same canonical order as ALL_TOOLS.
OTHER_TOOLS: list[Tool] = [
    tool for tool in ALL_TOOLS if not isinstance(tool, PyprojectTOMLTool)
]
