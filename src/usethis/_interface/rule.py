import typer

from usethis._config import offline_opt, quiet_opt, usethis_config
from usethis._config_file import files_manager
from usethis._core.rule import remove_rules, use_rules

remove_opt = typer.Option(
    False, "--remove", help="Remove the rule instead of adding it."
)


def rule(
    rules: list[str],
    remove: bool = remove_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
) -> None:
    with usethis_config.set(offline=offline, quiet=quiet), files_manager():
        if not remove:
            use_rules(rules)
        else:
            remove_rules(rules)
