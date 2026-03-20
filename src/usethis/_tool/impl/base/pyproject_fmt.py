from __future__ import annotations

from usethis._tool.base import Tool
from usethis._tool.impl.spec.pyproject_fmt import PyprojectFmtToolSpec


class PyprojectFmtTool(PyprojectFmtToolSpec, Tool):
    pass
