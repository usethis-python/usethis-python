from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from typing_extensions import Self

Rule: TypeAlias = str


class RuleConfig(BaseModel):
    """Configuration for linter rules associated with a tool.

    There is a distinction between selected and ignored rules. Selected rules are those
    which are enabled for the tool and will be used unless ignored. Ignored rules are
    those which are not run, even if they are selected. This follows the Ruff paradigm.

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
        tests_unmanaged_ignored: Unmanaged cases of rules ignored for specifically the
                                 tests directory.
    """

    selected: list[Rule] = Field(default_factory=list)
    ignored: list[Rule] = Field(default_factory=list)
    unmanaged_selected: list[Rule] = Field(default_factory=list)
    unmanaged_ignored: list[Rule] = Field(default_factory=list)
    tests_unmanaged_ignored: list[Rule] = Field(default_factory=list)

    def get_all_selected(self) -> list[Rule]:
        """Get all (project-scope) selected rules."""
        return self.selected + self.unmanaged_selected

    def get_all_ignored(self) -> list[Rule]:
        """Get all (project-scope) ignored rules."""
        return self.ignored + self.unmanaged_ignored

    @property
    def empty(self) -> bool:
        """Check if the rule config is empty."""
        return (
            not self.selected
            and not self.ignored
            and not self.unmanaged_selected
            and not self.unmanaged_ignored
            and not self.tests_unmanaged_ignored
        )

    def __repr__(self) -> str:
        """Representation which omits empty-list fields."""
        args = []
        if self.selected:
            args.append(f"selected={self.selected}")
        if self.ignored:
            args.append(f"ignored={self.ignored}")
        if self.unmanaged_selected:
            args.append(f"unmanaged_selected={self.unmanaged_selected}")
        if self.unmanaged_ignored:
            args.append(f"unmanaged_ignored={self.unmanaged_ignored}")
        if self.tests_unmanaged_ignored:
            args.append(f"tests_unmanaged_ignored={self.tests_unmanaged_ignored}")
        arg_str = ", ".join(args)
        return f"RuleConfig({arg_str})"

    def __or__(self, other: Self) -> Self:
        """Merge multiple rule configs together.

        Examples:
            >>> RuleConfig(selected=["A"]) | RuleConfig(selected=["B"])
            RuleConfig(selected=['A', 'B'])
            >>> RuleConfig(selected=["A"]) | RuleConfig(ignored=["B"])
            RuleConfig(selected=['A'], ignored=['B'])
        """
        if not isinstance(other, self.__class__):
            msg = (
                f"Cannot merge '{self.__class__.__name__}' with "
                f"'{other.__class__.__name__}'."
            )
            raise NotImplementedError(msg)

        return type(self)(
            selected=self.selected + other.selected,
            ignored=self.ignored + other.ignored,
            unmanaged_selected=self.unmanaged_selected + other.unmanaged_selected,
            unmanaged_ignored=self.unmanaged_ignored + other.unmanaged_ignored,
            tests_unmanaged_ignored=self.tests_unmanaged_ignored
            + other.tests_unmanaged_ignored,
        )
