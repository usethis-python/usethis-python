"""pyproject.toml as a managed tool."""

from __future__ import annotations

from typing import final

from typing_extensions import override

from usethis._console import how_print, info_print, instruct_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._tool.base import Tool
from usethis._tool.impl.base.codespell import CodespellTool
from usethis._tool.impl.base.coverage_py import CoveragePyTool
from usethis._tool.impl.base.deptry import DeptryTool
from usethis._tool.impl.base.import_linter import ImportLinterTool
from usethis._tool.impl.base.mkdocs import MkDocsTool
from usethis._tool.impl.base.pre_commit import PreCommitTool
from usethis._tool.impl.base.pyproject_fmt import PyprojectFmtTool
from usethis._tool.impl.base.pytest import PytestTool
from usethis._tool.impl.base.requirements_txt import RequirementsTxtTool
from usethis._tool.impl.base.ruff import RuffTool
from usethis._tool.impl.base.tach import TachTool
from usethis._tool.impl.base.ty import TyTool
from usethis._tool.impl.spec.pyproject_toml import PyprojectTOMLToolSpec

# N.B. this list must be kept in-sync with usethis._tool.all_.ALL_TOOLS.
OTHER_TOOLS: list[Tool] = [
    CodespellTool(),
    CoveragePyTool(),
    DeptryTool(),
    ImportLinterTool(),
    MkDocsTool(),
    PreCommitTool(),
    PyprojectFmtTool(),
    PytestTool(),
    RequirementsTxtTool(),
    RuffTool(),
    TachTool(),
    TyTool(),
]


@final
class PyprojectTOMLTool(PyprojectTOMLToolSpec, Tool):
    @override
    def print_how_to_use(self) -> None:
        how_print("Populate 'pyproject.toml' with the project configuration.")
        info_print(
            "Learn more at https://packaging.python.org/en/latest/guides/writing-pyproject-toml/"
        )

    @override
    def remove_managed_files(self) -> None:
        # https://github.com/usethis-python/usethis-python/issues/416
        # We need to step through the tools and see if pyproject.toml is the active
        # config file.
        # If it isn't an active config file, no action is required.
        # If it is an active config file, we  display a message to the user to inform
        # them that the active config is being removed and they need to re-configure
        # the tool

        instruct_print("Check that important config in 'pyproject.toml' is not lost.")

        for tool in OTHER_TOOLS:
            if (
                tool.is_used()
                and PyprojectTOMLManager() in tool.get_active_config_file_managers()
            ):
                # Warn the user
                instruct_print(
                    f"The {tool.name} tool was using 'pyproject.toml' for config, "
                    f"but that file is being removed. You will need to re-configure it."
                )

        super().remove_managed_files()
