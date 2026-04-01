"""Dependency management operations for project dependency groups."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.call import add_default_groups_via_uv
from usethis._backend.uv.deps import (
    add_dep_to_group_via_uv,
    get_default_groups_via_uv,
    remove_dep_from_group_via_uv,
)
from usethis._backend.uv.errors import UVDepGroupError
from usethis._config import usethis_config
from usethis._console import instruct_print, tick_print
from usethis._file.pyproject_toml.deps import (
    get_dep_groups as _get_dep_groups,
)
from usethis._file.pyproject_toml.deps import (
    get_project_deps as _get_project_deps,
)
from usethis._file.pyproject_toml.errors import PyprojectTOMLDepsError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._types.backend import BackendEnum
from usethis.errors import DepGroupError

if TYPE_CHECKING:
    from usethis._types.deps import Dependency


def get_project_deps() -> list[Dependency]:
    """Get all project dependencies.

    This does not include development dependencies, e.g. not those in the
    dependency-groups section, not extras/optional dependencies, not build dependencies.

    Usually this is just the dependencies in the `project.dependencies` section
    of the `pyproject.toml` file.
    """
    try:
        return _get_project_deps()
    except PyprojectTOMLDepsError as err:
        raise UVDepGroupError(str(err)) from None


def get_dep_groups() -> dict[str, list[Dependency]]:
    """Get all dependency groups from the dependency-groups section of pyproject.toml."""
    try:
        return _get_dep_groups()
    except PyprojectTOMLDepsError as err:
        raise DepGroupError(str(err)) from None


def get_deps_from_group(group: str) -> list[Dependency]:
    """Get the list of dependencies in a named dependency group."""
    dep_groups = get_dep_groups()
    try:
        return dep_groups[group]
    except KeyError:
        return []


def register_default_group(group: str) -> None:
    """Register a group in the default-groups configuration if it's not already there.

    This ensures that dependencies in the group will be installed by default.
    """
    if group == "dev":
        # Note, if the "dev" group is missing already then then we'll respect the
        # user's choice since they presumably would have added it themselves. So, we
        # won't register in that case.
        return

    default_groups = get_default_groups()

    # Choose which groups we want to add
    groups_to_add: list[str] = []
    if group not in default_groups:
        groups_to_add.append(group)
        # Add "dev" if section is empty or if we're adding a new group and "dev" isn't present
        if (not default_groups or group != "dev") and "dev" not in default_groups:
            ensure_dev_group_is_defined()
            groups_to_add.append("dev")

    if groups_to_add:
        add_default_groups(groups=groups_to_add)


def add_default_groups(groups: list[str]) -> None:
    """Register the given dependency groups as default groups in the package manager configuration."""
    backend = get_backend()
    if backend is BackendEnum.uv:
        add_default_groups_via_uv(groups)
    elif backend is BackendEnum.none:
        # This is not really a meaningful concept without a package manager
        pass
    else:
        assert_never(backend)


def get_default_groups() -> list[str]:
    """Get the list of default dependency groups installed automatically by the package manager."""
    backend = get_backend()
    if backend is BackendEnum.uv:
        return get_default_groups_via_uv()
    elif backend is BackendEnum.none:
        # This is not really a meaningful concept without a package manager
        return []
    else:
        assert_never(backend)


def ensure_dev_group_is_defined() -> None:
    # Ensure dev group exists in dependency-groups
    """Ensure the 'dev' dependency group exists in pyproject.toml."""
    PyprojectTOMLManager().extend_list(keys=["dependency-groups", "dev"], values=[])


def is_dep_satisfied_in(dep: Dependency, *, in_: list[Dependency]) -> bool:
    """Check if a dependency is satisfied by any dependency in the given list."""
    return any(_is_dep_satisfied_by(dep, by=by) for by in in_)


def _is_dep_satisfied_by(dep: Dependency, *, by: Dependency) -> bool:
    # Name is the same and extras are a subset of the extras of the dependency
    return dep.name == by.name and (dep.extras or set()) <= (by.extras or set())


def remove_deps_from_group(deps: list[Dependency], group: str) -> None:
    """Remove dependencies from the named group if present."""
    existing_group = get_deps_from_group(group)

    _deps = [dep for dep in deps if is_dep_satisfied_in(dep, in_=existing_group)]

    if not _deps:
        return

    deps_str = ", ".join([f"'{dep}'" for dep in _deps])
    ies = "y" if len(_deps) == 1 else "ies"
    backend = get_backend()

    if backend is BackendEnum.uv:
        tick_print(
            f"Removing dependenc{ies} {deps_str} from the '{group}' group in 'pyproject.toml'."
        )
        for dep in _deps:
            remove_dep_from_group_via_uv(dep, group)
    elif backend is BackendEnum.none:
        instruct_print(f"Remove the {group} dependenc{ies} {deps_str}.")
    else:
        assert_never(backend)


def is_dep_in_any_group(dep: Dependency) -> bool:
    """Check if a dependency exists in any dependency group."""
    return is_dep_satisfied_in(
        dep, in_=[dep for group in get_dep_groups().values() for dep in group]
    )


def add_deps_to_group(
    deps: list[Dependency], group: str, *, default: bool = True
) -> None:
    """Add dependencies to a named group using PEP 735 dependency groups.

    Args:
        deps: The dependencies to add to the group.
        group: The name of the dependency group.
        default: Whether to register the group as a default group. Set to False
                 for groups that should be declared but not installed by default.
    """
    existing_group = get_deps_from_group(group)

    to_add_deps = [
        dep for dep in deps if not is_dep_satisfied_in(dep, in_=existing_group)
    ]

    if not to_add_deps:
        return

    backend = get_backend()

    # Message regarding declaration of the dependencies
    deps_str = ", ".join([f"'{dep}'" for dep in to_add_deps])
    ies = "y" if len(to_add_deps) == 1 else "ies"
    if backend is BackendEnum.uv:
        tick_print(
            f"Adding dependenc{ies} {deps_str} to the '{group}' group in 'pyproject.toml'."
        )
    elif backend is BackendEnum.none:
        instruct_print(f"Add the {group} dependenc{ies} {deps_str}.")
    else:
        assert_never(backend)

    # Installation of the dependencies, and declaration if the package manager supports
    # a combined workflow.
    if usethis_config.frozen:
        instruct_print(f"Install the dependenc{ies} {deps_str}.")
    for dep in to_add_deps:
        if backend is BackendEnum.uv:
            add_dep_to_group_via_uv(dep, group)
        elif backend is BackendEnum.none:
            # We've already used a combined message
            pass
        else:
            assert_never(backend)

    # Register the group - don't do this before adding the deps in case that step fails
    if default:
        _register_default_group(group, backend=backend)


def _register_default_group(
    group: str, *, backend: Literal[BackendEnum.uv, BackendEnum.none]
) -> None:
    if backend is BackendEnum.uv:
        register_default_group(group)
    elif backend is BackendEnum.none:
        # This is not really a meaningful concept without a package manager
        pass
    else:
        assert_never(backend)
