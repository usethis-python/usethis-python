"""Tach tool specification."""

from __future__ import annotations

import functools
from pathlib import Path
from typing import TYPE_CHECKING, final

from typing_extensions import override

from usethis._config import usethis_config
from usethis._config_file import TachTOMLManager
from usethis._console import warn_print
from usethis._integrations.project.errors import ImportGraphBuildFailedError
from usethis._integrations.project.imports import (
    LayeredArchitecture,
    get_layered_architectures,
)
from usethis._integrations.project.layout import get_source_dir_str
from usethis._integrations.project.name import get_project_name
from usethis._integrations.project.packages import get_importable_packages
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._file.manager import Document, KeyValueFileManager

TACH_CONTRACT_MIN_MODULE_COUNT = 3


class TachToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Tach",
            url="https://github.com/gauge-sh/tach",
            managed_files=[Path("tach.toml")],
        )

    @override
    @final
    def raw_cmd(self) -> str:
        return "tach check"

    @override
    @final
    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="tach")]

    @override
    @final
    def preferred_file_manager(self) -> KeyValueFileManager[Document]:
        return TachTOMLManager()

    @override
    @final
    def config_spec(self) -> ConfigSpec:
        # https://docs.gauge.sh/usage/configuration/

        layered_architecture_by_module_by_root_package = (
            self._get_layered_architecture_by_module_by_root_package()
        )

        min_depth = min(
            (
                module.count(".")
                for layered_architecture_by_module in layered_architecture_by_module_by_root_package.values()
                for module in layered_architecture_by_module
                if any(
                    layered_architecture.module_count()
                    >= TACH_CONTRACT_MIN_MODULE_COUNT
                    for layered_architecture in layered_architecture_by_module.values()
                )
            ),
            default=0,
        )

        # Collect layers and modules from the architecture analysis
        all_layer_names: list[str] = []
        modules: list[dict[str, object]] = []
        seen_layer_names: set[str] = set()

        for (
            layered_architecture_by_module
        ) in layered_architecture_by_module_by_root_package.values():
            for module, layered_architecture in layered_architecture_by_module.items():
                if len(modules) > 0 and (
                    (
                        layered_architecture.module_count()
                        < TACH_CONTRACT_MIN_MODULE_COUNT
                    )
                    and module.count(".") > min_depth
                ):
                    continue

                # Tach layers are ordered from highest to lowest.
                # Each layer in layered_architecture.layers is a set of module names
                # at the same level. We assign numeric layer names.
                for layer_idx, layer in enumerate(layered_architecture.layers):
                    layer_name = f"layer{layer_idx}"
                    if layer_name not in seen_layer_names:
                        all_layer_names.append(layer_name)
                        seen_layer_names.add(layer_name)

                    for mod_name in sorted(layer):
                        full_path = f"{module}.{mod_name}"
                        # Determine dependencies: modules in lower layers (higher idx)
                        dep_paths: list[str] = []
                        for dep_layer_idx in range(layer_idx + 1, len(layered_architecture.layers)):
                            for dep_mod in sorted(layered_architecture.layers[dep_layer_idx]):
                                dep_paths.append(f"{module}.{dep_mod}")

                        mod_entry: dict[str, object] = {
                            "path": full_path,
                            "depends_on": dep_paths,
                            "layer": layer_name,
                        }
                        modules.append(mod_entry)

                for excluded_mod in sorted(layered_architecture.excluded):
                    full_path = f"{module}.{excluded_mod}"
                    mod_entry = {
                        "path": full_path,
                        "depends_on": [],
                        "utility": True,
                    }
                    modules.append(mod_entry)

        source_root = get_source_dir_str()

        config_items = [
            ConfigItem(
                description="Tach overall config",
                root={
                    Path("tach.toml"): ConfigEntry(keys=["source_roots"]),
                },
            ),
            ConfigItem(
                description="Source roots",
                root={
                    Path("tach.toml"): ConfigEntry(
                        keys=["source_roots"],
                        get_value=lambda: [source_root],
                    ),
                },
            ),
            ConfigItem(
                description="Exclude patterns",
                root={
                    Path("tach.toml"): ConfigEntry(
                        keys=["exclude"],
                        get_value=lambda: [
                            "**/*__pycache__",
                            "build/",
                            "dist/",
                            "docs/",
                            "tests/",
                            "venv/",
                        ],
                    ),
                },
            ),
        ]

        if all_layer_names:
            config_items.append(
                ConfigItem(
                    description="Layers",
                    root={
                        Path("tach.toml"): ConfigEntry(
                            keys=["layers"],
                            get_value=lambda: all_layer_names,
                        ),
                    },
                ),
            )

        if modules:
            config_items.append(
                ConfigItem(
                    description="Modules",
                    root={
                        Path("tach.toml"): ConfigEntry(
                            keys=["modules"],
                            get_value=lambda: modules,
                        ),
                    },
                ),
            )

        return ConfigSpec.from_flat(
            file_managers=[TachTOMLManager()],
            resolution="first",
            config_items=config_items,
        )

    @final
    def _get_layered_architecture_by_module_by_root_package(
        self,
    ) -> dict[str, dict[str, LayeredArchitecture]]:
        root_packages = sorted(get_importable_packages())
        if not root_packages:
            name = get_project_name()
            _tach_warn_no_packages_found(name)
            root_packages = [name]

        layered_architecture_by_module_by_root_package: dict[
            str, dict[str, LayeredArchitecture]
        ] = {}
        for root_package in root_packages:
            try:
                layered_architecture_by_module = get_layered_architectures(root_package)
            except ImportGraphBuildFailedError:
                layered_architecture_by_module: dict[str, LayeredArchitecture] = {}

            if not layered_architecture_by_module:
                layered_architecture_by_module = {
                    root_package: LayeredArchitecture(layers=[], excluded=set())
                }

            layered_architecture_by_module = dict(
                sorted(
                    layered_architecture_by_module.items(),
                    key=lambda item: item[0].count("."),
                )
            )

            layered_architecture_by_module_by_root_package[root_package] = (
                layered_architecture_by_module
            )

        return layered_architecture_by_module_by_root_package

    @override
    @final
    def pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_system_hook(
            hook_id="tach",
            entry="tach check",
        )


@functools.cache
def _tach_warn_no_packages_found(name: str) -> None:
    warn_print("Could not find any importable packages.")
    warn_print(f"Assuming the package name is {name}.")
