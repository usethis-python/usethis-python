from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from usethis._config import usethis_config
from usethis._config_file import DotImportLinterManager
from usethis._console import info_print
from usethis._file.ini.io_ import INIFileManager
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._tool.base import Tool
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec, NoConfigValue
from usethis._tool.impl.base.ruff import RuffTool
from usethis._tool.impl.spec.import_linter import ImportLinterToolSpec

if TYPE_CHECKING:
    from usethis._tool.rule import Rule

IMPORT_LINTER_CONTRACT_MIN_MODULE_COUNT = 3


class ImportLinterTool(ImportLinterToolSpec, Tool):
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

        contracts: list[dict] = []
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

                layers = []
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

        ini_contracts_config_items = []
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

    def is_used(self) -> bool:
        """Check if the Import Linter tool is used in the project."""
        # We suppress the warning about assumptions regarding the package name.
        # See _importlinter_warn_no_packages_found
        with usethis_config.set(quiet=True):
            return super().is_used()

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
