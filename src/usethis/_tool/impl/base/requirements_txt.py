from __future__ import annotations

from typing import final

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._config import usethis_config
from usethis._console import how_print
from usethis._tool.base import Tool
from usethis._tool.impl.spec.requirements_txt import RequirementsTxtToolSpec
from usethis._types.backend import BackendEnum


@final
class RequirementsTxtTool(RequirementsTxtToolSpec, Tool):
    def print_how_to_use(self) -> None:
        install_method = self.get_install_method()
        backend = get_backend()
        if install_method == "pre-commit":
            if backend is BackendEnum.uv:
                how_print(
                    "Run 'uv run pre-commit run -a uv-export' to write 'requirements.txt'."
                )
            elif backend is BackendEnum.none:
                how_print(
                    "Run 'pre-commit run -a uv-export' to write 'requirements.txt'."
                )
            else:
                assert_never(backend)
        elif install_method == "devdep" or install_method is None:
            if backend is BackendEnum.uv:
                how_print(
                    "Run 'uv export -o=requirements.txt' to write 'requirements.txt'."
                )
            elif backend is BackendEnum.none:
                if not (usethis_config.cpd() / "requirements.txt").exists():
                    how_print(
                        "Run 'usethis tool requirements.txt' to write 'requirements.txt'."
                    )
            else:
                assert_never(backend)
        else:
            assert_never(install_method)
