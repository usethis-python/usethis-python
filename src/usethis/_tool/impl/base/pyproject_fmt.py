"""pyproject-fmt tool implementation."""

from __future__ import annotations

import contextlib
from typing import final

from typing_extensions import override

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._console import tick_print
from usethis._tool.base import Tool
from usethis._tool.impl.spec.pyproject_fmt import PyprojectFmtToolSpec
from usethis._types.backend import BackendEnum


@final
class PyprojectFmtTool(PyprojectFmtToolSpec, Tool):
    @override
    def apply(self) -> None:
        """Run pyproject-fmt to format pyproject.toml."""
        if get_backend() is not BackendEnum.uv:
            return

        tick_print("Running pyproject-fmt on 'pyproject.toml'.")
        with contextlib.suppress(UVSubprocessFailedError):
            call_uv_subprocess(
                ["run", "pyproject-fmt", "pyproject.toml"], change_toml=False
            )
