"""Docstring style configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._core.tool import use_ruff
from usethis._tool.impl.base.ruff import RuffTool

if TYPE_CHECKING:
    from usethis._types.docstyle import DocStyleEnum


def use_docstyle(style: DocStyleEnum) -> None:
    """Configure the docstring style convention for the project using Ruff."""
    if not RuffTool().is_used():
        use_ruff(minimal=True)

    RuffTool().set_docstyle(style.value)

    if not RuffTool().are_pydocstyle_rules_selected():
        RuffTool().select_rules(["D2", "D3", "D4"])
