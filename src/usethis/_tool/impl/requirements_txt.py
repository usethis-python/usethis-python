from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from usethis._console import box_print
from usethis._integrations.pre_commit.schema import (
    HookDefinition,
    Language,
    LocalRepo,
    UriRepo,
)
from usethis._integrations.uv.used import is_uv_used
from usethis._tool.base import Tool
from usethis._tool.impl.pre_commit import PreCommitTool

if TYPE_CHECKING:
    from usethis._integrations.uv.deps import (
        Dependency,
    )


class RequirementsTxtTool(Tool):
    # https://pip.pypa.io/en/stable/reference/requirements-file-format/

    @property
    def name(self) -> str:
        return "requirements.txt"

    def print_how_to_use(self) -> None:
        if PreCommitTool().is_used():
            if is_uv_used():
                box_print(
                    "Run 'uv run pre-commit run uv-export' to write 'requirements.txt'."
                )
            else:
                box_print("Run 'pre-commit run uv-export' to write 'requirements.txt'.")
        else:
            if not is_uv_used():
                # This is a very crude approach as a temporary measure.
                box_print("Install uv to use 'uv export'.")

            box_print(
                "Run 'uv export --no-dev -o=requirements.txt' to write 'requirements.txt'."
            )

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return []

    def get_managed_files(self) -> list[Path]:
        return [Path("requirements.txt")]

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        return [
            LocalRepo(
                repo="local",
                hooks=[
                    HookDefinition(
                        id="uv-export",
                        name="uv-export",
                        files="^uv\\.lock$",
                        pass_filenames=False,
                        entry="uv export --frozen --offline --quiet --no-dev -o=requirements.txt",
                        language=Language("system"),
                        require_serial=True,
                    )
                ],
            )
        ]
