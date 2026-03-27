"""Check whether the uv CLI is available."""

from packaging.requirements import InvalidRequirement, Requirement

from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._file.pyproject_toml.errors import PyprojectTOMLError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager


def is_uv_available() -> bool:
    """Check if the `uv` command is available in the current environment."""
    try:
        call_uv_subprocess(["--version"], change_toml=False)
    except UVSubprocessFailedError:
        return _is_uv_a_dep()

    return True


def _is_uv_a_dep() -> bool:
    """Check if uv is declared as a project dependency or in a dependency group."""
    try:
        content = PyprojectTOMLManager().get()
    except (FileNotFoundError, PyprojectTOMLError):
        return False

    # Gather all requirement strings from both sources
    req_strs: list[str] = []

    # Collect from project dependencies
    try:
        project_section = content["project"]
        if isinstance(project_section, dict):
            deps = project_section["dependencies"]
            if isinstance(deps, list):
                req_strs.extend(s for s in deps if isinstance(s, str))
    except (KeyError, TypeError):
        pass

    # Collect from dependency groups
    try:
        groups = content["dependency-groups"]
        if isinstance(groups, dict):
            for group_deps in groups.values():
                if isinstance(group_deps, list):
                    req_strs.extend(s for s in group_deps if isinstance(s, str))
    except (KeyError, TypeError):
        pass

    # Check if any requirement is for 'uv'
    for req_str in req_strs:
        try:
            if Requirement(req_str).name == "uv":
                return True
        except InvalidRequirement:
            continue

    return False
