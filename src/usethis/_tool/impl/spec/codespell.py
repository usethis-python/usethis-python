from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, final

from typing_extensions import override

from usethis._config import usethis_config
from usethis._config_file import DotCodespellRCManager
from usethis._file.pyproject_toml.errors import PyprojectTOMLNotFoundError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.pyproject_toml.requires_python import (
    MissingRequiresPythonError,
    get_required_minor_python_versions,
)
from usethis._file.setup_cfg.io_ import SetupCFGManager
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._python.version import PythonVersion
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.deps import Dependency
from usethis._versions import CODESPELL_VERSION

if TYPE_CHECKING:
    from usethis._file.manager import KeyValueFileManager


class CodespellToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Codespell",
            url="https://github.com/codespell-project/codespell",
            managed_files=[Path(".codespellrc")],
        )

    @override
    @final
    def preferred_file_manager(self) -> KeyValueFileManager[object]:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return DotCodespellRCManager()

    @override
    @final
    def raw_cmd(self) -> str:
        return "codespell"

    @override
    @final
    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        deps = [Dependency(name="codespell")]

        # Python < 3.11 needs tomli (instead of the stdlib tomllib) to read
        # pyproject.toml files
        if unconditional:
            needs_tomli = True
        else:
            try:
                versions = get_required_minor_python_versions()
            except (MissingRequiresPythonError, PyprojectTOMLNotFoundError):
                versions = [PythonVersion.from_interpreter()]

            needs_tomli = any(v.to_short_tuple() < (3, 11) for v in versions)
        if needs_tomli:
            deps.append(Dependency(name="tomli"))

        return deps

    @override
    @final
    def pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_single_repo(
            pre_commit_schema.UriRepo(
                repo="https://github.com/codespell-project/codespell",
                rev=CODESPELL_VERSION,
                hooks=[
                    pre_commit_schema.HookDefinition(
                        id="codespell", additional_dependencies=["tomli"]
                    )
                ],
            ),
            requires_venv=False,
        )

    @override
    @final
    def config_spec(self) -> ConfigSpec:
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
