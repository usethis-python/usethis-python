from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._console import how_print
from usethis._detect.pre_commit import is_pre_commit_used
from usethis._integrations.ci.bitbucket import schema as bitbucket_schema
from usethis._integrations.ci.bitbucket.anchor import (
    ScriptItemAnchor as BitbucketScriptItemAnchor,
)
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._integrations.pre_commit.cmd_ import pre_commit_raw_cmd
from usethis._tool.base import Tool, ToolMeta, ToolSpec
from usethis._tool.deps import DepConfig
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._python.version import PythonVersion

_SYNC_WITH_UV_VERSION = "v0.5.0"  # Manually bump this version when necessary


class PreCommitToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="pre-commit",
            url="https://github.com/pre-commit/pre-commit",
            managed_files=[Path(".pre-commit-config.yaml")],
        )

    def raw_cmd(self) -> str:
        return pre_commit_raw_cmd

    def dep_config(self) -> DepConfig:
        return DepConfig.from_single_dev_dep(Dependency(name="pre-commit"))

    def pre_commit_config(self) -> PreCommitConfig:
        """Get the pre-commit configurations for the tool."""
        backend = get_backend()

        if backend is BackendEnum.uv:
            return PreCommitConfig.from_single_repo(
                pre_commit_schema.UriRepo(
                    repo="https://github.com/tsvikas/sync-with-uv",
                    rev=_SYNC_WITH_UV_VERSION,
                    hooks=[pre_commit_schema.HookDefinition(id="sync-with-uv")],
                ),
                requires_venv=False,
                inform_how_to_use_on_migrate=False,
            )
        elif backend is BackendEnum.none:
            return super().pre_commit_config()
        else:
            assert_never(backend)


class PreCommitTool(PreCommitToolSpec, Tool):
    def is_used(self) -> bool:
        return is_pre_commit_used()

    def print_how_to_use(self) -> None:
        how_print(f"Run '{self.how_to_use_cmd()}' to run the hooks manually.")

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

    def update_bitbucket_steps(self, *, matrix_python: bool = True) -> None:
        """Add Bitbucket steps associated with pre-commit, and remove outdated ones.

        Only runs if Bitbucket is used in the project.

        Args:
            matrix_python: Whether to use a Python version matrix. When False,
                           only the current development version is used.
        """
        self._unconditional_update_bitbucket_steps(matrix_python=matrix_python)

    def migrate_config_to_pre_commit(self) -> None:
        pass

    def migrate_config_from_pre_commit(self) -> None:
        pass
