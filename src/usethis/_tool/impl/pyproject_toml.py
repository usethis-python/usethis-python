from __future__ import annotations

from pathlib import Path

from usethis._console import how_print, info_print, instruct_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._tool.base import Tool, ToolMeta, ToolSpec
from usethis._tool.impl.codespell import CodespellTool
from usethis._tool.impl.coverage_py import CoveragePyTool
from usethis._tool.impl.deptry import DeptryTool
from usethis._tool.impl.import_linter import ImportLinterTool
from usethis._tool.impl.mkdocs import MkDocsTool
from usethis._tool.impl.pre_commit import PreCommitTool
from usethis._tool.impl.pyproject_fmt import PyprojectFmtTool
from usethis._tool.impl.pytest import PytestTool
from usethis._tool.impl.requirements_txt import RequirementsTxtTool
from usethis._tool.impl.ruff import RuffTool

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
]


class PyprojectTOMLToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="pyproject.toml",
            url="https://packaging.python.org/en/latest/guides/writing-pyproject-toml/",
            managed_files=[Path("pyproject.toml")],
        )


class PyprojectTOMLTool(PyprojectTOMLToolSpec, Tool):
    def print_how_to_use(self) -> None:
        how_print("Populate 'pyproject.toml' with the project configuration.")
        info_print(
            "Learn more at https://packaging.python.org/en/latest/guides/writing-pyproject-toml/"
        )

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
