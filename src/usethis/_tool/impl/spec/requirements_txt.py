"""requirements.txt tool specification."""

from __future__ import annotations

from pathlib import Path
from typing import final

from typing_extensions import assert_never, override

from usethis._backend.dispatch import get_backend
from usethis._fallback import FALLBACK_UV_VERSION
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum

_UV_PRE_COMMIT_REPO = "https://github.com/astral-sh/uv-pre-commit"


class RequirementsTxtToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="requirements.txt",
            url="https://pip.pypa.io/en/stable/reference/requirements-file-format/",
            managed_files=[Path("requirements.txt")],
        )

    @override
    @final
    def pre_commit_config(self) -> PreCommitConfig:
        backend = get_backend()

        if backend is BackendEnum.uv:
            return PreCommitConfig.from_single_repo(
                pre_commit_schema.UriRepo(
                    repo=_UV_PRE_COMMIT_REPO,
                    rev=FALLBACK_UV_VERSION,
                    hooks=[
                        pre_commit_schema.HookDefinition(
                            id="uv-export",
                        )
                    ],
                ),
                requires_venv=False,
            )
        elif backend in (BackendEnum.poetry, BackendEnum.none):
            # Need a backend to generate requirements.txt files
            return PreCommitConfig(repo_configs=[], inform_how_to_use_on_migrate=False)
        else:
            assert_never(backend)

    @override
    @final
    def config_spec(self) -> ConfigSpec:
        backend = get_backend()

        if backend is BackendEnum.uv:
            return ConfigSpec.from_flat(
                file_managers=[PyprojectTOMLManager()],
                resolution="first",
                config_items=[
                    ConfigItem(
                        description="Sync with UV repo-to-package mapping for uv-pre-commit",
                        root={
                            Path("pyproject.toml"): ConfigEntry(
                                keys=[
                                    "tool",
                                    "sync-with-uv",
                                    "repo-to-package",
                                    _UV_PRE_COMMIT_REPO,
                                ],
                                get_value=lambda: "uv",
                            )
                        },
                        managed=False,
                    ),
                ],
            )
        elif backend in (BackendEnum.poetry, BackendEnum.none):
            return ConfigSpec.empty()
        else:
            assert_never(backend)
