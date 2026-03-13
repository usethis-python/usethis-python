from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from usethis._config import usethis_config
from usethis._config_file import DotCodespellRCManager
from usethis._file.pyproject_toml.errors import PyprojectTOMLNotFoundError
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._file.pyproject_toml.requires_python import (
    MissingRequiresPythonError,
    get_required_minor_python_versions,
)
from usethis._integrations.pre_commit import schema as pre_commit_schema
from usethis._python.version import PythonVersion
from usethis._tool.base import ToolMeta, ToolSpec
from usethis._tool.pre_commit import PreCommitConfig
from usethis._types.deps import Dependency

if TYPE_CHECKING:
    from usethis._io import KeyValueFileManager

_CODESPELL_VERSION = "v2.4.1"  # Manually bump this version when necessary


class CodespellToolSpec(ToolSpec):
    @property
    def meta(self) -> ToolMeta:
        return ToolMeta(
            name="Codespell",
            url="https://github.com/codespell-project/codespell",
            managed_files=[Path(".codespellrc")],
        )

    def preferred_file_manager(self) -> KeyValueFileManager[object]:
        if (usethis_config.cpd() / "pyproject.toml").exists():
            return PyprojectTOMLManager()
        return DotCodespellRCManager()

    def raw_cmd(self) -> str:
        return "codespell"

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

    def pre_commit_config(self) -> PreCommitConfig:
        return PreCommitConfig.from_single_repo(
            pre_commit_schema.UriRepo(
                repo="https://github.com/codespell-project/codespell",
                rev=_CODESPELL_VERSION,
                hooks=[
                    pre_commit_schema.HookDefinition(
                        id="codespell", additional_dependencies=["tomli"]
                    )
                ],
            ),
            requires_venv=False,
        )
