"""Tach tool implementation."""

from __future__ import annotations

from typing import final

from typing_extensions import override

from usethis._config import usethis_config
from usethis._tool.base import Tool
from usethis._tool.impl.spec.tach import TachToolSpec


@final
class TachTool(TachToolSpec, Tool):
    @override
    def is_used(self) -> bool:
        """Check if the Tach tool is used in the project."""
        # We suppress the warning about assumptions regarding the package name.
        # See _tach_warn_no_packages_found
        with usethis_config.set(quiet=True):
            return super().is_used()
