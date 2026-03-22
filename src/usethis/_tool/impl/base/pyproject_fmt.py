from __future__ import annotations

from typing import final

from usethis._tool.base import Tool
from usethis._tool.impl.spec.pyproject_fmt import PyprojectFmtToolSpec


@final
class PyprojectFmtTool(PyprojectFmtToolSpec, Tool):
    pass
