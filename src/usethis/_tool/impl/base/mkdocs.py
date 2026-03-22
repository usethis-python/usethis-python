from __future__ import annotations

from typing import final

from typing_extensions import assert_never, override

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.detect import is_uv_used
from usethis._console import how_print
from usethis._tool.base import Tool
from usethis._tool.impl.spec.mkdocs import MkDocsToolSpec
from usethis._types.backend import BackendEnum


@final
class MkDocsTool(MkDocsToolSpec, Tool):
    @override
    def print_how_to_use(self) -> None:
        backend = get_backend()
        if backend is BackendEnum.uv and is_uv_used():
            how_print("Run 'uv run mkdocs build' to build the documentation.")
            how_print("Run 'uv run mkdocs serve' to serve the documentation locally.")
        elif backend in (BackendEnum.none, BackendEnum.uv):
            how_print("Run 'mkdocs build' to build the documentation.")
            how_print("Run 'mkdocs serve' to serve the documentation locally.")
        else:
            assert_never(backend)
