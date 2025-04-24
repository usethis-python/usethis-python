from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, Field

Rule: TypeAlias = str


class RuleConfig(BaseModel):
    """Configuration for linter rules associated with a tool.

    There is a distinction between selected and ignored rules. Selected rules are those
    which are enabled and will be run by the tool unless ignored. Ignored rules are
    those which are not run by the tool, even if they are selected. This follows the
    Ruff paradigm.

    There is also a distinction between managed and unmanaged rule config. Managed
    selections (and ignores) are those which are managed exclusively by the one tool,
    and so can be safely removed if the tool is removed. Unmanaged selections
    (and ignores) are those which are shared with other tools, and so they should only
    be added, never removed.

    Attributes:
        selected: Managed selected rules.
        ignored: Managed ignored rules.
        unmanaged_selected: Unmanaged selected rules.
        unmanaged_ignored: Unmanaged ignored rules.
    """

    selected: list[Rule] = Field(default_factory=list)
    ignored: list[Rule] = Field(default_factory=list)
    unmanaged_selected: list[Rule] = Field(default_factory=list)
    unmanaged_ignored: list[Rule] = Field(default_factory=list)

    def get_all_selected(self) -> list[Rule]:
        """Get all selected rules."""
        return self.selected + self.unmanaged_selected

    def get_all_ignored(self) -> list[Rule]:
        """Get all ignored rules."""
        return self.ignored + self.unmanaged_ignored
