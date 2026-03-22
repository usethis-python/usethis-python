from __future__ import annotations

from typing import final

from typing_extensions import assert_never, override

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.detect import is_uv_used
from usethis._console import how_print
from usethis._tool.base import Tool
from usethis._tool.heuristics import is_likely_used
from usethis._tool.impl.spec.coverage_py import CoveragePyToolSpec
from usethis._tool.impl.spec.pytest import PytestToolSpec
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency


@final
class CoveragePyTool(CoveragePyToolSpec, Tool):
    @override
    def test_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        deps = [Dependency(name="coverage", extras=frozenset({"toml"}))]
        if unconditional or is_likely_used(PytestToolSpec()):
            deps += [Dependency(name="pytest-cov")]
        return deps

    @override
    def print_how_to_use(self) -> None:
        backend = get_backend()

        if is_likely_used(PytestToolSpec()):
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
