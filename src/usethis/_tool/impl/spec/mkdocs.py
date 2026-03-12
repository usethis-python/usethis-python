from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from usethis._config_file import MkDocsYMLManager
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager


class MkDocsToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="MkDocs",
            url="https://www.mkdocs.org/",
            managed_files=[Path("mkdocs.yml")],
        )

    def doc_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        deps = [Dependency(name="mkdocs")]

        if unconditional:
            deps.append(Dependency(name="mkdocs-material"))

        return deps

    def preferred_file_manager(self) -> KeyValueFileManager:
        """If there is no currently active config file, this is the preferred one."""
        # Should set the mkdocs.yml file manager as the preferred one
        return MkDocsYMLManager()
