from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._console import plain_print
from usethis._integrations.project.name import get_project_name
from usethis._integrations.sonarqube.config import get_sonar_project_properties

if TYPE_CHECKING:
    from usethis._types.config_format import ConfigFormatEnum


def show_backend() -> None:
    plain_print(get_backend().value)


def show_name() -> None:
    plain_print(get_project_name())


def show_sonarqube_config(*, project_key: str | None = None) -> None:
    plain_print(get_sonar_project_properties(project_key=project_key))


def show_import_linter_config(*, format: ConfigFormatEnum) -> None:
    plain_print(get_import_linter_config(format=format))


def get_import_linter_config(*, format: ConfigFormatEnum) -> str:
    from usethis._types.config_format import ConfigFormatEnum

    if format is ConfigFormatEnum.toml:
        return _get_import_linter_config_toml()
    elif format is ConfigFormatEnum.ini:
        return _get_import_linter_config_ini()
    else:
        assert_never(format)


def _get_import_linter_contracts_and_root_packages() -> (
    tuple[list[dict[str, bool | str | list[str]]], list[str]]
):
    """Build the import-linter contracts and root packages from the project structure.

    Returns:
        A tuple of (contracts, root_packages).
    """
    from usethis._tool.impl.spec.import_linter import (
        IMPORT_LINTER_CONTRACT_MIN_MODULE_COUNT,
        ImportLinterToolSpec,
    )

    # Reuse the spec's method for getting layered architectures
    spec = ImportLinterToolSpec()
    layered_architecture_by_module_by_root_package = (
        spec._get_layered_architecture_by_module_by_root_package()
    )

    root_packages = list(layered_architecture_by_module_by_root_package.keys())

    # Build contracts using the same logic as config_spec()
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


def _get_import_linter_config_toml() -> str:
    import tomlkit

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
        if len(contract_layers) == 1:
            lines.append(f"layers = {contract_layers[0]}")
        else:
            lines.append("layers =")
            for layer in contract_layers:
                lines.append(f"    {layer}")

        contract_containers = contract["containers"]
        assert isinstance(contract_containers, list)
        if len(contract_containers) == 1:
            lines.append(f"containers = {contract_containers[0]}")
        else:
            lines.append("containers =")
            for container in contract_containers:
                lines.append(f"    {container}")

        lines.append(f"exhaustive = {contract['exhaustive']}")

        if "exhaustive_ignores" in contract:
            ignores = contract["exhaustive_ignores"]
            assert isinstance(ignores, list)
            if len(ignores) == 1:
                lines.append(f"exhaustive_ignores = {ignores[0]}")
            else:
                lines.append("exhaustive_ignores =")
                for ignore in ignores:
                    lines.append(f"    {ignore}")

    return "\n".join(lines)
