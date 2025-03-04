from __future__ import annotations

import typer

from usethis._console import box_print


def browse_pypi(*, package: str, browser: bool = False) -> None:
    url = f"https://pypi.org/project/{package}/"
    if browser:
        typer.launch(url)
    else:
        box_print(f"Open URL <{url}>.")
