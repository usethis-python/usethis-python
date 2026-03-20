from __future__ import annotations

from usethis._console import how_print
from usethis._tool.base import Tool
from usethis._tool.impl.spec.codespell import CodespellToolSpec


class CodespellTool(CodespellToolSpec, Tool):
    def print_how_to_use(self) -> None:
        how_print(f"Run '{self.how_to_use_cmd()}' to run the {self.name} spellchecker.")
