from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import assert_never

from usethis._config import usethis_config
from usethis._config_file import CodespellRCManager
from usethis._console import box_print
from usethis._integrations.backend.dispatch import get_backend
from usethis._integrations.backend.uv.used import is_uv_used
from usethis._integrations.ci.bitbucket.anchor import (
    ScriptItemAnchor as BitbucketScriptItemAnchor,
)
from usethis._integrations.ci.bitbucket.schema import Script as BitbucketScript
from usethis._integrations.ci.bitbucket.schema import Step as BitbucketStep
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

    def print_how_to_use(self) -> None:
        backend = get_backend()
        install_method = self.get_install_method()
        if install_method == "pre-commit":
            if backend is BackendEnum.uv and is_uv_used():
                box_print(
                    "Run 'uv run pre-commit run codespell --all-files' to run the Codespell spellchecker."
                )
            else:
                assert backend in (BackendEnum.none, BackendEnum.uv)
                box_print(
                    "Run 'pre-commit run codespell --all-files' to run the Codespell spellchecker."
                )
        elif install_method == "devdep" or install_method is None:
            if backend is BackendEnum.uv and is_uv_used():
                box_print("Run 'uv run codespell' to run the Codespell spellchecker.")
            else:
                assert backend in (BackendEnum.none, BackendEnum.uv)
                box_print("Run 'codespell' to run the Codespell spellchecker.")
        else:
            assert_never(install_method)

    def get_dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="codespell")]

    def preferred_file_manager(self) -> KeyValueFileManager:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return CodespellRCManager()

    def get_config_spec(self) -> ConfigSpec:
        # https://github.com/codespell-project/codespell?tab=readme-ov-file#using-a-config-file

        return ConfigSpec.from_flat(
            file_managers=[
                CodespellRCManager(),
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

    def get_bitbucket_steps(self) -> list[BitbucketStep]:
        backend = get_backend()

        if backend is BackendEnum.uv:
            return [
                BitbucketStep(
                    name=f"Run {self.name}",
                    caches=["uv"],
                    script=BitbucketScript(
                        [
                            BitbucketScriptItemAnchor(name="install-uv"),
                            "uv run codespell",
                        ]
                    ),
                )
            ]
        elif backend is BackendEnum.none:
            return [
                BitbucketStep(
                    name=f"Run {self.name}",
                    script=BitbucketScript(
                        [
                            BitbucketScriptItemAnchor(name="ensure-venv"),
                            "codespell",
                        ]
                    ),
                )
            ]
        else:
            assert_never(backend)
