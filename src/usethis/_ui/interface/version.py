from __future__ import annotations

import typer


def version() -> None:
    from usethis._console import plain_print

    try:
        from usethis._version import __version__
    except ImportError:
        raise typer.Exit(code=1) from None
    else:
        plain_print(__version__)
