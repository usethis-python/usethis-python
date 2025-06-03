from usethis._config import (
    frozen_opt,
    how_opt,
    offline_opt,
    quiet_opt,
    remove_opt,
    usethis_config,
)
from usethis._config_file import files_manager
from usethis._core.tool import use_pyproject_fmt, use_ruff


def format_(
    remove: bool = remove_opt,
    how: bool = how_opt,
    offline: bool = offline_opt,
    quiet: bool = quiet_opt,
    frozen: bool = frozen_opt,
) -> None:
    """Add recommended formatters to the project."""
    with (
        usethis_config.set(offline=offline, quiet=quiet, frozen=frozen),
        files_manager(),
    ):
        use_ruff(linter=False, formatter=True, remove=remove, how=how)
        use_pyproject_fmt(remove=remove, how=how)
