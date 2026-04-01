"""Import Linter tool specification."""

from __future__ import annotations

import functools
import re
from pathlib import Path
from typing import TYPE_CHECKING, final

from typing_extensions import override

from usethis._config import usethis_config
from usethis._config_file import DotImportLinterManager
from usethis._console import warn_print
from usethis._file.ini.io_ import INIFileManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._integrations.project.errors import ImportGraphBuildFailedError
from usethis._integrations.project.imports import (
    LayeredArchitecture,
    get_layered_architectures,
)
from usethis._integrations.project.name import get_project_name
from usethis._integrations.project.packages import get_importable_packages
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec, NoConfigValue
from usethis._tool.pre_commit import PreCommitConfig
from usethis._tool.rule import RuleConfig
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._file.manager import Document, KeyValueFileManager
    from usethis._tool.config import ResolutionT

IMPORT_LINTER_CONTRACT_MIN_MODULE_COUNT = 3


class ImportLinterToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Import Linter",
            url="https://github.com/seddonym/import-linter",
            managed_files=[Path(".importlinter")],
            rule_config=RuleConfig(
                unmanaged_selected=["INP"], tests_unmanaged_ignored=["INP"]
            ),
        )

    @override
    @final
    def raw_cmd(self) -> str:
        return "lint-imports"

    @override
    @final
    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="import-linter")]

    @override
    @final
    def preferred_file_manager(self) -> KeyValueFileManager[Document]:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return DotImportLinterManager()

    @override
    @final
    def config_spec(self) -> ConfigSpec:
        # https://import-linter.readthedocs.io/en/stable/usage.html

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
                    >= IMPORT_LINTER_CONTRACT_MIN_MODULE_COUNT
                    for layered_architecture in layered_architecture_by_module.values()
                )
            ),
            default=0,
        )

        contracts: list[dict[str, bool | str | list[str]]] = []
        for (
            layered_architecture_by_module
        ) in layered_architecture_by_module_by_root_package.values():
            for module, layered_architecture in layered_architecture_by_module.items():
                # We only skip if we have at least one contract.
                if len(contracts) > 0 and (
                    (
                        # Skip if the contract isn't big enough to be notable.
                        layered_architecture.module_count()
                        < IMPORT_LINTER_CONTRACT_MIN_MODULE_COUNT
                    )
                    and
                    # We have waited until we have finished a complete depth level
                    # (e.g. we have done all of a.b, a.c, and a.d so we won't go on to
                    # a.b.e)
                    module.count(".") > min_depth
                ):
                    continue

                layers: list[str] = []
                for layer in layered_architecture.layers:
                    layers.append(" | ".join(sorted(layer)))

                contract = {
                    "name": module,
                    "type": "layers",
                    "layers": layers,
                    "containers": [module],
                    "exhaustive": True,
                }

                if layered_architecture.excluded:
                    contract["exhaustive_ignores"] = sorted(
                        layered_architecture.excluded
                    )

                contracts.append(contract)

        if not contracts:
            raise AssertionError

        def get_root_packages() -> list[str] | NoConfigValue:
            # There are two configuration items which are very similar:
            # root_packages = ["usethis"]  # noqa: ERA001
            # root_package = "usethis" # noqa: ERA001
            # Maybe at a later point we can abstract this case of variant config
            # into ConfigEntry but it seems premautre, so for now for Import Linter
            # we manually check this case. This might give somewhat reduced performance,
            # perhaps.
            if self._is_root_package_singular():
                return NoConfigValue()
            return list(layered_architecture_by_module_by_root_package.keys())

        # We're only going to add the INI contracts if there aren't already any
        # contracts, so we need to check if there are any contracts.
        are_active_ini_contracts = self._are_active_ini_contracts()

        ini_contracts_config_items: list[ConfigItem] = []
        for idx, contract in enumerate(contracts):
            if are_active_ini_contracts:
                continue

            # Cast bools to strings for INI files
            ini_contract = contract.copy()
            ini_contract["exhaustive"] = str(ini_contract["exhaustive"])

            ini_contracts_config_items.append(
                ConfigItem(
                    description=f"Itemized Contract {idx} (INI)",
                    root={
                        Path("setup.cfg"): ConfigEntry(
                            keys=[f"importlinter:contract:{idx}"],
                            get_value=lambda c=ini_contract: c,
                        ),
                        Path(".importlinter"): ConfigEntry(
                            keys=[f"importlinter:contract:{idx}"],
                            get_value=lambda c=ini_contract: c,
                        ),
                    },
                    applies_to_all=False,
                )
            )

        return ConfigSpec(
            file_manager_by_relative_path=self._get_file_manager_by_relative_path(),
            resolution=self._get_resolution(),
            config_items=[
                ConfigItem(
                    description="Overall config",
                    root={
                        Path("setup.cfg"): ConfigEntry(keys=["importlinter"]),
                        Path(".importlinter"): ConfigEntry(keys=["importlinter"]),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "importlinter"]
                        ),
                    },
                ),
                ConfigItem(
                    description="Root packages",
                    root={
                        Path("setup.cfg"): ConfigEntry(
                            keys=["importlinter", "root_packages"],
                            get_value=get_root_packages,
                        ),
                        Path(".importlinter"): ConfigEntry(
                            keys=["importlinter", "root_packages"],
                            get_value=get_root_packages,
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "importlinter", "root_packages"],
                            get_value=get_root_packages,
                        ),
                    },
                ),
                ConfigItem(
                    description="Listed Contracts",
                    root={
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "importlinter", "contracts"],
                            get_value=lambda: contracts,
                        ),
                        # N.B. these INI sections are added via
                        # `ini_contracts_config_items`
                        # but there might be others so we still need to declare they
                        # are associated with this tool based on regex.
                        Path(".importlinter"): ConfigEntry(
                            keys=[re.compile("importlinter:contract:.*")]
                        ),
                        Path(".importlinter"): ConfigEntry(
                            keys=[re.compile("importlinter:contract:.*")]
                        ),
                    },
                    applies_to_all=False,
                ),
                *ini_contracts_config_items,
            ],
        )

    @final
    def _are_active_ini_contracts(self) -> bool:
        # Consider active config manager, and see if there's a matching regex
        # for the contract in the INI file.
        (file_manager,) = self._get_active_config_file_managers_from_resolution(
            self._get_resolution(),
            file_manager_by_relative_path=self._get_file_manager_by_relative_path(),
        )
        if not isinstance(file_manager, INIFileManager):
            return False
        return [re.compile("importlinter:contract:.*")] in file_manager

    @final
    def _is_root_package_singular(self) -> bool:
        (file_manager,) = self._get_active_config_file_managers_from_resolution(
            self._get_resolution(),
            file_manager_by_relative_path=self._get_file_manager_by_relative_path(),
        )
        if isinstance(file_manager, PyprojectTOMLManager):
            return ["tool", "importlinter", "root_package"] in file_manager
        elif isinstance(file_manager, SetupCFGManager | DotImportLinterManager):
            return ["importlinter", "root_package"] in file_manager
        else:
            msg = f"Unsupported file manager: '{file_manager}'."
            raise NotImplementedError(msg)

    @final
    def _get_layered_architecture_by_module_by_root_package(
        self,
    ) -> dict[str, dict[str, LayeredArchitecture]]:
        root_packages = sorted(get_importable_packages())
        if not root_packages:
            # Couldn't find any packages, we're assuming the package name is the name
            # of the project. Warn the user accordingly.
            name = get_project_name()
            _importlinter_warn_no_packages_found(name)
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

    @final
    def _get_resolution(self) -> ResolutionT:
        return "first"

    @final
    def _get_file_manager_by_relative_path(
        self,
    ) -> dict[Path, KeyValueFileManager[Document]]:
        return {
            Path("setup.cfg"): SetupCFGManager(),
            Path(".importlinter"): DotImportLinterManager(),
            Path("pyproject.toml"): PyprojectTOMLManager(),
        }

    @override
    @final
    def pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_system_hook(
            hook_id="import-linter",
            entry="lint-imports",
        )


@functools.cache
def _importlinter_warn_no_packages_found(name: str) -> None:
    warn_print("Could not find any importable packages.")
    warn_print(f"Assuming the package name is {name}.")
