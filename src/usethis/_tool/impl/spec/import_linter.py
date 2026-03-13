from __future__ import annotations

import functools
from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._backend.dispatch import get_backend
from usethis._config import usethis_config
from usethis._config_file import DotImportLinterManager
from usethis._console import warn_print
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._integrations.pre_commit.language import get_system_language
from usethis._integrations.project.errors import ImportGraphBuildFailedError
from usethis._integrations.project.imports import (
    LayeredArchitecture,
    get_layered_architectures,
)
from usethis._integrations.project.name import get_project_name
from usethis._integrations.project.packages import get_importable_packages
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._tool.rule import RuleConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager
    from usethis._tool.config import ResolutionT


class ImportLinterToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Import Linter",
            url="https://github.com/seddonym/import-linter",
            managed_files=[Path(".importlinter")],
            rule_config=RuleConfig(
                unmanaged_selected=["INP"], tests_unmanaged_ignored=["INP"]
            ),
        )

    def raw_cmd(self) -> str:
        return "lint-imports"

    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="import-linter")]

    def preferred_file_manager(self) -> KeyValueFileManager[object]:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return DotImportLinterManager()

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

        layered_architecture_by_module_by_root_package = {}
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

            layered_architecture_by_module_by_root_package[root_package] = (
                layered_architecture_by_module
            )

        return layered_architecture_by_module_by_root_package

    def _get_resolution(self) -> ResolutionT:
        return "first"

    def _get_file_manager_by_relative_path(
        self,
    ) -> dict[Path, KeyValueFileManager[object]]:
        return {
            Path("setup.cfg"): SetupCFGManager(),
            Path(".importlinter"): DotImportLinterManager(),
            Path("pyproject.toml"): PyprojectTOMLManager(),
        }

    def pre_commit_config(self) -> PreCommitConfig:
        backend = get_backend()

        if backend is BackendEnum.uv:
            return PreCommitConfig.from_single_repo(
                pre_commit_schema.LocalRepo(
                    repo="local",
                    hooks=[
                        pre_commit_schema.HookDefinition(
                            id="import-linter",
                            name="import-linter",
                            pass_filenames=False,
                            entry="uv run --frozen --offline lint-imports",
                            language=get_system_language(),
                            require_serial=True,
                            always_run=True,
                        )
                    ],
                ),
                requires_venv=True,
                inform_how_to_use_on_migrate=False,
            )
        elif backend is BackendEnum.none:
            return PreCommitConfig.from_single_repo(
                pre_commit_schema.LocalRepo(
                    repo="local",
                    hooks=[
                        pre_commit_schema.HookDefinition(
                            id="import-linter",
                            name="import-linter",
                            pass_filenames=False,
                            entry="lint-imports",
                            language=get_system_language(),
                        )
                    ],
                ),
                requires_venv=True,
                inform_how_to_use_on_migrate=False,
            )
        else:
            assert_never(backend)


@functools.cache
def _importlinter_warn_no_packages_found(name: str) -> None:
    warn_print("Could not find any importable packages.")
    warn_print(f"Assuming the package name is {name}.")
