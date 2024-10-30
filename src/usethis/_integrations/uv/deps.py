import re
import subprocess

from packaging.requirements import Requirement
from pydantic import TypeAdapter

from usethis._console import console
from usethis._integrations.pyproject.io import read_pyproject_toml


def get_dep_groups() -> dict[str, list[str]]:
    pyproject = read_pyproject_toml()
    try:
        dep_groups_section = pyproject["dependency-groups"]
    except KeyError:
        # In the past might have been in [tool.uv.dev-dependencies] section but this
        # will be deprecated/
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


def add_deps_to_group(pypi_names: list[str], group: str, *, offline: bool) -> None:
    """Add a package as a non-build dependency using PEP 735 dependency groups."""
    existing_group = get_deps_from_group(group)

    for dep in pypi_names:
        if _strip_extras(dep) in existing_group:
            # Early exit; the tool is already a dev dependency.
            continue

        console.tick_print(f"Adding '{dep}' to the '{group}' dependency group.")
        if not offline:
            subprocess.run(
                ["uv", "add", "--group", group, "--quiet", dep],
                check=True,
            )
        else:
            subprocess.run(
                ["uv", "add", "--group", group, "--quiet", "--offline", dep],
                check=True,
            )


def remove_deps_from_group(pypi_names: list[str], group: str, *, offline: bool) -> None:
    """Remove the tool's development dependencies, if present."""
    existing_group = get_deps_from_group(group)

    for dep in pypi_names:
        if _strip_extras(dep) not in existing_group:
            # Early exit; the tool is already not a dependency.
            continue

        console.tick_print(f"Removing '{dep}' from the '{group}' dependency group.")
        if not offline:
            subprocess.run(
                [
                    "uv",
                    "remove",
                    "--group",
                    group,
                    "--quiet",
                    _strip_extras(dep),
                ],
                check=True,
            )
        else:
            subprocess.run(
                [
                    "uv",
                    "remove",
                    "--group",
                    group,
                    "--quiet",
                    "--offline",
                    _strip_extras(dep),
                ],
                check=True,
            )


def is_dep_in_any_group(dep: str) -> bool:
    return _strip_extras(dep) in {
        dep for group in get_dep_groups().values() for dep in group
    }


def _strip_extras(dep: str) -> str:
    """Remove extras from a dependency string."""
    return re.sub(r"\[.*\]", "", dep)
