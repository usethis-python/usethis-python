"""Check whether the uv CLI is available."""

from __future__ import annotations

from typing import TYPE_CHECKING

from packaging.requirements import InvalidRequirement, Requirement

from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.errors import UVSubprocessFailedError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from tomlkit import TOMLDocument


def is_uv_available() -> bool:
    """Check if the `uv` command is available in the current environment."""
    try:
        call_uv_subprocess(["--version"], change_toml=False)
    except UVSubprocessFailedError:
        return _is_uv_a_dep()

    return True


def _is_uv_a_dep() -> bool:
    """Check if uv is declared as a project dependency or in a dependency group.

    Note: we cannot use the higher-level ``get_project_deps`` /
    ``get_dep_groups`` helpers from ``usethis._deps`` because the
    ``_backend`` layer must not import from the ``_deps`` layer
    (enforced by import-linter).  The logic below mirrors those
    functions using only ``_file`` and ``_types`` which are
    permitted.
    """
    uv_dep = Dependency(name="uv")

    try:
        pyproject = PyprojectTOMLManager().get()
    except Exception:
        return False

    all_deps = _get_project_deps(pyproject) + _get_dep_group_deps(pyproject)
    return any(dep.name == uv_dep.name for dep in all_deps)


def _get_project_deps(pyproject: TOMLDocument) -> list[Dependency]:
    """Extract dependencies from the [project.dependencies] section."""
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

    if not isinstance(dep_section, list):
        return []

    deps: list[Dependency] = []
    for item in dep_section:
        if not isinstance(item, str):
            continue
        try:
            req = Requirement(item)
        except InvalidRequirement:
            continue
        deps.append(Dependency(name=req.name, extras=frozenset(req.extras)))
    return deps


def _get_dep_group_deps(pyproject: TOMLDocument) -> list[Dependency]:
    """Extract dependencies from all [dependency-groups] sections."""
    try:
        groups_section = pyproject["dependency-groups"]
    except KeyError:
        return []

    if not isinstance(groups_section, dict):
        return []

    deps: list[Dependency] = []
    for group_items in groups_section.values():
        if not isinstance(group_items, list):
            continue
        for item in group_items:
            if not isinstance(item, str):
                continue
            try:
                req = Requirement(item)
            except InvalidRequirement:
                continue
            deps.append(Dependency(name=req.name, extras=frozenset(req.extras)))
    return deps
