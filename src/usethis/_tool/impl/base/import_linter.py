"""Import Linter tool implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

from typing_extensions import override

from usethis._config import usethis_config
from usethis._console import info_print
from usethis._tool.base import Tool
from usethis._tool.impl.base.ruff import RuffTool
from usethis._tool.impl.spec.import_linter import ImportLinterToolSpec

if TYPE_CHECKING:
    from usethis._tool.rule import Rule


@final
class ImportLinterTool(ImportLinterToolSpec, Tool):
    @override
    def is_used(self) -> bool:
        """Check if the Import Linter tool is used in the project."""
        # We suppress the warning about assumptions regarding the package name.
        # See _importlinter_warn_no_packages_found
        with usethis_config.set(quiet=True):
            return super().is_used()

    @override
    def print_how_to_use(self) -> None:
        if not _is_inp_rule_selected():
            # If Ruff is used, we enable the INP rules instead.
            info_print("Ensure '__init__.py' files are used in your packages.")
            info_print(
                "For more info see <https://docs.python.org/3/tutorial/modules.html#packages>"
            )
        super().print_how_to_use()


def _is_inp_rule_selected() -> bool:
    return any(_is_inp_rule(rule) for rule in RuffTool().selected_rules())


def _is_inp_rule(rule: Rule) -> bool:
    return rule.startswith("INP") and (not rule[3:] or rule[3:].isdigit())
