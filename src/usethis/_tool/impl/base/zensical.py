"""Zensical tool implementation."""

from __future__ import annotations

from typing import final

from typing_extensions import assert_never, override

from usethis._backend.dispatch import get_backend
from usethis._backend.poetry.detect import is_poetry_used
from usethis._backend.uv.detect import is_uv_used
from usethis._console import how_print
from usethis._tool.base import Tool
from usethis._tool.impl.spec.zensical import ZensicalToolSpec
from usethis._types.backend import BackendEnum


@final
class ZensicalTool(ZensicalToolSpec, Tool):
    @override
    def print_how_to_use(self) -> None:
        backend = get_backend()
        if backend is BackendEnum.uv and is_uv_used():
            how_print("Run 'uv run zensical build' to build the documentation.")
            how_print("Run 'uv run zensical serve' to serve the documentation locally.")
        elif backend is BackendEnum.poetry and is_poetry_used():
            how_print("Run 'poetry run zensical build' to build the documentation.")
            how_print(
                "Run 'poetry run zensical serve' to serve the documentation locally."
            )
        elif backend in (BackendEnum.none, BackendEnum.uv, BackendEnum.poetry):
            how_print("Run 'zensical build' to build the documentation.")
            how_print("Run 'zensical serve' to serve the documentation locally.")
        else:
            assert_never(backend)
