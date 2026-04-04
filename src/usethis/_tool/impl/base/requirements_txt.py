"""requirements.txt tool implementation."""

from __future__ import annotations

from typing import final

from typing_extensions import assert_never, override

from usethis._backend.dispatch import get_backend
from usethis._config import usethis_config
from usethis._console import how_print
from usethis._tool.base import Tool
from usethis._tool.impl.spec.requirements_txt import RequirementsTxtToolSpec
from usethis._types.backend import BackendEnum


@final
class RequirementsTxtTool(RequirementsTxtToolSpec, Tool):
    @override
    def print_how_to_use(self) -> None:
        install_method = self.get_install_method()
        backend = get_backend()
        name = self._output_file
        if install_method == "pre-commit":
            if backend is BackendEnum.uv:
                how_print(
                    f"Run 'uv run pre-commit run -a uv-export' to write '{name}'."
                )
            elif backend in (BackendEnum.poetry, BackendEnum.none):
                how_print(f"Run 'pre-commit run -a uv-export' to write '{name}'.")
            else:
                assert_never(backend)
        elif install_method == "devdep" or install_method is None:
            if backend is BackendEnum.uv:
                how_print(f"Run 'uv export -o={name}' to write '{name}'.")
            elif backend in (BackendEnum.poetry, BackendEnum.none):
                if not (usethis_config.cpd() / name).exists():
                    how_print(f"Run 'usethis tool requirements.txt' to write '{name}'.")
            else:
                assert_never(backend)
        else:
            assert_never(install_method)
