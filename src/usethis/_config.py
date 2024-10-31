from collections.abc import Generator
from contextlib import contextmanager

import typer
from pydantic import BaseModel


class UsethisConfig(BaseModel):
    """Global-state for command options which affect low level behaviour."""

    offline: bool
    quiet: bool

    @contextmanager
    def set(
        self, *, offline: bool | None = None, quiet: bool | None = None
    ) -> Generator[None, None, None]:
        """Temporarily change command options."""
        old_offline = self.offline
        old_quiet = self.quiet

        if offline is None:
            offline = old_offline
        if quiet is None:
            quiet = old_quiet

        self.offline = offline
        self.quiet = quiet
        yield
        self.offline = old_offline
        self.quiet = old_quiet


_OFFLINE_DEFAULT = False
_QUIET_DEFAULT = False

usethis_config = UsethisConfig(offline=_OFFLINE_DEFAULT, quiet=_QUIET_DEFAULT)

offline_opt = typer.Option(_OFFLINE_DEFAULT, "--offline", help="Disable network access")
quiet_opt = typer.Option(_QUIET_DEFAULT, "--quiet", help="Suppress output")
