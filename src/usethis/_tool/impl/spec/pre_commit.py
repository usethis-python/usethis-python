from __future__ import annotations

from pathlib import Path
from typing import final

from typing_extensions import assert_never, override

from usethis._backend.dispatch import get_backend
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._integrations.pre_commit.cmd_ import pre_commit_raw_cmd
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency
from usethis._versions import FALLBACK_SYNC_WITH_UV_VERSION


class PreCommitToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="pre-commit",
            url="https://github.com/pre-commit/pre-commit",
            managed_files=[Path(".pre-commit-config.yaml")],
        )

    @override
    @final
    def raw_cmd(self) -> str:
        return pre_commit_raw_cmd

    @override
    @final
    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="pre-commit")]

    @override
    @final
    def pre_commit_config(self) -> PreCommitConfig:
        """Get the pre-commit configurations for the tool."""
        backend = get_backend()

        if backend is BackendEnum.uv:
            return PreCommitConfig.from_single_repo(
                pre_commit_schema.UriRepo(
                    repo="https://github.com/tsvikas/sync-with-uv",
                    rev=FALLBACK_SYNC_WITH_UV_VERSION,
                    hooks=[pre_commit_schema.HookDefinition(id="sync-with-uv")],
                ),
                requires_venv=False,
                inform_how_to_use_on_migrate=False,
            )
        elif backend is BackendEnum.none:
            return super().pre_commit_config()
        else:
            assert_never(backend)
