from __future__ import annotations

import typer


def version() -> None:
    from usethis._console import plain_print

    try:
        from usethis._version import __version__
    except ImportError:
        __version__ = None

    if __version__ is not None:
        plain_print(__version__)
    else:
        raise typer.Exit(code=1)
