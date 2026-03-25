from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from pydantic import BaseModel, Field
from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Sequence

    from typing_extensions import Self

Rule: TypeAlias = str


def is_rule_covered_by(rule: Rule, parent: Rule) -> bool:
    """Check if a rule is covered (subsumed) by a more general rule.

    A rule is covered if a more general rule would already include it.
    For example, "TC001" is covered by "TC", and any rule is covered by "ALL".

    A rule does not cover itself. "ALL" is never covered by a specific rule.
    """
    if parent == rule:
        return False
    if parent == "ALL":
        return True
    if rule == "ALL":
        return False
    return rule.startswith(parent)


def reconcile_rules(
    existing: Sequence[Rule], incoming: Sequence[Rule]
) -> tuple[list[Rule], list[Rule]]:
    """Determine which rules to add and which existing rules to remove.

    Respects the rule code hierarchy: more general rules subsume more specific
    ones. For example, adding "TC" when "TC001" already exists will replace
    "TC001" with "TC". Adding "TC001" when "TC" already exists is a no-op.

    Returns:
        A tuple of (rules_to_add, rules_to_remove).
    """
    # Filter out incoming rules already covered by existing rules
    incoming_filtered: list[Rule] = []
    for rule in incoming:
        if rule in existing:
            continue
        if any(is_rule_covered_by(rule, e) for e in existing):
            continue
        incoming_filtered.append(rule)

    # Among the filtered incoming rules, remove those covered by other incoming
    incoming_deduped: list[Rule] = []
    for rule in incoming_filtered:
        if any(
            is_rule_covered_by(rule, other)
            for other in incoming_filtered
            if other != rule
        ):
            continue
        if rule not in incoming_deduped:
            incoming_deduped.append(rule)

    # Determine which existing rules are now subsumed by incoming rules
    to_remove: list[Rule] = []
    for existing_rule in existing:
        if any(is_rule_covered_by(existing_rule, new_rule) for new_rule in incoming_deduped):
            to_remove.append(existing_rule)

    return sorted(incoming_deduped), sorted(to_remove)


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
        tests_ignored: Managed cases of rules ignored for specifically the tests
                       directory.
        nontests_ignored: Managed cases of rules ignored for specifically non-test
                          directories (using !tests/**/*.py glob).
        tests_unmanaged_ignored: Unmanaged cases of rules ignored for specifically the
                                 tests directory.
        nontests_unmanaged_ignored: Unmanaged cases of rules ignored for specifically
                                    non-test directories (using !tests/**/*.py glob).
    """

    selected: list[Rule] = Field(default_factory=list)
    ignored: list[Rule] = Field(default_factory=list)
    unmanaged_selected: list[Rule] = Field(default_factory=list)
    unmanaged_ignored: list[Rule] = Field(default_factory=list)
    tests_ignored: list[Rule] = Field(default_factory=list)
    nontests_ignored: list[Rule] = Field(default_factory=list)
    tests_unmanaged_ignored: list[Rule] = Field(default_factory=list)
    nontests_unmanaged_ignored: list[Rule] = Field(default_factory=list)

    def get_all_selected(self) -> list[Rule]:
        """Get all (project-scope) selected rules."""
        return self.selected + self.unmanaged_selected

    def get_all_ignored(self) -> list[Rule]:
        """Get all (project-scope) ignored rules."""
        return self.ignored + self.unmanaged_ignored

    def subset_related_to_tests(self) -> Self:
        """Get a RuleConfig with only rules relating to tests configuration.

        This is useful for cases where we are introducing pytest into a project, and
        then we want to introduce specifically this subset of rules.
        """
        self = self.model_copy()
        self.selected = []
        self.ignored = []
        self.unmanaged_selected = []
        self.unmanaged_ignored = []
        # tests_ignored, nontests_ignored, tests_unmanaged_ignored, and
        # nontests_unmanaged_ignored are preserved because they are per-file-ignores
        # specific to test directories and should not be cleared when removing global
        # rules.
        return self

    @property
    def empty(self) -> bool:
        """Check if the rule config is empty."""
        return (
            not self.selected
            and not self.ignored
            and not self.unmanaged_selected
            and not self.unmanaged_ignored
            and not self.tests_ignored
            and not self.nontests_ignored
            and not self.tests_unmanaged_ignored
            and not self.nontests_unmanaged_ignored
        )

    @property
    def is_related_to_tests(self) -> bool:
        """Check if the rule config has any tests-related rules."""
        return bool(
            self.tests_ignored
            or self.nontests_ignored
            or self.tests_unmanaged_ignored
            or self.nontests_unmanaged_ignored
        )

    @override
    def __repr__(self) -> str:
        """Representation which omits empty-list fields."""
        args: list[str] = []
        if self.selected:
            args.append(f"selected={self.selected}")
        if self.ignored:
            args.append(f"ignored={self.ignored}")
        if self.unmanaged_selected:
            args.append(f"unmanaged_selected={self.unmanaged_selected}")
        if self.unmanaged_ignored:
            args.append(f"unmanaged_ignored={self.unmanaged_ignored}")
        if self.tests_ignored:
            args.append(f"tests_ignored={self.tests_ignored}")
        if self.nontests_ignored:
            args.append(f"nontests_ignored={self.nontests_ignored}")
        if self.tests_unmanaged_ignored:
            args.append(f"tests_unmanaged_ignored={self.tests_unmanaged_ignored}")
        if self.nontests_unmanaged_ignored:
            args.append(f"nontests_unmanaged_ignored={self.nontests_unmanaged_ignored}")
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

        new = self.model_copy()
        new.selected = self.selected + other.selected
        new.ignored = self.ignored + other.ignored
        new.unmanaged_selected = self.unmanaged_selected + other.unmanaged_selected
        new.unmanaged_ignored = self.unmanaged_ignored + other.unmanaged_ignored
        new.tests_ignored = self.tests_ignored + other.tests_ignored
        new.nontests_ignored = self.nontests_ignored + other.nontests_ignored
        new.tests_unmanaged_ignored = (
            self.tests_unmanaged_ignored + other.tests_unmanaged_ignored
        )
        new.nontests_unmanaged_ignored = (
            self.nontests_unmanaged_ignored + other.nontests_unmanaged_ignored
        )
        return new
