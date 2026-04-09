"""Registry of all available tool specifications."""

from __future__ import annotations

from usethis._tool.impl.spec.codespell import CodespellToolSpec
from usethis._tool.impl.spec.coverage_py import CoveragePyToolSpec
from usethis._tool.impl.spec.deptry import DeptryToolSpec
from usethis._tool.impl.spec.import_linter import ImportLinterToolSpec
from usethis._tool.impl.spec.mkdocs import MkDocsToolSpec
from usethis._tool.impl.spec.pre_commit import PreCommitToolSpec
from usethis._tool.impl.spec.pyproject_fmt import PyprojectFmtToolSpec
from usethis._tool.impl.spec.pyproject_toml import PyprojectTOMLToolSpec
from usethis._tool.impl.spec.pytest import PytestToolSpec
from usethis._tool.impl.spec.requirements_txt import RequirementsTxtToolSpec
from usethis._tool.impl.spec.ruff import RuffToolSpec
from usethis._tool.impl.spec.tach import TachToolSpec
from usethis._tool.impl.spec.ty import TyToolSpec
from usethis._tool.impl.spec.zensical import ZensicalToolSpec

ALL_TOOL_SPECS: list[
    CodespellToolSpec
    | CoveragePyToolSpec
    | DeptryToolSpec
    | ImportLinterToolSpec
    | MkDocsToolSpec
    | PreCommitToolSpec
    | PyprojectFmtToolSpec
    | PyprojectTOMLToolSpec
    | PytestToolSpec
    | RequirementsTxtToolSpec
    | RuffToolSpec
    | TachToolSpec
    | TyToolSpec
    | ZensicalToolSpec
] = [
    # Alphabetical order, matching ALL_TOOLS in usethis._tool.all_
    CodespellToolSpec(),
    CoveragePyToolSpec(),
    DeptryToolSpec(),
    ImportLinterToolSpec(),
    MkDocsToolSpec(),
    PreCommitToolSpec(),
    PyprojectFmtToolSpec(),
    PyprojectTOMLToolSpec(),
    PytestToolSpec(),
    RequirementsTxtToolSpec(),
    RuffToolSpec(),
    TachToolSpec(),
    TyToolSpec(),
    ZensicalToolSpec(),
]
