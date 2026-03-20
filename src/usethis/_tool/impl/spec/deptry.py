from __future__ import annotations

from pathlib import Path

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._integrations.pre_commit.language import get_system_language
from usethis._integrations.project.layout import get_source_dir_str
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency


class DeptryToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="deptry",
            url="https://github.com/fpgmaas/deptry",
        )

    def raw_cmd(self) -> str:
        _dir = get_source_dir_str()
        return f"deptry {_dir}"

    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="deptry")]

    def pre_commit_config(self) -> PreCommitConfig:
        backend = get_backend()

        _dir = get_source_dir_str()
        if backend is BackendEnum.uv:
            return PreCommitConfig.from_single_repo(
                pre_commit_schema.LocalRepo(
                    repo="local",
                    hooks=[
                        pre_commit_schema.HookDefinition(
                            id="deptry",
                            name="deptry",
                            entry=f"uv run --frozen --offline deptry {_dir}",
                            language=get_system_language(),
                            always_run=True,
                            pass_filenames=False,
                        )
                    ],
                ),
                requires_venv=True,
                inform_how_to_use_on_migrate=False,
            )
        elif backend is BackendEnum.none:
            return PreCommitConfig.from_single_repo(
                pre_commit_schema.LocalRepo(
                    repo="local",
                    hooks=[
                        pre_commit_schema.HookDefinition(
                            id="deptry",
                            name="deptry",
                            entry=f"deptry {_dir}",
                            language=get_system_language(),
                            always_run=True,
                            pass_filenames=False,
                        )
                    ],
                ),
                requires_venv=True,
                inform_how_to_use_on_migrate=False,
            )
        else:
            assert_never(backend)

    def config_spec(self) -> ConfigSpec:
        # https://deptry.com/usage/#configuration
        return ConfigSpec.from_flat(
            file_managers=[PyprojectTOMLManager()],
            resolution="first",
            config_items=[
                ConfigItem(
                    description="Overall config",
                    root={Path("pyproject.toml"): ConfigEntry(keys=["tool", "deptry"])},
                ),
                ConfigItem(
                    description="Ignore notebooks",
                    root={
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "deptry", "ignore_notebooks"],
                            get_value=lambda: False,
                        )
                    },
                ),
            ],
        )
