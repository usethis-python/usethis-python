"""Installation of project packages, done lazily if the backend supports it."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, assert_never

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.sync import sync_environment_via_uv
from usethis._config import usethis_config
from usethis._console import instruct_print
from usethis._types.backend import BackendEnum

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path
    from typing import ClassVar


@contextmanager
def lazy_install_packages() -> Generator[None, None, None]:
    """Context manager to install packages lazily, if the backend supports it.

    Adding several dependencies one after another can be slow if each addition installs
    the dependency separately. Not all backends support a deferred approach though.

    Raises:
        BackendSubprocessFailedError: If installing the packages on exit fails.
    """
    manager = LazyInstallManager()

    if manager.is_active:
        # The scope which is already open is responsible for installing the packages
        yield
        return

    manager.enter()
    try:
        yield
    except BaseException:
        if manager.owed_groups:
            _instruct_install_groups(manager.owed_groups)
        raise
    finally:
        owed_groups = manager.owed_groups
        manager.leave()

    if owed_groups:
        _install_groups_via_backend(owed_groups, path=manager.path)


def _instruct_install_groups(groups: list[str]) -> None:
    """Tell the user to install the groups of dependencies which are owed an install."""
    groups_str = ", ".join([f"'{group}'" for group in groups])
    s = "" if len(groups) == 1 else "s"
    instruct_print(
        f"Install the dependencies which were added to the {groups_str} dependency "
        f"group{s}."
    )


def _install_groups_via_backend(groups: list[str], *, path: Path) -> None:
    backend = get_backend()
    if backend is BackendEnum.uv:
        sync_environment_via_uv(groups, path=path)
    elif backend is BackendEnum.poetry or backend is BackendEnum.none:
        # Only dependencies which are added lazily owe an install, and only the uv
        # backend does that.
        msg = f"The '{backend.value}' backend doesn't install lazily."
        raise AssertionError(msg)
    else:
        assert_never(backend)


class LazyInstallManager:
    """Tracks whether packages are being installed lazily for a project.

    Installing lazily means that, rather than each dependency being installed as it is
    added, installing the dependency groups which were added to is left until the end of
    the scope, so that they are all installed together.

    Each instance is a cheap handle on state which is held per project directory, in the
    same way as `FileManager`. The state is shared between instances for the same project,
    and is isolated from other projects.

    Lifecycle:
        1. **Enter** (`enter`): A scope is opened. There is at most one scope open for
           a project, so whoever finds one open (`is_active`) leaves it to its owner.
        2. **Add** (`mark_pending`): A dependency is added to a group without being
           installed, so that group is owed an installation.
        3. **Leave** (`leave`): The scope is closed. Its owner is responsible for
           installing the groups which are owed (`owed_groups`).
    """

    _pending_groups_by_path: ClassVar[dict[Path, set[str]]] = {}
    path: Path

    def __init__(self) -> None:
        self.path = usethis_config.cpd().resolve()

    @property
    def is_active(self) -> bool:
        """Whether there is an open scope."""
        return self.path in self._pending_groups_by_path

    @property
    def is_lazy(self) -> bool:
        """Whether dependencies are being added without being installed.

        Nothing is installed when frozen, so there is nothing to be lazy about then.
        """
        return self.is_active and not usethis_config.frozen

    @property
    def owed_groups(self) -> list[str]:
        """The dependency groups which are owed an installation.

        There are none if there is no open scope.
        """
        return sorted(self._pending_groups_by_path.get(self.path, set()))

    def enter(self) -> None:
        """Record that a scope has been opened.

        A scope which is already open is left as it is, rather than discarding the
        groups which are owed an installation.
        """
        self._pending_groups_by_path.setdefault(self.path, set())

    def mark_pending(self, group: str) -> None:
        """Record that a dependency was added to the group without being installed.

        Raises:
            KeyError: If there is no open scope.
        """
        self._pending_groups_by_path[self.path].add(group)

    def leave(self) -> None:
        """Record that a scope has been closed."""
        del self._pending_groups_by_path[self.path]
