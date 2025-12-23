from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._config import usethis_config
from usethis._config_file import DotCodespellRCManager
from usethis._console import how_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.backend.uv.used import is_uv_used
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.file.setup_cfg.io_ import SetupCFGManager
from usethis._integrations.pre_commit.schema import HookDefinition, UriRepo
from usethis._tool.base import Tool
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.backend import BackendEnum
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager

_CODESPELL_VERSION = "v2.4.1"  # Manually bump this version when necessary


class CodespellTool(Tool):
    # https://github.com/codespell-project/codespell
    @property
    def name(self) -> str:
        return "Codespell"

    def default_command(self) -> str:
        backend = get_backend()
        if backend is BackendEnum.uv and is_uv_used():
            return "uv run codespell"
        elif backend is BackendEnum.none or backend is BackendEnum.uv:
            return "codespell"
        else:
            assert_never(backend)

    def print_how_to_use(self) -> None:
        backend = get_backend()
        install_method = self.get_install_method()
        if install_method == "pre-commit":
            if backend is BackendEnum.uv and is_uv_used():
                how_print(
                    "Run 'uv run pre-commit run codespell --all-files' to run the Codespell spellchecker."
                )
            elif backend in (BackendEnum.none, BackendEnum.uv):
                how_print(
                    "Run 'pre-commit run codespell --all-files' to run the Codespell spellchecker."
                )
            else:
                assert_never(backend)
        elif install_method == "devdep" or install_method is None:
            cmd = self.default_command()
            how_print(f"Run '{cmd}' to run the Codespell spellchecker.")
        else:
            assert_never(install_method)

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="codespell")]

    def preferred_file_manager(self) -> KeyValueFileManager:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return DotCodespellRCManager()

    def get_config_spec(self) -> ConfigSpec:
        # https://github.com/codespell-project/codespell?tab=readme-ov-file#using-a-config-file

        return ConfigSpec.from_flat(
            file_managers=[
                DotCodespellRCManager(),
                SetupCFGManager(),
                PyprojectTOMLManager(),
            ],
            resolution="first_content",
            config_items=[
                ConfigItem(
                    description="Overall config",
                    root={
                        Path(".codespellrc"): ConfigEntry(keys=[]),
                        Path("setup.cfg"): ConfigEntry(keys=["codespell"]),
                        Path("pyproject.toml"): ConfigEntry(keys=["tool", "codespell"]),
                    },
                ),
                ConfigItem(
                    description="Ignore long base64 strings",
                    root={
                        Path(".codespellrc"): ConfigEntry(
                            keys=["codespell", "ignore-regex"],
                            get_value=lambda: "[A-Za-z0-9+/]{100,}",
                        ),
                        Path("setup.cfg"): ConfigEntry(
                            keys=["codespell", "ignore-regex"],
                            get_value=lambda: "[A-Za-z0-9+/]{100,}",
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "codespell", "ignore-regex"],
                            get_value=lambda: ["[A-Za-z0-9+/]{100,}"],
                        ),
                    },
                ),
                ConfigItem(
                    description="Ignore Words List",
                    root={
                        Path(".codespellrc"): ConfigEntry(
                            keys=["codespell", "ignore-words-list"],
                            get_value=lambda: "...",
                        ),
                        Path("setup.cfg"): ConfigEntry(
                            keys=["codespell", "ignore-words-list"],
                            get_value=lambda: "...",
                        ),
                        Path("pyproject.toml"): ConfigEntry(
                            keys=["tool", "codespell", "ignore-words-list"],
                            get_value=lambda: ["..."],
                        ),
                    },
                ),
            ],
        )

    def get_managed_files(self) -> list[Path]:
        return [Path(".codespellrc")]

    def get_pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_single_repo(
            UriRepo(
                repo="https://github.com/codespell-project/codespell",
                rev=_CODESPELL_VERSION,
                hooks=[
                    HookDefinition(id="codespell", additional_dependencies=["tomli"])
                ],
            ),
            requires_venv=False,
        )
