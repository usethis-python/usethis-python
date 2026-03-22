from __future__ import annotations

from pathlib import Path
from typing import final

from typing_extensions import assert_never, override

from usethis._backend.dispatch import get_backend
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._integrations.pre_commit.language import get_system_language
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum


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
                pre_commit_schema.LocalRepo(
                    repo="local",
                    hooks=[
                        pre_commit_schema.HookDefinition(
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
