from __future__ import annotations

import pydantic
from packaging.requirements import Requirement
from pydantic import BaseModel, TypeAdapter

from usethis._config import usethis_config
from usethis._console import box_print, tick_print
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.uv.call import call_uv_subprocess
from usethis._integrations.uv.errors import UVDepGroupError, UVSubprocessFailedError
from usethis._integrations.uv.toml import UVTOMLManager


class Dependency(BaseModel):
    name: str
    extras: frozenset[str] = frozenset()

    def __str__(self) -> str:
        extras = sorted(self.extras or set())
        return self.name + "".join(f"[{extra}]" for extra in extras)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.name, self.extras))


def get_project_deps() -> list[Dependency]:
    """Get all project dependencies.

    This does not include development dependencies, e.g. not those in the
    dependency-groups section, not extras/optional dependencies, not build dependencies.

    Usually this is just the dependencies in the `project.dependencies` section
    of the `pyproject.toml` file.
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
        raise UVDepGroupError(msg) from None

    reqs = [Requirement(req_str) for req_str in req_strs]
    deps = [Dependency(name=req.name, extras=frozenset(req.extras)) for req in reqs]
    return deps


def get_dep_groups() -> dict[str, list[Dependency]]:
    try:
        pyproject = PyprojectTOMLManager().get()
    except FileNotFoundError:
        return {}

    try:
        dep_groups_section = pyproject["dependency-groups"]
    except KeyError:
        # In the past might have been in [tool.uv.dev-dependencies] section but this
        # will be deprecated.
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
        raise UVDepGroupError(msg) from None
    reqs_by_group = {
        group: [Requirement(req_str) for req_str in req_strs]
        for group, req_strs in req_strs_by_group.items()
    }
    deps_by_group = {
        group: [Dependency(name=req.name, extras=frozenset(req.extras)) for req in reqs]
        for group, reqs in reqs_by_group.items()
    }
    return deps_by_group


def get_deps_from_group(group: str) -> list[Dependency]:
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
    groups_to_add = []
    if group not in default_groups:
        groups_to_add.append(group)
        # Add "dev" if section is empty or if we're adding a new group and "dev" isn't present
        if (not default_groups or group != "dev") and "dev" not in default_groups:
            ensure_dev_group_is_defined()
            groups_to_add.append("dev")

    if groups_to_add:
        add_default_groups(groups=groups_to_add)


def add_default_groups(groups: list[str]) -> None:
    if UVTOMLManager().path.exists():
        UVTOMLManager().extend_list(keys=["default-groups"], values=groups)
    else:
        PyprojectTOMLManager().extend_list(
            keys=["tool", "uv", "default-groups"], values=groups
        )


def get_default_groups() -> list[str]:
    try:
        if UVTOMLManager().path.exists():
            default_groups = UVTOMLManager()[["default-groups"]]
        else:
            default_groups = PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
        if not isinstance(default_groups, list):
            default_groups = []
    except KeyError:
        default_groups = []

    return default_groups


def ensure_dev_group_is_defined() -> None:
    # Ensure dev group exists in dependency-groups
    PyprojectTOMLManager().extend_list(keys=["dependency-groups", "dev"], values=[])


def add_deps_to_group(deps: list[Dependency], group: str) -> None:
    """Add a package as a non-build dependency using PEP 735 dependency groups."""
    existing_group = get_deps_from_group(group)

    to_add_deps = [
        dep for dep in deps if not is_dep_satisfied_in(dep, in_=existing_group)
    ]

    if not to_add_deps:
        return

    deps_str = ", ".join([f"'{dep}'" for dep in to_add_deps])
    ies = "y" if len(to_add_deps) == 1 else "ies"
    tick_print(
        f"Adding dependenc{ies} {deps_str} to the '{group}' group in 'pyproject.toml'."
    )

    if usethis_config.frozen:
        box_print(f"Install the dependenc{ies} {deps_str}.")

    for dep in to_add_deps:
        try:
            call_uv_subprocess(
                ["add", "--group", group, str(dep)],
                change_toml=True,
            )
        except UVSubprocessFailedError as err:
            msg = f"Failed to add '{dep}' to the '{group}' dependency group:\n{err}"
            msg += (usethis_config.cpd() / "pyproject.toml").read_text()
            raise UVDepGroupError(msg) from None

    # Register the group - don't do this before adding the deps in case that step fails
    register_default_group(group)


def is_dep_satisfied_in(dep: Dependency, *, in_: list[Dependency]) -> bool:
    return any(_is_dep_satisfied_by(dep, by=by) for by in in_)


def _is_dep_satisfied_by(dep: Dependency, *, by: Dependency) -> bool:
    # Name is the same and extras are a subset of the extras of the dependency
    return dep.name == by.name and (dep.extras or set()) <= (by.extras or set())


def remove_deps_from_group(deps: list[Dependency], group: str) -> None:
    """Remove the tool's development dependencies, if present."""
    existing_group = get_deps_from_group(group)

    _deps = [dep for dep in deps if is_dep_satisfied_in(dep, in_=existing_group)]

    if not _deps:
        return

    deps_str = ", ".join([f"'{dep}'" for dep in _deps])
    ies = "y" if len(_deps) == 1 else "ies"
    tick_print(
        f"Removing dependenc{ies} {deps_str} from the '{group}' group in 'pyproject.toml'."
    )

    for dep in _deps:
        try:
            call_uv_subprocess(["remove", "--group", group, str(dep)], change_toml=True)
        except UVSubprocessFailedError as err:
            msg = (
                f"Failed to remove '{dep}' from the '{group}' dependency group:\n{err}"
            )
            raise UVDepGroupError(msg) from None


def is_dep_in_any_group(dep: Dependency) -> bool:
    return is_dep_satisfied_in(
        dep, in_=[dep for group in get_dep_groups().values() for dep in group]
    )
