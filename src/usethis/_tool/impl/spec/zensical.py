"""Zensical tool specification."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, final

from typing_extensions import override

from usethis._config_file import MkDocsYMLManager, ZensicalTOMLManager
from usethis._integrations.project.name import get_project_name
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._file.manager import Document, KeyValueFileManager


class ZensicalToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Zensical",
            url="https://zensical.org/",
            managed_files=[Path("zensical.toml")],
        )

    @override
    @final
    def doc_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="zensical")]

    @override
    @final
    def preferred_file_manager(self) -> KeyValueFileManager[Document]:
        """If there is no currently active config file, this is the preferred one."""
        return ZensicalTOMLManager()

    @override
    @final
    def config_spec(self) -> ConfigSpec:
        """Get the configuration specification for this tool."""
        return ConfigSpec.from_flat(
            file_managers=[
                ZensicalTOMLManager(),
                MkDocsYMLManager(),
            ],
            resolution="first_content",
            config_items=[
                ConfigItem(
                    description="Site Name",
                    root={
                        Path("zensical.toml"): ConfigEntry(
                            keys=["project", "site_name"],
                            get_value=lambda: get_project_name(),
                        ),
                        Path("mkdocs.yml"): ConfigEntry(
                            keys=["site_name"],
                            get_value=lambda: get_project_name(),
                        ),
                    },
                ),
                ConfigItem(
                    description="Navigation",
                    root={
                        Path("zensical.toml"): ConfigEntry(
                            keys=["project", "nav"],
                            get_value=lambda: [{"Home": "index.md"}],
                        ),
                        Path("mkdocs.yml"): ConfigEntry(
                            keys=["nav"],
                            get_value=lambda: [{"Home": "index.md"}],
                        ),
                    },
                ),
            ],
        )
