"""Dependency group operations via the uv backend."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import TypeAdapter, ValidationError

from usethis._backend.uv.call import call_uv_subprocess
from usethis._backend.uv.errors import (
    UVDepGroupError,
    UVSubprocessFailedError,
)
from usethis._backend.uv.toml import UVTOMLManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager

if TYPE_CHECKING:
    from usethis._types.deps import Dependency


def add_dep_to_group_via_uv(dep: Dependency, group: str):
    """Add a dependency to the named group using uv."""
    try:
        call_uv_subprocess(
            ["add", "--group", group, str(dep)],
            change_toml=True,
        )
    except UVSubprocessFailedError as err:
        msg = f"Failed to add '{dep}' to the '{group}' dependency group:\n{err}"
        raise UVDepGroupError(msg) from None


def remove_dep_from_group_via_uv(dep: Dependency, group: str):
    """Remove a dependency from the named group using uv."""
    try:
        call_uv_subprocess(["remove", "--group", group, str(dep)], change_toml=True)
    except UVSubprocessFailedError as err:
        msg = f"Failed to remove '{dep}' from the '{group}' dependency group:\n{err}"
        raise UVDepGroupError(msg) from None


def get_default_groups_via_uv() -> list[str]:
    """Get the default dependency groups from the uv configuration."""
    try:
        if UVTOMLManager().path.exists():
            default_groups = TypeAdapter(list[str]).validate_python(
                UVTOMLManager()[["default-groups"]]
            )
        else:
            default_groups = TypeAdapter(list[str]).validate_python(
                PyprojectTOMLManager()[["tool", "uv", "default-groups"]]
            )
    except (KeyError, ValidationError):
        default_groups: list[str] = []

    return default_groups
