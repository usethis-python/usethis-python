from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._console import how_print, info_print
from usethis._integrations.ci.bitbucket.config import (
    add_bitbucket_pipelines_config,
    remove_bitbucket_pipelines_config,
)
from usethis._tool.impl.codespell import CodespellTool
from usethis._tool.impl.deptry import DeptryTool
from usethis._tool.impl.import_linter import ImportLinterTool
from usethis._tool.impl.pre_commit import PreCommitTool
from usethis._tool.impl.pyproject_fmt import PyprojectFmtTool
from usethis._tool.impl.pytest import PytestTool
from usethis._tool.impl.ruff import RuffTool

if TYPE_CHECKING:
    from usethis._tool.base import Tool

# These are tools would run via pre-commit if available
_CI_QA_TOOLS: list[type[Tool]] = [  # Not including pytest and pre-commit
    # This order should match the canonical order in the function which adds
    # steps
    PyprojectFmtTool,
    RuffTool,
    DeptryTool,
    ImportLinterTool,
    CodespellTool,
]


def use_ci_bitbucket(
    *, remove: bool = False, how: bool = False, matrix_python: bool = True
) -> None:
    if how:
        print_how_to_use_ci_bitbucket()
        return

    if not remove:
        use_pre_commit = PreCommitTool().is_used()
        use_any_tool = (
            use_pre_commit or PytestTool().is_used() or _using_any_ci_qa_tools()
        )

        add_bitbucket_pipelines_config(report_placeholder=not use_any_tool)

        if use_pre_commit:
            PreCommitTool().update_bitbucket_steps()
        else:
            for tool in _CI_QA_TOOLS:
                tool().update_bitbucket_steps()

        PytestTool().update_bitbucket_steps(matrix_python=matrix_python)

        print_how_to_use_ci_bitbucket()
    else:
        remove_bitbucket_pipelines_config()


def _using_any_ci_qa_tools():
    return any(tool().is_used() for tool in _CI_QA_TOOLS)


def print_how_to_use_ci_bitbucket() -> None:
    """Print how to use the Bitbucket CI service."""
    _suggest_pytest()

    how_print("Run your pipeline via the Bitbucket website.")


def _suggest_pytest() -> None:
    if not PytestTool().is_used():
        info_print("Consider `usethis tool pytest` to test your code for the pipeline.")
