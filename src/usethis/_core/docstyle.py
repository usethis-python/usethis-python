from typing import Literal

from usethis._core.tool import use_ruff
from usethis._tool.impl.ruff import RuffTool
from usethis.errors import UsethisError


class UnknownDocstringStyleError(ValueError, UsethisError):
    """Exception raised for unknown docstring styles."""


def use_docstyle(style: Literal["numpy", "google", "pep257"]) -> None:
    if not RuffTool().is_used():
        use_ruff(minimal=True)

    RuffTool().set_docstyle(style)

    if not RuffTool()._are_pydocstyle_rules_selected():
        RuffTool().select_rules(["D2", "D3", "D4"])
