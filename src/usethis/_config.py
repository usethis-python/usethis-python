from collections.abc import Generator
from contextlib import contextmanager

import typer
from pydantic import BaseModel

_OFFLINE_DEFAULT = False
_QUIET_DEFAULT = False

offline_opt = typer.Option(_OFFLINE_DEFAULT, "--offline", help="Disable network access")
quiet_opt = typer.Option(_QUIET_DEFAULT, "--quiet", help="Suppress output")


class UsethisConfig(BaseModel):
    """Global-state for command options which affect low level behaviour."""

    offline: bool
    quiet: bool

    @contextmanager
    def set(self, *, offline: bool, quiet: bool) -> Generator[None, None, None]:
        """Temporarily set the console to quiet mode."""
        self.offline = offline
        self.quiet = quiet
        yield
        self.offline = _OFFLINE_DEFAULT
        self.quiet = _QUIET_DEFAULT


usethis_config = UsethisConfig(offline=_OFFLINE_DEFAULT, quiet=_QUIET_DEFAULT)
