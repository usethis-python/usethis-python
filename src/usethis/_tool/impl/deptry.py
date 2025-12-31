from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._console import how_print, info_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.backend.uv.used import is_uv_used
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._integrations.pre_commit.language import get_system_language
from usethis._integrations.project.layout import get_source_dir_str
from usethis._tool.base import Tool
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


class DeptryTool(Tool):
    # https://github.com/fpgmaas/deptry
    @property
    def name(self) -> str:
        return "deptry"

    def default_command(self) -> str:
        backend = get_backend()
        _dir = get_source_dir_str()
        if backend is BackendEnum.uv and is_uv_used():
            return f"uv run deptry {_dir}"
        elif backend is BackendEnum.none or backend is BackendEnum.uv:
            return f"deptry {_dir}"
        else:
            assert_never(backend)

    def print_how_to_use(self) -> None:
        _dir = get_source_dir_str()
        install_method = self.get_install_method()
        backend = get_backend()
        if install_method == "pre-commit":
            if backend is BackendEnum.uv and is_uv_used():
                how_print(
                    f"Run 'uv run pre-commit run deptry --all-files' to run {self.name}."
                )
            elif backend in (BackendEnum.none, BackendEnum.uv):
                how_print(
                    f"Run 'pre-commit run deptry --all-files' to run {self.name}."
                )
            else:
                assert_never(backend)
        elif install_method == "devdep" or install_method is None:
            cmd = self.default_command()
            how_print(f"Run '{cmd}' to run deptry.")
        else:
            assert_never(install_method)

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="deptry")]

    def get_config_spec(self) -> ConfigSpec:
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

    def get_pre_commit_config(self) -> PreCommitConfig:
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

    def is_managed_rule(self, rule: Rule) -> bool:
        return rule.startswith("DEP") and rule[3:].isdigit()

    def select_rules(self, rules: list[Rule]) -> bool:
        """Does nothing for deptry - all rules are automatically enabled by default."""
        if rules:
            info_print(f"All {self.name} rules are always implicitly selected.")
        return False

    def get_selected_rules(self) -> list[Rule]:
        """No notion of selection for deptry.

        This doesn't mean rules won't be enabled, it just means we don't keep track
        of selection for them.
        """
        return []

    def deselect_rules(self, rules: list[Rule]) -> bool:
        """Does nothing for deptry - all rules are automatically enabled by default."""
        return False

    def get_ignored_rules(self) -> list[Rule]:
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
