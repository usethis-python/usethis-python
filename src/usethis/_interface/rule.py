import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._config_file import files_manager
from usethis._core.rule import (
    deselect_rules,
    ignore_rules,
    select_rules,
    unignore_rules,
)

remove_opt = typer.Option(
    False, "--remove", help="Remove the rule selection or ignore status."
)
ignore_opt = typer.Option(
    False, "--ignore", help="Add (or remove) the rule to (or from) the ignore list"
)


def rule(
    rules: list[str],
    remove: bool = remove_opt,
    ignore: bool = ignore_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        if remove and not ignore:
            deselect_rules(rules)
        elif ignore and not remove:
            ignore_rules(rules)
        elif remove and ignore:
            unignore_rules(rules)
        else:
            select_rules(rules)
