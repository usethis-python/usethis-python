from usethis._console import tick_print
from usethis._integrations.pyproject.core import (
    append_config_list,
    get_config_value,
    remove_from_config_list,
)


def select_ruff_rules(rules: list[str]) -> None:
    """Add Ruff rules to the project."""
    rules = sorted(set(rules) - set(get_ruff_rules()))

    if not rules:
        return

    rules_str = ", ".join([f"'{rule}'" for rule in rules])
    s = "" if len(rules) == 1 else "s"
    tick_print(f"Enabling Ruff rule{s} {rules_str} in 'pyproject.toml'.")

    append_config_list(["tool", "ruff", "lint", "select"], rules)


def ignore_ruff_rules(rules: list[str]) -> None:
    """Ignore Ruff rules in the project."""
    rules = sorted(set(rules) - set(get_ignored_ruff_rules()))

    if not rules:
        return

    rules_str = ", ".join([f"'{rule}'" for rule in rules])
    s = "" if len(rules) == 1 else "s"
    tick_print(f"Ignoring Ruff rule{s} {rules_str} in 'pyproject.toml'.")

    append_config_list(["tool", "ruff", "lint", "ignore"], rules)


def deselect_ruff_rules(rules: list[str]) -> None:
    """Ensure Ruff rules are not selected in the project."""
    rules = list(set(rules) & set(get_ruff_rules()))

    if not rules:
        return

    rules_str = ", ".join([f"'{rule}'" for rule in rules])
    s = "" if len(rules) == 1 else "s"
    tick_print(f"Disabling Ruff rule{s} {rules_str} in 'pyproject.toml'.")

    remove_from_config_list(["tool", "ruff", "lint", "select"], rules)


def get_ruff_rules() -> list[str]:
    """Get the Ruff rules selected in the project."""
    try:
        rules: list[str] = get_config_value(["tool", "ruff", "lint", "select"])
    except KeyError:
        rules = []

    return rules


def get_ignored_ruff_rules() -> list[str]:
    """Get the Ruff rules ignored in the project."""
    try:
        rules: list[str] = get_config_value(["tool", "ruff", "lint", "ignore"])
    except KeyError:
        rules = []

    return rules
