from __future__ import annotations

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.detect import is_uv_used
from usethis._console import how_print
from usethis._tool.base import Tool
from usethis._tool.impl.spec.coverage_py import CoveragePyToolSpec
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency


class CoveragePyTool(CoveragePyToolSpec, Tool):
    def test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        from usethis._tool.impl.base.pytest import (  # to avoid circularity;  # noqa: PLC0415
            PytestTool,
        )

        deps = [Dependency(name="coverage", extras=frozenset({"toml"}))]
        if unconditional or PytestTool().is_used():
            deps += [Dependency(name="pytest-cov")]
        return deps

    def print_how_to_use(self) -> None:
        from usethis._tool.impl.base.pytest import (  # to avoid circularity;  # noqa: PLC0415
            PytestTool,
        )

        backend = get_backend()

        if PytestTool().is_used():
            if backend is BackendEnum.uv and is_uv_used():
                how_print(
                    f"Run 'uv run pytest --cov' to run your tests with {self.name}."
                )
            elif backend in (BackendEnum.none, BackendEnum.uv):
                how_print(f"Run 'pytest --cov' to run your tests with {self.name}.")
            else:
                assert_never(backend)
        elif backend is BackendEnum.uv and is_uv_used():
            how_print(
                f"Run 'uv run coverage help' to see available {self.name} commands."
            )
        elif backend in (BackendEnum.none, BackendEnum.uv):
            how_print(f"Run 'coverage help' to see available {self.name} commands.")
        else:
            assert_never(backend)
