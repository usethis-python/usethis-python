import re

from packaging.requirements import Requirement
from pydantic import TypeAdapter

from usethis._config import usethis_config
from usethis._console import tick_print
from usethis._integrations.pyproject.io import read_pyproject_toml
from usethis._integrations.uv.call import call_uv_subprocess
from usethis._integrations.uv.errors import UVDepGroupError, UVSubprocessFailedError


def get_dep_groups() -> dict[str, list[str]]:
    pyproject = read_pyproject_toml()
    try:
        dep_groups_section = pyproject["dependency-groups"]
    except KeyError:
        # In the past might have been in [tool.uv.dev-dependencies] section but this
        # will be deprecated.
        return {}

    req_strs_by_group = TypeAdapter(dict[str, list[str]]).validate_python(
        dep_groups_section
    )
    reqs_by_group = {
        group: [Requirement(req_str).name for req_str in req_strs]
        for group, req_strs in req_strs_by_group.items()
    }
    return reqs_by_group


def get_deps_from_group(group: str) -> list[str]:
    dep_groups = get_dep_groups()
    try:
        return dep_groups[group]
    except KeyError:
        return []


def add_deps_to_group(pypi_names: list[str], group: str) -> None:
    """Add a package as a non-build dependency using PEP 735 dependency groups."""
    existing_group = get_deps_from_group(group)

    for dep in pypi_names:
        if _strip_extras(dep) in existing_group:
            # Early exit; the tool is already a dev dependency.
            continue

        tick_print(f"Adding '{dep}' to the '{group}' dependency group.")
        try:
            if not usethis_config.offline:
                call_uv_subprocess(["add", "--group", group, "--quiet", dep])
            else:
                call_uv_subprocess(
                    ["add", "--group", group, "--quiet", "--offline", dep]
                )
        except UVSubprocessFailedError as err:
            msg = f"Failed to add '{dep}' to the '{group}' dependency group:\n{err}"
            raise UVDepGroupError(msg) from None


def remove_deps_from_group(pypi_names: list[str], group: str) -> None:
    """Remove the tool's development dependencies, if present."""
    existing_group = get_deps_from_group(group)

    for dep in pypi_names:
        if _strip_extras(dep) not in existing_group:
            # Early exit; the tool is already not a dependency.
            continue

        tick_print(f"Removing '{dep}' from the '{group}' dependency group.")
        se_dep = _strip_extras(dep)
        try:
            if not usethis_config.offline:
                call_uv_subprocess(["remove", "--group", group, "--quiet", se_dep])
            else:
                call_uv_subprocess(
                    ["remove", "--group", group, "--quiet", "--offline", se_dep]
                )
        except UVSubprocessFailedError as err:
            msg = (
                f"Failed to remove '{dep}' from the '{group}' dependency group:\n{err}"
            )
            raise UVDepGroupError(msg) from None


def is_dep_in_any_group(dep: str) -> bool:
    return _strip_extras(dep) in {
        dep for group in get_dep_groups().values() for dep in group
    }


def _strip_extras(dep: str) -> str:
    """Remove extras from a dependency string."""
    return re.sub(r"\[.*\]", "", dep)
