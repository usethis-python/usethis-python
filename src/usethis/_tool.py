from abc import abstractmethod
from pathlib import Path
from typing import Protocol

from usethis._console import tick_print
from usethis._integrations.pre_commit.hooks import (
    add_repo,
    get_hook_names,
    remove_hook,
)
from usethis._integrations.pre_commit.schema import (
    FileType,
    FileTypes,
    HookDefinition,
    Language,
    LocalRepo,
    UriRepo,
)
from usethis._integrations.pyproject.config import PyProjectConfig
from usethis._integrations.pyproject.core import (
    PyProjectTOMLValueAlreadySetError,
    PyProjectTOMLValueMissingError,
    do_id_keys_exist,
    remove_config_value,
    set_config_value,
)
from usethis._integrations.uv.deps import Dependency, is_dep_in_any_group


class Tool(Protocol):
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool, for display purposes.

        It is assumed that this name is also the name of the Python package associated
        with the tool; if not, make sure to override methods which access this property.
        """

    @property
    def dev_deps(self) -> list[Dependency]:
        """The tool's development dependencies."""
        return []

    def get_extra_dev_deps(self) -> list[Dependency]:
        """Additional development dependencies for the tool.

        These won't be installed automatically - usually they are only needed for
        integrations with other tools and will only be conditionally installed.

        However, they will be used to determine if the tool is being used, so they
        should be considered characteristic of the tool. It follows that they should be
        removed when the tool is being removed.
        """
        return []

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        """Get the pre-commit repository configurations for the tool."""
        return []

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        """Get the pyproject configurations for the tool.

        All configuration keys returned by this method must be sub-keys of the
        keys returned by get_pyproject_id_keys().
        """
        return []

    def get_associated_ruff_rules(self) -> list[str]:
        """Get the Ruff rule codes associated with the tool."""
        return []

    def get_managed_files(self) -> list[Path]:
        """Get (relative) paths to files managed by the tool."""
        return []

    def get_pyproject_id_keys(self) -> list[list[str]]:
        """Get keys for any pyproject.toml sections only used by this tool (not shared)."""
        return []

    def is_used(self) -> bool:
        """Whether the tool is being used in the current project.

        Three heuristics are used by default:
        1. Whether any of the tool's characteristic dev dependencies are in the project.
        2. Whether any of the tool's managed files are in the project.
        3. Whether any of the tool's managed pyproject.toml sections are present.
        """
        for file in self.get_managed_files():
            if file.exists() and file.is_file():
                return True
        for id_keys in self.get_pyproject_id_keys():
            if do_id_keys_exist(id_keys):
                return True
        for dep in self.dev_deps:
            if is_dep_in_any_group(dep):
                return True
        for extra_dep in self.get_extra_dev_deps():
            if is_dep_in_any_group(extra_dep):
                return True

        return False

    def add_pre_commit_repo_configs(self) -> None:
        """Add the tool's pre-commit configuration."""
        repos = self.get_pre_commit_repos()

        if not repos:
            return

        # Add the config for this specific tool.
        for repo_config in repos:
            if repo_config.hooks is None:
                continue

            if len(repo_config.hooks) > 1:
                msg = "Multiple hooks in a single repo not yet supported."
                raise NotImplementedError(msg)

            for hook in repo_config.hooks:
                if hook.id not in get_hook_names():
                    # This will remove the placeholder, if present.
                    add_repo(repo_config)

    def remove_pre_commit_repo_configs(self) -> None:
        """Remove the tool's pre-commit configuration.

        If the .pre-commit-config.yaml file does not exist, this method has no effect.
        """
        repo_configs = self.get_pre_commit_repos()

        if not repo_configs:
            return

        for repo_config in repo_configs:
            if repo_config.hooks is None:
                continue

            # Remove the config for this specific tool.
            for hook in repo_config.hooks:
                if hook.id in get_hook_names():
                    remove_hook(hook.id)

    def add_pyproject_configs(self) -> None:
        """Add the tool's pyproject.toml configurations."""
        configs = self.get_pyproject_configs()
        if not configs:
            return

        first_addition = True
        for config in configs:
            try:
                set_config_value(config.id_keys, config.value)
            except PyProjectTOMLValueAlreadySetError:
                pass
            else:
                if first_addition:
                    tick_print(f"Adding {self.name} config to 'pyproject.toml'.")
                    first_addition = False

    def remove_pyproject_configs(self) -> None:
        """Remove all pyproject.toml configurations associated with this tool.

        This includes any tool-specific sections in the pyproject.toml file.
        If no configurations exist, this method has no effect.
        """
        # Collect all keys to remove
        keys_to_remove = [
            config.id_keys for config in self.get_pyproject_configs()
        ] + self.get_pyproject_id_keys()

        # Try to remove the first key to trigger the message
        first_removal = True
        for keys in keys_to_remove:
            try:
                remove_config_value(keys)
            except PyProjectTOMLValueMissingError:
                pass
            else:
                if first_removal:
                    tick_print(f"Removing {self.name} config from 'pyproject.toml'.")
                    first_removal = False


