"""Dependency group operations via the Poetry backend."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._backend.poetry.call import call_poetry_subprocess
from usethis._backend.poetry.errors import (
    PoetryDepGroupError,
    PoetrySubprocessFailedError,
)

if TYPE_CHECKING:
    from usethis._types.deps import Dependency


def add_dep_to_group_via_poetry(dep: Dependency, group: str) -> None:
    """Add a dependency to the named group using Poetry."""
    try:
        call_poetry_subprocess(
            ["add", "--group", group, str(dep)],
            change_toml=True,
        )
    except PoetrySubprocessFailedError as err:
        msg = f"Failed to add '{dep}' to the '{group}' dependency group:\n{err}"
        raise PoetryDepGroupError(msg) from None


def remove_dep_from_group_via_poetry(dep: Dependency, group: str) -> None:
    """Remove a dependency from the named group using Poetry."""
    try:
        call_poetry_subprocess(
            ["remove", "--group", group, str(dep)],
            change_toml=True,
        )
    except PoetrySubprocessFailedError as err:
        msg = f"Failed to remove '{dep}' from the '{group}' dependency group:\n{err}"
        raise PoetryDepGroupError(msg) from None
