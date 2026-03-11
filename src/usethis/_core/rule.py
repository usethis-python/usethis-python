from pydantic import BaseModel

from usethis._core.tool import use_deptry, use_ruff
from usethis._tool.impl.deptry import DeptryTool
from usethis._tool.impl.ruff import RuffTool


class RulesMapping(BaseModel):
    ruff_rules: list[str]
    deptry_rules: list[str]


def select_rules(rules: list[str]) -> None:
    rules_mapping = get_rules_mapping(rules)

    if rules_mapping.deptry_rules and not DeptryTool().is_used():
        use_deptry()
    if rules_mapping.ruff_rules and not RuffTool().is_used():
        use_ruff()

    _ = DeptryTool().select_rules(rules_mapping.deptry_rules)
    _ = RuffTool().select_rules(rules_mapping.ruff_rules)


def deselect_rules(rules: list[str]) -> None:
    rules_mapping = get_rules_mapping(rules)

    _ = DeptryTool().deselect_rules(rules_mapping.deptry_rules)
    _ = RuffTool().deselect_rules(rules_mapping.ruff_rules)


def ignore_rules(rules: list[str]) -> None:
    rules_mapping = get_rules_mapping(rules)

    _ = DeptryTool().ignore_rules(rules_mapping.deptry_rules)
    _ = RuffTool().ignore_rules(rules_mapping.ruff_rules)


def unignore_rules(rules: list[str]) -> None:
    rules_mapping = get_rules_mapping(rules)

    _ = DeptryTool().unignore_rules(rules_mapping.deptry_rules)
    _ = RuffTool().unignore_rules(rules_mapping.ruff_rules)


def get_rules_mapping(rules: list[str]) -> RulesMapping:
    deptry_rules = [rule for rule in rules if rule.startswith("DEP")]
    ruff_rules = [rule for rule in rules if rule not in deptry_rules]

    return RulesMapping(ruff_rules=ruff_rules, deptry_rules=deptry_rules)
