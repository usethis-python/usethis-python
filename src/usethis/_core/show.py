from __future__ import annotations

import tomlkit
from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._console import plain_print, warn_print
from usethis._integrations.project.errors import ImportGraphBuildFailedError
from usethis._integrations.project.imports import (
    LayeredArchitecture,
    get_layered_architectures,
)
from usethis._integrations.project.name import get_project_name
from usethis._integrations.project.packages import get_importable_packages
from usethis._integrations.sonarqube.config import get_sonar_project_properties
from usethis._tool.impl.spec.import_linter import (
    IMPORT_LINTER_CONTRACT_MIN_MODULE_COUNT,
)
from usethis._types.config_format import ConfigFormatEnum


def show_backend() -> None:
    plain_print(get_backend().value)


def show_name() -> None:
    plain_print(get_project_name())


def show_sonarqube_config(*, project_key: str | None = None) -> None:
    plain_print(get_sonar_project_properties(project_key=project_key))


def show_import_linter_config(*, format_: ConfigFormatEnum) -> None:
    plain_print(get_import_linter_config(format_=format_))


def get_import_linter_config(*, format_: ConfigFormatEnum) -> str:
    if format_ is ConfigFormatEnum.toml:
        return _get_import_linter_config_toml()
    elif format_ is ConfigFormatEnum.ini:
        return _get_import_linter_config_ini()
    else:
        assert_never(format_)


def _get_import_linter_contracts_and_root_packages() -> tuple[
    list[dict[str, bool | str | list[str]]], list[str]
]:
    """Build the import-linter contracts and root packages from the project structure.

    Returns:
        A tuple of (contracts, root_packages).
    """
    layered_architecture_by_module_by_root_package = (
        _get_layered_architecture_by_module_by_root_package()
    )

    root_packages = list(layered_architecture_by_module_by_root_package.keys())

    # Build contracts using the same logic as ImportLinterToolSpec.config_spec()
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
            if len(contracts) > 0 and (
                (
                    layered_architecture.module_count()
                    < IMPORT_LINTER_CONTRACT_MIN_MODULE_COUNT
                )
                and module.count(".") > min_depth
            ):
                continue

            layers: list[str] = []
            for layer in layered_architecture.layers:
                layers.append(" | ".join(sorted(layer)))

            contract: dict[str, bool | str | list[str]] = {
                "name": module,
                "type": "layers",
                "layers": layers,
                "containers": [module],
                "exhaustive": True,
            }

            if layered_architecture.excluded:
                contract["exhaustive_ignores"] = sorted(layered_architecture.excluded)

            contracts.append(contract)

    return contracts, root_packages


def _get_layered_architecture_by_module_by_root_package() -> (
    dict[str, dict[str, LayeredArchitecture]]
):
    """Get layered architectures for all root packages in the project.

    This replicates the logic from ImportLinterToolSpec to avoid calling
    private methods.
    """
    root_packages = sorted(get_importable_packages())
    if not root_packages:
        name = get_project_name()
        warn_print("Could not find any importable packages.")
        warn_print(f"Assuming the package name is {name}.")
        root_packages = [name]

    result: dict[str, dict[str, LayeredArchitecture]] = {}
    for root_package in root_packages:
        try:
            layered_architecture_by_module = get_layered_architectures(root_package)
        except ImportGraphBuildFailedError:
            layered_architecture_by_module = {}

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

        result[root_package] = layered_architecture_by_module

    return result


def _get_import_linter_config_toml() -> str:
    contracts, root_packages = _get_import_linter_contracts_and_root_packages()

    data: dict[str, object] = {
        "tool": {
            "importlinter": {
                "root_packages": root_packages,
                "contracts": contracts,
            }
        }
    }

    return tomlkit.dumps(data).rstrip("\n")


def _get_import_linter_config_ini() -> str:
    contracts, root_packages = _get_import_linter_contracts_and_root_packages()

    lines: list[str] = ["[importlinter]"]
    if len(root_packages) == 1:
        lines.append(f"root_package = {root_packages[0]}")
    else:
        lines.append("root_packages =")
        for pkg in root_packages:
            lines.append(f"    {pkg}")

    for idx, contract in enumerate(contracts):
        lines.append("")
        lines.append(f"[importlinter:contract:{idx}]")
        lines.append(f"name = {contract['name']}")
        lines.append(f"type = {contract['type']}")
        contract_layers = contract["layers"]
        assert isinstance(contract_layers, list)
        _append_ini_list(lines, "layers", contract_layers)
        contract_containers = contract["containers"]
        assert isinstance(contract_containers, list)
        _append_ini_list(lines, "containers", contract_containers)
        lines.append(f"exhaustive = {contract['exhaustive']}")
        if "exhaustive_ignores" in contract:
            contract_ignores = contract["exhaustive_ignores"]
            assert isinstance(contract_ignores, list)
            _append_ini_list(lines, "exhaustive_ignores", contract_ignores)

    return "\n".join(lines)


def _append_ini_list(lines: list[str], key: str, values: list[str]) -> None:
    """Append a key-value pair to the INI lines, handling list values."""
    if len(values) == 1:
        lines.append(f"{key} = {values[0]}")
    else:
        lines.append(f"{key} =")
        for value in values:
            lines.append(f"    {value}")
