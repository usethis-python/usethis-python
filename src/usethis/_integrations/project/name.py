from usethis._integrations.file.dir import get_project_name_from_dir
from usethis._integrations.file.pyproject_toml.errors import (
    PyprojectTOMLProjectSectionError,
)
from usethis._integrations.file.pyproject_toml.name import get_name
from usethis._integrations.project.packages import get_importable_packages


def get_project_name() -> str:
    """The project name, from pyproject.toml if available or fallback to heuristics."""
    try:
        return get_name()
    except (PyprojectTOMLProjectSectionError, FileNotFoundError):
        packages = get_importable_packages()
        if len(packages) == 1:
            (package,) = packages
            return package
        else:
            return get_project_name_from_dir()
