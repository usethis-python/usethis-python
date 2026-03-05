from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._console import info_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._integrations.pre_commit.language import get_system_language
from usethis._integrations.project.layout import get_source_dir_str
from usethis._tool.base import Tool, ToolMeta, ToolSpec
from usethis._tool.config import (
    ConfigEntry,
    ConfigItem,
    ConfigSpec,
)
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager
    from usethis._tool.rule import Rule


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


class DeptryTool(DeptryToolSpec, Tool):
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

    def select_rules(self, rules: list[Rule]) -> bool:
        """Does nothing for deptry - all rules are automatically enabled by default."""
        if rules:
            info_print(f"All {self.name} rules are always implicitly selected.")
        return False

    def selected_rules(self) -> list[Rule]:
        """No notion of selection for deptry.

        This doesn't mean rules won't be enabled, it just means we don't keep track
        of selection for them.
        """
        return []

    def deselect_rules(self, rules: list[Rule]) -> bool:
        """Does nothing for deptry - all rules are automatically enabled by default."""
        return False

    def ignored_rules(self) -> list[Rule]:
        (file_manager,) = self.get_active_config_file_managers()
        keys = self._get_ignore_keys(file_manager)
        try:
            rules: list[Rule] = file_manager[keys]
        except (KeyError, FileNotFoundError):
            rules = []

        return rules

    def _get_ignore_keys(self, file_manager: KeyValueFileManager) -> list[str]:
        """Get the keys for the ignored rules in the given file manager."""
        if isinstance(file_manager, PyprojectTOMLManager):
            return ["tool", "deptry", "ignore"]
        else:
            return super()._get_ignore_keys(file_manager)
