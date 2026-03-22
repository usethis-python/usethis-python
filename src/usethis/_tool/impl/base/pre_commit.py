from __future__ import annotations

from typing import TYPE_CHECKING, final

from typing_extensions import assert_never, override

from usethis._backend.dispatch import get_backend
from usethis._console import how_print
from usethis._detect.pre_commit import is_pre_commit_used
from usethis._integrations.ci.bitbucket import schema as bitbucket_schema
from usethis._integrations.ci.bitbucket.anchor import (
    ScriptItemAnchor as BitbucketScriptItemAnchor,
)
from usethis._tool.base import Tool
from usethis._tool.impl.spec.pre_commit import PreCommitToolSpec
from usethis._types.backend import BackendEnum

if TYPE_CHECKING:
    from usethis._python.version import PythonVersion


@final
class PreCommitTool(PreCommitToolSpec, Tool):
    @override
    def is_used(self) -> bool:
        return is_pre_commit_used()

    @override
    def print_how_to_use(self) -> None:
        how_print(f"Run '{self.how_to_use_cmd()}' to run the hooks manually.")

    @override
    def get_bitbucket_steps(
        self,
        *,
        matrix_python: bool = True,
        versions: list[PythonVersion] | None = None,
    ) -> list[bitbucket_schema.Step]:
        backend = get_backend()

        if backend is BackendEnum.uv:
            return [
                bitbucket_schema.Step(
                    name=f"Run {self.name}",
                    caches=["uv", "pre-commit"],
                    script=bitbucket_schema.Script(
                        [
                            BitbucketScriptItemAnchor(name="install-uv"),
                            "uv run pre-commit run -a",
                        ]
                    ),
                )
            ]
        elif backend is BackendEnum.none:
            return [
                bitbucket_schema.Step(
                    name=f"Run {self.name}",
                    caches=["pre-commit"],
                    script=bitbucket_schema.Script(
                        [
                            BitbucketScriptItemAnchor(name="ensure-venv"),
                            "pre-commit run -a",
                        ]
                    ),
                )
            ]
        else:
            assert_never(backend)

    @override
    def update_bitbucket_steps(self, *, matrix_python: bool = True) -> None:
        """Add Bitbucket steps associated with pre-commit, and remove outdated ones.

        Only runs if Bitbucket is used in the project.

        Args:
            matrix_python: Whether to use a Python version matrix. When False,
                           only the current development version is used.
        """
        self.unconditional_update_bitbucket_steps(matrix_python=matrix_python)

    @override
    def migrate_config_to_pre_commit(self) -> None:
        pass

    @override
    def migrate_config_from_pre_commit(self) -> None:
        pass
