from usethis._console import console
from usethis._integrations.pyproject.core import (
    append_config_list,
    get_config_value,
    remove_from_config_list,
)


def select_ruff_rules(rules: list[str]) -> None:
    """Add ruff rules to the project."""
    rules = sorted(set(rules) - set(get_ruff_rules()))

    if not rules:
        return

    rules_str = ", ".join([f"'{rule}'" for rule in rules])
    s = "" if len(rules) == 1 else "s"
    console.tick_print(f"Enabling ruff rule{s} {rules_str} in 'pyproject.toml'.")

    append_config_list(["tool", "ruff", "lint", "select"], rules)


def deselect_ruff_rules(rules: list[str]) -> None:
    """Ensure ruff rules are not selected in the project."""

    rules = list(set(rules) & set(get_ruff_rules()))

    if not rules:
        return

    rules_str = ", ".join([f"'{rule}'" for rule in rules])
    s = "" if len(rules) == 1 else "s"
    console.tick_print(f"Disabling ruff rule{s} {rules_str} in 'pyproject.toml'.")

    remove_from_config_list(["tool", "ruff", "lint", "select"], rules)


def get_ruff_rules() -> list[str]:
    """Get the ruff rules selected in the project."""

    try:
        rules: list[str] = get_config_value(["tool", "ruff", "lint", "select"])
    except KeyError:
        rules = []

    return rules
