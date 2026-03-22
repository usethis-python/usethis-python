from __future__ import annotations

from typing import TYPE_CHECKING, final

from pydantic import TypeAdapter, ValidationError

from usethis._console import info_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._tool.base import Tool
from usethis._tool.impl.spec.deptry import DeptryToolSpec
from usethis._tool.rule import Rule

if TYPE_CHECKING:
    from collections.abc import Sequence

    from usethis._io import KeyValueFileManager


@final
class DeptryTool(DeptryToolSpec, Tool):
    def select_rules(self, rules: Sequence[Rule]) -> bool:
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

    def deselect_rules(self, rules: Sequence[Rule]) -> bool:
        """Does nothing for deptry - all rules are automatically enabled by default."""
        return False

    def ignored_rules(self) -> list[Rule]:
        (file_manager,) = self.get_active_config_file_managers()
        keys = self._get_ignore_keys(file_manager)
        try:
            rules = TypeAdapter(list[Rule]).validate_python(file_manager[keys])
        except (KeyError, FileNotFoundError, ValidationError):
            rules: list[Rule] = []

        return rules

    def _get_ignore_keys(self, file_manager: KeyValueFileManager[object]) -> list[str]:
        """Get the keys for the ignored rules in the given file manager."""
        if isinstance(file_manager, PyprojectTOMLManager):
            return ["tool", "deptry", "ignore"]
        else:
            return super()._get_ignore_keys(file_manager)
