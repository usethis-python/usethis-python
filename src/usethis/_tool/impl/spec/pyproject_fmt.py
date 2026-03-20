from __future__ import annotations

from pathlib import Path

from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.deps import Dependency

_PYPROJECT_FMT_VERSION = "v2.16.2"  # Manually bump this version when necessary


class PyprojectFmtToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="pyproject-fmt",
            # also https://github.com/tox-dev/pyproject-fmt for pre-commit hook
            url="https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt",
        )

    def raw_cmd(self) -> str:
        return "pyproject-fmt pyproject.toml"

    def dev_deps(self, *, unconditional: bool = False) -> list[Dependency]:
        return [Dependency(name="pyproject-fmt")]

    def pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_single_repo(
            pre_commit_schema.UriRepo(
                repo="https://github.com/tox-dev/pyproject-fmt",
                rev=_PYPROJECT_FMT_VERSION,
                hooks=[pre_commit_schema.HookDefinition(id="pyproject-fmt")],
            ),
            requires_venv=False,
        )

    def config_spec(self) -> ConfigSpec:
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
