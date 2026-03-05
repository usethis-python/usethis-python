from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._backend.uv.detect import is_uv_used
from usethis._config_file import MkDocsYMLManager
from usethis._console import how_print
from usethis._integrations.project.name import get_project_name
from usethis._tool.base import Tool, ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._types.backend import BackendEnum
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


class MkDocsTool(MkDocsToolSpec, Tool):
    def config_spec(self) -> ConfigSpec:
        """Get the configuration specification for this tool.

        This includes the file managers and resolution methodology.
        """
        return ConfigSpec.from_flat(
            file_managers=[
                MkDocsYMLManager(),
            ],
            resolution="first_content",
            config_items=[
                ConfigItem(
                    description="Site Name",
                    root={
                        Path("mkdocs.yml"): ConfigEntry(
                            keys=["site_name"],
                            get_value=lambda: get_project_name(),
                        ),
                    },
                ),
                ConfigItem(
                    description="Navigation",
                    root={
                        Path("mkdocs.yml"): ConfigEntry(
                            keys=["nav"],
                            get_value=lambda: [{"Home": "index.md"}],
                        ),
                    },
                ),
            ],
        )

    def print_how_to_use(self) -> None:
        backend = get_backend()
        if backend is BackendEnum.uv and is_uv_used():
            how_print("Run 'uv run mkdocs build' to build the documentation.")
            how_print("Run 'uv run mkdocs serve' to serve the documentation locally.")
        elif backend in (BackendEnum.none, BackendEnum.uv):
            how_print("Run 'mkdocs build' to build the documentation.")
            how_print("Run 'mkdocs serve' to serve the documentation locally.")
        else:
            assert_never(backend)
