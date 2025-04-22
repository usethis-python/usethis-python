from pydantic import BaseModel

from usethis._core.tool import use_deptry, use_ruff
from usethis._tool import DeptryTool, RuffTool


class RulesMapping(BaseModel):
    ruff_rules: list[str]
    deptry_rules: list[str]


def use_rules(rules: list[str]) -> None:
    rules_mapping = get_rules_mapping(rules)

    if rules_mapping.deptry_rules and not DeptryTool().is_used():
        use_deptry()
    if rules_mapping.ruff_rules and not RuffTool().is_used():
        use_ruff()

    DeptryTool().select_rules(rules_mapping.deptry_rules)
    RuffTool().select_rules(rules_mapping.ruff_rules)


def remove_rules(rules: list[str]) -> None:
    rules_mapping = get_rules_mapping(rules)

    DeptryTool().deselect_rules(rules_mapping.deptry_rules)
    RuffTool().deselect_rules(rules_mapping.ruff_rules)


def get_rules_mapping(rules: list[str]) -> RulesMapping:
    deptry_rules = [rule for rule in rules if rule.startswith("DEP")]
    ruff_rules = [rule for rule in rules if rule not in deptry_rules]

    return RulesMapping(ruff_rules=ruff_rules, deptry_rules=deptry_rules)
