from enum import Enum

from usethis._core.tool import use_ruff
from usethis._tool.impl.ruff import RuffTool


class DocStyleEnum(Enum):
    numpy = "numpy"
    google = "google"
    pep257 = "pep257"


def use_docstyle(style: DocStyleEnum) -> None:
    if not RuffTool().is_used():
        use_ruff(minimal=True)

    RuffTool().set_docstyle(style.value)

    if not RuffTool()._are_pydocstyle_rules_selected():
        RuffTool().select_rules(["D2", "D3", "D4"])
