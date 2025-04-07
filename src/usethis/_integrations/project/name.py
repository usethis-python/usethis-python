from usethis._integrations.file.dir import get_project_name_from_dir
from usethis._integrations.file.pyproject_toml.errors import (
    PyprojectTOMLProjectNameError,
)
from usethis._integrations.file.pyproject_toml.name import get_name


def get_project_name() -> str:
    """The project name, from pyproject.toml if available or fallback to dir name."""
    try:
        return get_name()
    except PyprojectTOMLProjectNameError:
        return get_project_name_from_dir()
