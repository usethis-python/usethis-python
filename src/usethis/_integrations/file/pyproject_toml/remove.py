from __future__ import annotations

from usethis._config import usethis_config
from usethis._console import tick_print
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager


def remove_pyproject_toml() -> None:
    path = usethis_config.cpd() / "pyproject.toml"
    if path.exists() and path.is_file():
        tick_print("Removing 'pyproject.toml' file")
        PyprojectTOMLManager().write_file()
        PyprojectTOMLManager().unlock()
        path.unlink()
