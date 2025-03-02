from pathlib import Path

from usethis._console import tick_print
from usethis._integrations.pyproject_toml.io_ import PyprojectTOMLManager


def remove_pyproject_toml() -> None:
    path = Path.cwd() / "pyproject.toml"
    if path.exists() and path.is_file():
        tick_print("Removing 'pyproject.toml' file")
        PyprojectTOMLManager().write_file()
        PyprojectTOMLManager().unlock()
        path.unlink()
