"""Dependency extraction from pyproject.toml."""

from __future__ import annotations

from typing import Any

from packaging.requirements import Requirement

from usethis._file.pyproject_toml.errors import PyprojectTOMLDepsError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._types.deps import Dependency
from usethis._validate import validate_or_raise


def get_project_deps() -> list[Dependency]:
    """Get all project dependencies from [project.dependencies].

    This does not include development dependencies, e.g. not those in the
    dependency-groups section, not extras/optional dependencies, not build dependencies.
    """
    try:
        pyproject = PyprojectTOMLManager().get()
    except FileNotFoundError:
        return []

    try:
        project_section = pyproject["project"]
    except KeyError:
        return []

    if not isinstance(project_section, dict):
        return []

    try:
        dep_section = project_section["dependencies"]
    except KeyError:
        return []

    req_strs = validate_or_raise(
        list[str],
        dep_section,
        error_cls=PyprojectTOMLDepsError,
        error_msg=(
            "Failed to parse the 'project.dependencies' section in 'pyproject.toml'.\n\n"
            "Please check the section and try again."
        ),
    )

    reqs = [Requirement(req_str) for req_str in req_strs]
    return [Dependency(name=req.name, extras=frozenset(req.extras)) for req in reqs]


def get_dep_groups() -> dict[str, list[Dependency]]:
    """Get all dependency groups from [dependency-groups]."""
    try:
        pyproject = PyprojectTOMLManager().get()
    except FileNotFoundError:
        return {}

    try:
        dep_groups_section = pyproject["dependency-groups"]
    except KeyError:
        return {}

    req_strs_by_group = validate_or_raise(
        dict[str, list[str]],
        dep_groups_section,
        error_cls=PyprojectTOMLDepsError,
        error_msg=(
            "Failed to parse the 'dependency-groups' section in 'pyproject.toml'.\n\n"
            "Please check the section and try again."
        ),
    )

    reqs_by_group = {
        group: [Requirement(req_str) for req_str in req_strs]
        for group, req_strs in req_strs_by_group.items()
    }
    return {
        group: [Dependency(name=req.name, extras=frozenset(req.extras)) for req in reqs]
        for group, reqs in reqs_by_group.items()
    }


def get_poetry_project_deps() -> list[Dependency]:
    """Get project dependencies from [tool.poetry.dependencies].

    This reads Poetry's custom dependency specification format where
    dependencies are key-value pairs rather than PEP 508 strings.
    The ``python`` key is excluded since it represents a Python version
    constraint, not a package dependency.
    """
    try:
        pyproject = PyprojectTOMLManager().get()
    except FileNotFoundError:
        return []

    poetry_deps = (
        pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {})  # type: ignore[union-attr]
    )

    if not isinstance(poetry_deps, dict):
        return []

    return _parse_poetry_deps(poetry_deps)


def get_poetry_dep_groups() -> dict[str, list[Dependency]]:
    """Get dependency groups from [tool.poetry.group.*.dependencies].

    This reads Poetry's custom group dependency specification format where
    each group has its own ``[tool.poetry.group.GROUPNAME.dependencies]``
    section containing key-value pairs.
    """
    try:
        pyproject = PyprojectTOMLManager().get()
    except FileNotFoundError:
        return {}

    poetry_groups = pyproject.get("tool", {}).get("poetry", {}).get("group", {})  # type: ignore[union-attr]

    if not isinstance(poetry_groups, dict):
        return {}

    result: dict[str, list[Dependency]] = {}
    for group_name, group_config in poetry_groups.items():
        if not isinstance(group_config, dict):
            continue
        group_deps = group_config.get("dependencies", {})
        if not isinstance(group_deps, dict):
            continue
        deps = _parse_poetry_deps(group_deps)
        if deps:
            result[group_name] = deps

    return result


def _parse_poetry_deps(deps_table: dict[str, Any]) -> list[Dependency]:
    """Parse a Poetry dependencies table into a list of Dependency objects.

    Poetry dependencies are key-value pairs where:
    - The key is the package name
    - The value is either a version string (e.g. ``"^2.28"``) or a dict
      (e.g. ``{version = "^2.28", extras = ["security"]}``)

    The ``python`` key is excluded.
    """
    result: list[Dependency] = []
    for name, spec in deps_table.items():
        if name.lower() == "python":
            continue
        extras: frozenset[str] = frozenset()
        if isinstance(spec, dict):
            extras_list = spec.get("extras", [])
            if isinstance(extras_list, list):
                extras = frozenset(str(e) for e in extras_list)
        result.append(Dependency(name=name, extras=extras))
    return result
