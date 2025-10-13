from __future__ import annotations

from pathlib import Path

from typing_extensions import assert_never

from usethis._config import usethis_config
from usethis._console import box_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.backend.uv.used import is_uv_used
from usethis._integrations.ci.bitbucket.anchor import (
    ScriptItemAnchor as BitbucketScriptItemAnchor,
)
from usethis._integrations.ci.bitbucket.schema import Script as BitbucketScript
from usethis._integrations.ci.bitbucket.schema import Step as BitbucketStep
from usethis._integrations.pre_commit.schema import HookDefinition, UriRepo
from usethis._tool.base import Tool
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency

_SYNC_WITH_UV_VERSION = "v0.4.0"  # Manually bump this version when necessary


class PreCommitTool(Tool):
    # https://github.com/pre-commit/pre-commit
    @property
    def name(self) -> str:
        return "pre-commit"

    def get_pre_commit_config(self) -> PreCommitConfig:
        """Get the pre-commit configurations for the tool."""
        backend = get_backend()

        if backend is BackendEnum.uv:
            return PreCommitConfig.from_single_repo(
                UriRepo(
                    repo="https://github.com/tsvikas/sync-with-uv",
                    rev=_SYNC_WITH_UV_VERSION,
                    hooks=[HookDefinition(id="sync-with-uv")],
                ),
                requires_venv=False,
                inform_how_to_use_on_migrate=False,
            )
        elif backend is BackendEnum.none:
            return super().get_pre_commit_config()
        else:
            assert_never(backend)

    def is_used(self) -> bool:
        if usethis_config.disable_pre_commit:
            return False
        return super().is_used()

    def print_how_to_use(self) -> None:
        backend = get_backend()
        if backend is BackendEnum.uv and is_uv_used():
            box_print(
                "Run 'uv run pre-commit run --all-files' to run the hooks manually."
            )
        else:
            assert backend in (BackendEnum.none, BackendEnum.uv)
            box_print("Run 'pre-commit run --all-files' to run the hooks manually.")

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="pre-commit")]

    def get_managed_files(self) -> list[Path]:
        return [Path(".pre-commit-config.yaml")]

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        backend = get_backend()

        if backend is BackendEnum.uv:
            return [
                BitbucketStep(
                    name=f"Run {self.name}",
                    caches=["uv", "pre-commit"],
                    script=BitbucketScript(
                        [
                            BitbucketScriptItemAnchor(name="install-uv"),
                            "uv run pre-commit run --all-files",
                        ]
                    ),
                )
            ]
        elif backend is BackendEnum.none:
            return [
                BitbucketStep(
                    name=f"Run {self.name}",
                    script=BitbucketScript(
                        [
                            BitbucketScriptItemAnchor(name="ensure-venv"),
                            "pre-commit run --all-files",
                        ]
                    ),
                )
            ]
        else:
            assert_never(backend)

    def migrate_config_to_pre_commit(self) -> None:
        pass

    def migrate_config_from_pre_commit(self) -> None:
        pass
