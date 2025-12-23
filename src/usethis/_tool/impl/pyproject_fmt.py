from __future__ import annotations

from pathlib import Path

from typing_extensions import assert_never

from usethis._console import how_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.backend.uv.used import is_uv_used
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.pre_commit.schema import HookDefinition, UriRepo
from usethis._tool.base import Tool
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency

_PYPROJECT_FMT_VERSION = "v2.11.1"  # Manually bump this version when necessary


class PyprojectFmtTool(Tool):
    # https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt
    # https://github.com/tox-dev/pyproject-fmt
    @property
    def name(self) -> str:
        return "pyproject-fmt"

    def default_command(self) -> str:
        backend = get_backend()
        if backend is BackendEnum.uv and is_uv_used():
            return "uv run pyproject-fmt pyproject.toml"
        elif backend is BackendEnum.none or backend is BackendEnum.uv:
            return "pyproject-fmt pyproject.toml"
        else:
            assert_never(backend)

    def print_how_to_use(self) -> None:
        install_method = self.get_install_method()
        backend = get_backend()
        if install_method == "pre-commit":
            if backend is BackendEnum.uv and is_uv_used():
                how_print(
                    f"Run 'uv run pre-commit run pyproject-fmt --all-files' to run {self.name}."
                )
            elif backend in (BackendEnum.none, BackendEnum.uv):
                how_print(
                    f"Run 'pre-commit run pyproject-fmt --all-files' to run {self.name}."
                )
            else:
                assert_never(backend)
        elif install_method == "devdep" or install_method is None:
            cmd = self.default_command()
            how_print(f"Run '{cmd}' to run {self.name}.")
        else:
            assert_never(install_method)

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="pyproject-fmt")]

    def get_config_spec(self) -> ConfigSpec:
        # https://pyproject-fmt.readthedocs.io/en/latest/#configuration-via-file
        return ConfigSpec.from_flat(
            file_managers=[PyprojectTOMLManager()],
            resolution="first",
            config_items=[
                ConfigItem(
                    description="Overall Config",
                    root={
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "pyproject-fmt"]
                        )
                    },
                ),
                ConfigItem(
                    description="Keep Full Version",
                    root={
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "pyproject-fmt", "keep_full_version"],
                            get_value=lambda: True,
                        )
                    },
                ),
            ],
        )

    def get_pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_single_repo(
            UriRepo(
                repo="https://github.com/tox-dev/pyproject-fmt",
                rev=_PYPROJECT_FMT_VERSION,
                hooks=[HookDefinition(id="pyproject-fmt")],
            ),
            requires_venv=False,
        )
