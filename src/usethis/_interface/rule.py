import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._config_file import files_manager
from usethis._tool import DeptryTool, RuffTool

remove_opt = typer.Option(
    False, "--remove", help="Remove the rule instead of adding it."
)


def rule(
    rules: list[str],
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    # TODO what about when ruff (or the tool) is not actually being used?
    # Do we automatically add the tool?'
    # TODO do we validate the rules being added somehow?

    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        # TODO Rather than doing it this way, let's add an abstraction in the Tool class which
        # which is similar to is_used; but it would be is_own_rule or similar (name is tricky)
        # and it would determine whether a rule belongs to a tool or not.
        # Ruff might have a more sophisticated mechanism than just "everything else"
        # but also I would want to be careful about this because we don't want a maintenance burden.

        # TODO need to be very careful here. In the future, we might want to support multiple tools
        # that provide separate implementations of the same rule codes. For example, flake8 and ruff
        # so how would we know which tool should "own" the rule? Presumably we could use
        # precedence rules, e.g. if both ruff and flake8 are being used then ruff wins. Or
        # we could have an option (~please no~) which tells us which tool to add it to.
        # OR we could throw an error.
        deptry_rules = [rule for rule in rules if rule.startswith("DEP")]
        ruff_rules = [rule for rule in rules if rule not in deptry_rules]

        if not remove:
            DeptryTool().select_rules(deptry_rules)
            RuffTool().select_rules(ruff_rules)
        else:
            DeptryTool().deselect_rules(deptry_rules)
            RuffTool().deselect_rules(ruff_rules)
