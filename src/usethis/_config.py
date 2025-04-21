from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

import typer
from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import Generator


class UsethisConfig(BaseModel):
    """Global-state for command options which affect low level behaviour."""

    offline: bool
    quiet: bool
    frozen: bool = False
    subprocess_verbose: bool = False

    @contextmanager
    def set(
        self,
        *,
        offline: bool | None = None,
        quiet: bool | None = None,
        frozen: bool | None = None,
        subprocess_verbose: bool | None = None,
    ) -> Generator[None, None, None]:
        """Temporarily change command options."""
        old_offline = self.offline
        old_quiet = self.quiet
        old_frozen = self.frozen
        old_subprocess_verbose = self.subprocess_verbose

        if offline is None:
            offline = old_offline
        if quiet is None:
            quiet = old_quiet
        if frozen is None:
            frozen = old_frozen
        if subprocess_verbose is None:
            subprocess_verbose = old_subprocess_verbose

        self.offline = offline
        self.quiet = quiet
        self.frozen = frozen
        self.subprocess_verbose = subprocess_verbose
        yield
        self.offline = old_offline
        self.quiet = old_quiet
        self.frozen = old_frozen
        self.subprocess_verbose = old_subprocess_verbose


_OFFLINE_DEFAULT = False
_QUIET_DEFAULT = False

usethis_config = UsethisConfig(
    offline=_OFFLINE_DEFAULT,
    quiet=_QUIET_DEFAULT,
    frozen=False,
    subprocess_verbose=False,
)

offline_opt = typer.Option(_OFFLINE_DEFAULT, "--offline", help="Disable network access")
quiet_opt = typer.Option(_QUIET_DEFAULT, "--quiet", help="Suppress output")
