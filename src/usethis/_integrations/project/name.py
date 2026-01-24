from usethis._file.dir import get_project_name_from_dir
from usethis._file.pyproject_toml.errors import (
    PyprojectTOMLProjectSectionError,
)
from usethis._file.pyproject_toml.name import get_name


def get_project_name() -> str:
    """The project name, from pyproject.toml if available or fallback to heuristics."""
    try:
        return get_name()
    except (PyprojectTOMLProjectSectionError, FileNotFoundError):
        return get_project_name_from_dir()
