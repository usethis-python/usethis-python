from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import Generator


class UsethisConfig(BaseModel):
    """Global-state for command options which affect low level behaviour.

    Attributes:
        offline: Disable network access.
        quiet: Suppress all output, regardless of any other options.
        frozen: Do not install dependencies, nor update lockfiles.
        alert_only: Suppress all output except for warnings and errors.
        subprocess_verbose: Verbose output for subprocesses.
        force_project_dir: Directory for the project. If None, defaults to the current
                           working directory dynamically determined at runtime.
    """

    offline: bool = False
    quiet: bool = False
    frozen: bool = False
    alert_only: bool = False
    subprocess_verbose: bool = False
    project_dir: Path | None = None

    @contextmanager
    def set(  # noqa: PLR0913
        self,
        *,
        offline: bool | None = None,
        quiet: bool | None = None,
        frozen: bool | None = None,
        alert_only: bool | None = None,
        subprocess_verbose: bool | None = None,
        project_dir: Path | str | None = None,
    ) -> Generator[None, None, None]:
        """Temporarily change command options."""
        old_offline = self.offline
        old_quiet = self.quiet
        old_frozen = self.frozen
        old_alert_only = self.alert_only
        old_subprocess_verbose = self.subprocess_verbose
        old_project_dir = self.project_dir

        if offline is None:
            offline = old_offline
        if quiet is None:
            quiet = old_quiet
        if frozen is None:
            frozen = old_frozen
        if alert_only is None:
            alert_only = self.alert_only
        if subprocess_verbose is None:
            subprocess_verbose = old_subprocess_verbose
        if project_dir is None:
            project_dir = old_project_dir

        self.offline = offline
        self.quiet = quiet
        self.frozen = frozen
        self.alert_only = alert_only
        self.subprocess_verbose = subprocess_verbose
        if isinstance(project_dir, str):
            project_dir = Path(project_dir)
        self.project_dir = project_dir
        yield
        self.offline = old_offline
        self.quiet = old_quiet
        self.frozen = old_frozen
        self.alert_only = old_alert_only
        self.subprocess_verbose = old_subprocess_verbose
        self.project_dir = old_project_dir

    def cpd(self) -> Path:
        """Return the current project directory."""
        if self.project_dir is None:
            return Path.cwd()
        return self.project_dir


_OFFLINE_DEFAULT = False
_QUIET_DEFAULT = False
_HOW_DEFAULT = False
_REMOVE_DEFAULT = False
_FROZEN_DEFAULT = False

usethis_config = UsethisConfig(
    offline=_OFFLINE_DEFAULT,
    quiet=_QUIET_DEFAULT,
    frozen=False,
    alert_only=False,
    subprocess_verbose=False,
)

offline_opt = typer.Option(_OFFLINE_DEFAULT, "--offline", help="Disable network access")
quiet_opt = typer.Option(_QUIET_DEFAULT, "--quiet", help="Suppress output")
how_opt = typer.Option(
    _HOW_DEFAULT,
    "--how",
    help="Only print how to use tools, do not add or remove them.",
)
remove_opt = typer.Option(
    _REMOVE_DEFAULT, "--remove", help="Remove tools instead of adding them."
)
frozen_opt = typer.Option(
    _FROZEN_DEFAULT,
    "--frozen",
    help="Do not install dependencies, nor update lockfiles.",
)
