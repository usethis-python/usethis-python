"""Open project-related URLs in a browser."""

from __future__ import annotations

import typer

from usethis._console import how_print


def browse_pypi(*, package: str, browser: bool = False) -> None:
    """Open the PyPI page for a package."""
    url = f"https://pypi.org/project/{package}/"
    if browser:
        typer.launch(url)
    else:
        how_print(f"Open URL <{url}>.")
