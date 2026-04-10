"""deptry tool specification."""

from __future__ import annotations

from pathlib import Path
from typing import final

from typing_extensions import override

from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.project.layout import get_source_dir_str
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.deps import Dependency


class DeptryToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="deptry",
            url="https://github.com/osprey-oss/deptry",
        )

    @override
    @final
    def raw_cmd(self) -> str:
        _dir = get_source_dir_str()
        return f"deptry {_dir}"

    @override
    @final
    def deps_by_group(
        self, *, unconditional: bool = False
    ) -> dict[str, list[Dependency]]:
        return {"dev": [Dependency(name="deptry")]}

    @override
    @final
    def pre_commit_config(self) -> PreCommitConfig:
        _dir = get_source_dir_str()
        return PreCommitConfig.from_system_hook(
            hook_id="deptry",
            entry=f"deptry {_dir}",
        )

    @override
    @final
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
