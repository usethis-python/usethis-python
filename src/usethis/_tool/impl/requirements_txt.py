from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._config import usethis_config
from usethis._console import how_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.pre_commit.language import get_system_language
from usethis._integrations.pre_commit.schema import HookDefinition, LocalRepo
from usethis._tool.base import Tool
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum

if TYPE_CHECKING:
    from usethis._integrations.backend.uv.deps import (
        Dependency,
    )


class RequirementsTxtTool(Tool):
    # https://pip.pypa.io/en/stable/reference/requirements-file-format/

    @property
    def name(self) -> str:
        return "requirements.txt"

    def print_how_to_use(self) -> None:
        install_method = self.get_install_method()
        backend = get_backend()
        if install_method == "pre-commit":
            if backend is BackendEnum.uv:
                how_print(
                    "Run 'uv run pre-commit run uv-export' to write 'requirements.txt'."
                )
            elif backend is BackendEnum.none:
                how_print("Run 'pre-commit run uv-export' to write 'requirements.txt'.")
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

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return []

    def get_managed_files(self) -> list[Path]:
        return [Path("requirements.txt")]

    def get_pre_commit_config(self) -> PreCommitConfig:
        backend = get_backend()

        if backend is BackendEnum.uv:
            return PreCommitConfig.from_single_repo(
                LocalRepo(
                    repo="local",
                    hooks=[
                        HookDefinition(
                            id="uv-export",
                            name="uv-export",
                            files="^uv\\.lock$",
                            pass_filenames=False,
                            entry="uv export --frozen --offline --quiet -o=requirements.txt",
                            language=get_system_language(),
                            require_serial=True,
                        )
                    ],
                ),
                requires_venv=True,
            )
        elif backend is BackendEnum.none:
            # Need a backend to generate requirements.txt files
            return PreCommitConfig(repo_configs=[], inform_how_to_use_on_migrate=False)
        else:
            assert_never(backend)
