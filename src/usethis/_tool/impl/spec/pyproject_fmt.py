"""pyproject-fmt tool specification."""

from __future__ import annotations

from pathlib import Path
from typing import final

from typing_extensions import override

from usethis._fallback import FALLBACK_PYPROJECT_FMT_VERSION
from usethis._file.pyproject_toml.errors import PyprojectTOMLNotFoundError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.pyproject_toml.requires_python import (
    MissingRequiresPythonError,
    get_required_minor_python_versions,
)
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._python.version import PythonVersion
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.config import ConfigEntry, ConfigItem, ConfigSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.deps import Dependency


class PyprojectFmtToolSpec(ToolSpec):
    @final
    @property
    @override
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="pyproject-fmt",
            # also https://github.com/tox-dev/pyproject-fmt for pre-commit hook
            url="https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt",
        )

    @override
    @final
    def raw_cmd(self) -> str:
        return "pyproject-fmt pyproject.toml"

    @override
    @final
    def deps_by_group(
        self, *, unconditional: bool = False
    ) -> dict[str, list[Dependency]]:
        deps = [Dependency(name="pyproject-fmt")]

        # pyproject-fmt v2.22.0+ vendored toml-fmt-common without declaring
        # tomli as a dependency.  Python < 3.11 needs tomli (instead of the
        # stdlib tomllib) to parse TOML files.
        if unconditional:
            needs_tomli = True
        else:
            try:
                versions = get_required_minor_python_versions()
            except (MissingRequiresPythonError, PyprojectTOMLNotFoundError):
                versions = [PythonVersion.from_interpreter()]

            needs_tomli = any(v.to_short_tuple() < (3, 11) for v in versions)
        if needs_tomli:
            # tomli is a supporting dependency shared with other tools, not
            # characteristic of pyproject-fmt, so it must not identify pyproject-fmt
            # as used.
            deps.append(Dependency(name="tomli", is_identifying=False))

        return {"dev": deps}

    @override
    @final
    def pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_single_repo(
            pre_commit_schema.UriRepo(
                repo="https://github.com/tox-dev/pyproject-fmt",
                rev=FALLBACK_PYPROJECT_FMT_VERSION,
                hooks=[pre_commit_schema.HookDefinition(id="pyproject-fmt")],
            ),
            requires_venv=False,
        )

    @override
    @final
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
