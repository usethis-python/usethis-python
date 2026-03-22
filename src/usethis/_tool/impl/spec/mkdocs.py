from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, final

from typing_extensions import override

from usethis._config_file import MkDocsYMLManager
from usethis._integrations.project.name import get_project_name
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._file.manager import KeyValueFileManager


class MkDocsToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="MkDocs",
            url="https://www.mkdocs.org/",
            managed_files=[Path("mkdocs.yml")],
        )

    @override
    @final
    def doc_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        deps = [Dependency(name="mkdocs")]

        if unconditional:
            deps.append(Dependency(name="mkdocs-material"))

        return deps

    @override
    @final
    def preferred_file_manager(self) -> KeyValueFileManager[object]:
        """If there is no currently active config file, this is the preferred one."""
        # Should set the mkdocs.yml file manager as the preferred one
        return MkDocsYMLManager()

    @override
    @final
    def config_spec(self) -> ConfigSpec:
        """Get the configuration specification for this tool."""
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