class CoverageTool(Tool):
    @property
    def name(self) -> str:
        return "coverage"

    @property
    def dev_deps(self) -> list[Dependency]:
        return [Dependency(name="coverage", extras=frozenset({"toml"}))]

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        return [
            PyProjectConfig(
                id_keys=["tool", "coverage", "run"],
                value={
                    "source": ["src"],
                    "omit": ["*/pytest-of-*/*"],
                },
            ),
            PyProjectConfig(
                id_keys=["tool", "coverage", "report"],
                value={
                    "exclude_also": [
                        "if TYPE_CHECKING:",
                        "raise AssertionError",
                        "raise NotImplementedError",
                        "assert_never(.*)",
                        "class .*\\bProtocol\\):",
                        "@(abc\\.)?abstractmethod",
                    ]
                },
            ),
        ]

    def get_pyproject_id_keys(self) -> list[list[str]]:
        return [["tool", "coverage"]]

    def get_managed_files(self) -> list[Path]:
        return [Path(".coveragerc")]


class DeptryTool(Tool):
    @property
    def name(self) -> str:
        return "deptry"

    @property
    def dev_deps(self) -> list[Dependency]:
        return [Dependency(name="deptry")]

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        return [
            LocalRepo(
                repo="local",
                hooks=[
                    HookDefinition(
                        id="deptry",
                        name="deptry",
                        entry="uv run --frozen deptry src",
                        language=Language("system"),
                        always_run=True,
                        pass_filenames=False,
                    )
                ],
            )
        ]

    def get_pyproject_id_keys(self) -> list[list[str]]:
        return [["tool", "deptry"]]


class PreCommitTool(Tool):
    @property
    def name(self) -> str:
        return "pre-commit"

    @property
    def dev_deps(self) -> list[Dependency]:
        return [Dependency(name="pre-commit")]

    def get_managed_files(self) -> list[Path]:
        return [Path(".pre-commit-config.yaml")]


class PyprojectFmtTool(Tool):
    @property
    def name(self) -> str:
        return "pyproject-fmt"

    @property
    def dev_deps(self) -> list[Dependency]:
        return [Dependency(name="pyproject-fmt")]

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        return [
            UriRepo(
                repo="https://github.com/tox-dev/pyproject-fmt",
                rev="v2.5.0",  # Manually bump this version when necessary
                hooks=[HookDefinition(id="pyproject-fmt")],
            )
        ]

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        return [
            PyProjectConfig(
                id_keys=["tool", "pyproject-fmt"],
                value={"keep_full_version": True},
            )
        ]

    def get_pyproject_id_keys(self) -> list[list[str]]:
        return [["tool", "pyproject-fmt"]]


class PytestTool(Tool):
    @property
    def name(self) -> str:
        return "pytest"

    @property
    def dev_deps(self) -> list[Dependency]:
        return [Dependency(name="pytest")]

    def get_extra_dev_deps(self) -> list[Dependency]:
        return [Dependency(name="pytest-cov")]

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        return [
            PyProjectConfig(
                id_keys=["tool", "pytest"],
                value={
                    "ini_options": {
                        "testpaths": ["tests"],
                        "addopts": [
                            "--import-mode=importlib",  # Now recommended https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#which-import-mode
                        ],
                        "filterwarnings": ["error"],
                    }
                },
            ),
        ]

    def get_associated_ruff_rules(self) -> list[str]:
        return ["PT"]

    def get_pyproject_id_keys(self) -> list[list[str]]:
        return [["tool", "pytest"]]

    def get_managed_files(self) -> list[Path]:
        return [Path("tests/conftest.py")]


class RequirementsTxtTool(Tool):
    @property
    def name(self) -> str:
        return "requirements.txt"

    @property
    def dev_deps(self) -> list[Dependency]:
        return []

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        return [
            LocalRepo(
                repo="local",
                hooks=[
                    HookDefinition(
                        id="uv-export",
                        name="uv-export",
                        files="^uv\\.lock$",
                        pass_filenames=False,
                        entry="uv export --frozen --no-dev --output-file=requirements.txt --quiet",
                        language=Language("system"),
                        require_serial=True,
                    )
                ],
            )
        ]

    def get_managed_files(self) -> list[Path]:
        return [Path("requirements.txt")]


class RuffTool(Tool):
    @property
    def name(self) -> str:
        return "Ruff"

    @property
    def dev_deps(self) -> list[Dependency]:
        return [Dependency(name="ruff")]

    def get_pre_commit_repos(self) -> list[LocalRepo | UriRepo]:
        return [
            LocalRepo(
                repo="local",
                hooks=[
                    HookDefinition(
                        id="ruff-format",
                        name="ruff-format",
                        entry="uv run --frozen ruff format --force-exclude",
                        language=Language("system"),
                        types_or=FileTypes(
                            [FileType("python"), FileType("pyi"), FileType("jupyter")]
                        ),
                        always_run=True,
                        require_serial=True,
                    ),
                ],
            ),
            LocalRepo(
                repo="local",
                hooks=[
                    HookDefinition(
                        id="ruff",
                        name="ruff",
                        entry="uv run --frozen ruff check --fix --force-exclude",
                        language=Language("system"),
                        types_or=FileTypes(
                            [FileType("python"), FileType("pyi"), FileType("jupyter")]
                        ),
                        always_run=True,
                        require_serial=True,
                    ),
                ],
            ),
        ]

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        return [
            PyProjectConfig(
                id_keys=["tool", "ruff"],
                value={
                    "src": ["src"],
                    "line-length": 88,
                    "lint": {"select": []},
                },
            )
        ]

    def get_pyproject_id_keys(self) -> list[list[str]]:
        return [["tool", "ruff"]]

    def get_managed_files(self) -> list[Path]:
        return [Path("ruff.toml"), Path(".ruff.toml")]


ALL_TOOLS: list[Tool] = [
    CoverageTool(),
    DeptryTool(),
    PreCommitTool(),
    PyprojectFmtTool(),
    PytestTool(),
    RequirementsTxtTool(),
    RuffTool(),
]
