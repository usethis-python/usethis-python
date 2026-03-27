"""ty tool specification."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, final

from typing_extensions import override

from usethis._config import usethis_config
from usethis._config_file import DotTyTOMLManager, TyTOMLManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.project.layout import get_source_dir_str
from usethis._integrations.project.packages import get_importable_packages
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._file.manager import Document, KeyValueFileManager


class TyToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="ty",
            url="https://docs.astral.sh/ty/",
            managed_files=[Path("ty.toml"), Path(".ty.toml")],
        )

    @override
    @final
    def preferred_file_manager(self) -> KeyValueFileManager[Document]:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return TyTOMLManager()

    @override
    @final
    def raw_cmd(self) -> str:
        return "ty check"

    @override
    @final
    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="ty")]

    @override
    @final
    def pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_system_hook(
            hook_id="ty",
            entry="ty check",
            always_run=True,
            pass_filenames=False,
        )

    @override
    @final
    def config_spec(self) -> ConfigSpec:
        # https://docs.astral.sh/ty/configuration/
        # https://docs.astral.sh/ty/reference/configuration/#include_1

        def _get_src_include() -> list[str]:
            source_dir_str = get_source_dir_str()
            if source_dir_str == "src":
                dirs = ["src"]
            else:
                # Root layout: include the importable package directories
                packages = get_importable_packages()
                dirs = sorted({pkg.split(".")[0] for pkg in packages}) or ["."]
            return [*dirs, "tests"]

        return ConfigSpec.from_flat(
            file_managers=[
                DotTyTOMLManager(),
                TyTOMLManager(),
                PyprojectTOMLManager(),
            ],
            resolution="first",
            config_items=[
                ConfigItem(
                    description="Overall config",
                    root={
                        Path(".ty.toml"): ConfigEntry(keys=[]),
                        Path("ty.toml"): ConfigEntry(keys=[]),
                        Path("pyproject.toml"): ConfigEntry(keys=["tool", "ty"]),
                    },
                ),
                ConfigItem(
                    description="Source include",
                    root={
                        Path(".ty.toml"): ConfigEntry(
                            keys=["src", "include"],
                            get_value=_get_src_include,
                        ),
                        Path("ty.toml"): ConfigEntry(
                            keys=["src", "include"],
                            get_value=_get_src_include,
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "ty", "src", "include"],
                            get_value=_get_src_include,
                        ),
                    },
                ),
            ],
        )
