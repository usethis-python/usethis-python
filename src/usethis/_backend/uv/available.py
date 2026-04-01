"""Check whether the uv CLI is available."""

from packaging.requirements import InvalidRequirement

from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._file.pyproject_toml.deps import get_dep_groups, get_project_deps
from usethis._file.pyproject_toml.errors import PyprojectTOMLError
from usethis._types.deps import Dependency


def is_uv_available() -> bool:
    """Check if the `uv` command is available in the current environment."""
    try:
        call_uv_subprocess(["--version"], change_toml=False)
    except UVSubprocessFailedError:
        return _is_uv_a_dep()

    return True


def _is_uv_a_dep() -> bool:
    """Check if uv is declared as a project dependency or in a dependency group."""
    uv_dep = Dependency(name="uv")

    try:
        project_deps = get_project_deps()
    except (PyprojectTOMLError, InvalidRequirement):
        project_deps = []

    try:
        dep_groups = get_dep_groups()
    except (PyprojectTOMLError, InvalidRequirement):
        dep_groups = {}

    all_group_deps = [dep for group in dep_groups.values() for dep in group]
    return any(dep.name == uv_dep.name for dep in project_deps + all_group_deps)
