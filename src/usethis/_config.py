from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

HOW_DEFAULT = False
REMOVE_DEFAULT = False
FROZEN_DEFAULT = False
OFFLINE_DEFAULT = False
QUIET_DEFAULT = False


@dataclass
class UsethisConfig:
    """Global-state for command options which affect low level behaviour.

    Attributes:
        offline: Disable network access.
        quiet: Suppress all output, regardless of any other options.
        frozen: Do not install dependencies, nor update lockfiles.
        alert_only: Suppress all output except for warnings and errors.
        disable_uv_subprocess: Raise an error if a uv subprocess invocation is tried.
        disable_pre_commit: Disable pre-commit integrations. Assume that pre-commit is
                            never used (unless explicitly requested via a function whose
                            purpose is to modify pre-commit configuration).
        subprocess_verbose: Verbose output for subprocesses.
        force_project_dir: Directory for the project. If None, defaults to the current
                           working directory dynamically determined at runtime.
    """

    offline: bool = False
    quiet: bool = False
    frozen: bool = False
    alert_only: bool = False
    disable_uv_subprocess: bool = False
    disable_pre_commit: bool = False
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
        disable_uv_subprocess: bool | None = None,
        disable_pre_commit: bool | None = None,
        subprocess_verbose: bool | None = None,
        project_dir: Path | str | None = None,
    ) -> Generator[None, None, None]:
        """Temporarily change command options."""
        old_offline = self.offline
        old_quiet = self.quiet
        old_frozen = self.frozen
        old_alert_only = self.alert_only
        old_disable_uv_subprocess = self.disable_uv_subprocess
        old_disable_pre_commit = self.disable_pre_commit
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
        if disable_uv_subprocess is None:
            disable_uv_subprocess = old_disable_uv_subprocess
        if disable_pre_commit is None:
            disable_pre_commit = old_disable_pre_commit
        if subprocess_verbose is None:
            subprocess_verbose = old_subprocess_verbose
        if project_dir is None:
            project_dir = old_project_dir

        self.offline = offline
        self.quiet = quiet
        self.frozen = frozen
        self.alert_only = alert_only
        self.disable_uv_subprocess = disable_uv_subprocess
        self.disable_pre_commit = disable_pre_commit
        self.subprocess_verbose = subprocess_verbose
        if isinstance(project_dir, str):
            project_dir = Path(project_dir)
        self.project_dir = project_dir
        yield
        self.offline = old_offline
        self.quiet = old_quiet
        self.frozen = old_frozen
        self.alert_only = old_alert_only
        self.disable_uv_subprocess = old_disable_uv_subprocess
        self.disable_pre_commit = old_disable_pre_commit
        self.subprocess_verbose = old_subprocess_verbose
        self.project_dir = old_project_dir

    def cpd(self) -> Path:
        """Return the current project directory."""
        if self.project_dir is None:
            return Path.cwd()
        return self.project_dir


usethis_config = UsethisConfig(
    offline=OFFLINE_DEFAULT,
    quiet=QUIET_DEFAULT,
    frozen=FROZEN_DEFAULT,
    alert_only=False,
    disable_uv_subprocess=False,
    disable_pre_commit=False,
    subprocess_verbose=False,
)
