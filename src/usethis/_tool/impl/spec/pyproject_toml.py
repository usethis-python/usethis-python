from __future__ import annotations

from pathlib import Path

from usethis._tool.base import ToolMeta, ToolSpec


class PyprojectTOMLToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="pyproject.toml",
            url="https://packaging.python.org/en/latest/guides/writing-pyproject-toml/",
            managed_files=[Path("pyproject.toml")],
        )
