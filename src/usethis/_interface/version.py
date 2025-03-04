from __future__ import annotations

import typer

try:
    from usethis._version import __version__
except ImportError:
    __version__ = None


def version() -> None:
    if __version__ is not None:
        print(__version__)
    else:
        raise typer.Exit(code=1)
