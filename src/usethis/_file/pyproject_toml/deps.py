"""Dependency extraction from pyproject.toml."""

from __future__ import annotations

import pydantic
from packaging.requirements import Requirement
from pydantic import TypeAdapter

from usethis._file.pyproject_toml.errors import PyprojectTOMLDepsError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._types.deps import Dependency


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

    try:
        req_strs = TypeAdapter(list[str]).validate_python(dep_section)
    except pydantic.ValidationError as err:
        msg = (
            "Failed to parse the 'project.dependencies' section in 'pyproject.toml':\n"
            f"{err}\n\n"
            "Please check the section and try again."
        )
        raise PyprojectTOMLDepsError(msg) from None

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

    try:
        req_strs_by_group = TypeAdapter(dict[str, list[str]]).validate_python(
            dep_groups_section
        )
    except pydantic.ValidationError as err:
        msg = (
            "Failed to parse the 'dependency-groups' section in 'pyproject.toml':\n"
            f"{err}\n\n"
            "Please check the section and try again."
        )
        raise PyprojectTOMLDepsError(msg) from None

    reqs_by_group = {
        group: [Requirement(req_str) for req_str in req_strs]
        for group, req_strs in req_strs_by_group.items()
    }
    return {
        group: [Dependency(name=req.name, extras=frozenset(req.extras)) for req in reqs]
        for group, reqs in reqs_by_group.items()
    }
