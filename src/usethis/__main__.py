"""The CLI application for usethis."""

from __future__ import annotations

from usethis._app import app

app(prog_name="usethis")

__all__ = ["app"]
