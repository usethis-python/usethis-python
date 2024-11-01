from abc import abstractmethod
from pathlib import Path
from typing import Protocol

from pydantic import TypeAdapter

from usethis._console import tick_print
from usethis._integrations.pre_commit.config import HookConfig, PreCommitRepoConfig
from usethis._integrations.pre_commit.core import add_pre_commit_config
from usethis._integrations.pre_commit.hooks import (
    add_hook,
    get_hook_names,
    remove_hook,
)
from usethis._integrations.pyproject.config import PyProjectConfig
from usethis._integrations.pyproject.core import (
    ConfigValueAlreadySetError,
    ConfigValueMissingError,
    remove_config_value,
    set_config_value,
)
from usethis._integrations.pyproject.io import read_pyproject_toml
from usethis._integrations.uv.deps import is_dep_in_any_group


class Tool(Protocol):
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool, for display purposes."""

    @property
    def dev_deps(self) -> list[str]:
        """The name of the tool's development dependencies."""
        return []

    def get_pre_commit_repo_configs(self) -> list[PreCommitRepoConfig]:
        """Get the pre-commit repository configurations for the tool."""
        return []

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        """Get the pyproject configurations for the tool."""
        return []

    def get_associated_ruff_rules(self) -> list[str]:
        """Get the ruff rule codes associated with the tool."""
        return []

    def get_unique_dev_deps(self) -> list[str]:
        """Any development dependencies only used by this tool (not shared)."""
        return self.dev_deps

    def get_managed_files(self) -> list[Path]:
        """Get (relative) paths to files managed by the tool."""
        return []

    def get_pyproject_id_keys(self) -> list[list[str]]:
        """Get keys for any pyproject.toml sections only used by this tool (not shared)."""
        return []

    def is_used(self) -> bool:
        """Whether the tool is being used in the current project.

        Three heuristics are used by default:
        1. Whether any of the tool's development dependencies are in the project.
        2. Whether any of the tool's managed files are in the project.
        3. Whether any of the tool's managed pyproject.toml sections are present.
        """
        is_any_deps = any(is_dep_in_any_group(dep) for dep in self.dev_deps)
        is_any_files = False
        for file in self.get_managed_files():
            if file.exists() and file.is_file():
                is_any_files = True
                break

        pyproject = read_pyproject_toml()

        is_any_pyproject = False
        for id_keys in self.get_pyproject_id_keys():
            p = pyproject
            try:
                for key in id_keys:
                    TypeAdapter(dict).validate_python(p)
                    assert isinstance(p, dict)
                    p = p[key]
            except KeyError:
                pass
            else:
                is_any_pyproject = True
                break

        return is_any_deps or is_any_files or is_any_pyproject

    def add_pre_commit_repo_config(self) -> None:
        """Add the tool's pre-commit configuration."""
        repo_configs = self.get_pre_commit_repo_configs()

        if not repo_configs:
            return

        if len(repo_configs) > 1:
            raise NotImplementedError(
                "Multiple pre-commit repo configurations not yet supported."
            )
        repo_config = repo_configs[0]

        add_pre_commit_config()

        # Add the config for this specific tool.
        first_time_adding = True
        for hook in repo_config.hooks:
            if hook.id not in get_hook_names():
                # Need to add this hook, it is missing.
                if first_time_adding:
                    tick_print(
                        f"Adding {self.name} config to '.pre-commit-config.yaml'."
                    )
                    first_time_adding = False

                add_hook(
                    PreCommitRepoConfig(
                        repo=repo_config.repo, rev=repo_config.rev, hooks=[hook]
                    )
                )

    def remove_pre_commit_repo_config(self) -> None:
        """Remove the tool's pre-commit configuration."""
        repo_configs = self.get_pre_commit_repo_configs()

        if not repo_configs:
            return

        if len(repo_configs) > 1:
            raise NotImplementedError(
                "Multiple pre-commit repo configurations not yet supported."
            )
        repo_config = repo_configs[0]

        # Remove the config for this specific tool.
        first_removal = True
        for hook in repo_config.hooks:
            if hook.id in get_hook_names():
                if first_removal:
                    tick_print(
                        f"Removing {self.name} config from '.pre-commit-config.yaml'."
                    )
                    first_removal = False
                remove_hook(hook.id)

    def add_pyproject_configs(self) -> None:
        """Add the tool's pyproject.toml configurations."""

        configs = self.get_pyproject_configs()
        if not configs:
            return

        first_addition = True
        for config in configs:
            try:
                set_config_value(config.id_keys, config.main_contents)
            except ConfigValueAlreadySetError:
                pass
            else:
                if first_addition:
                    tick_print(f"Adding {self.name} config to 'pyproject.toml'.")
                    first_addition = False

    def remove_pyproject_configs(self) -> None:
        """Remove the tool's pyproject.toml configuration."""

        configs = self.get_pyproject_configs()
        if not configs:
            return

        first_removal = True
        for config in configs:
            try:
                remove_config_value(config.id_keys)
            except ConfigValueMissingError:
                pass
            else:
                if first_removal:
                    tick_print(f"Removing {self.name} config from 'pyproject.toml'.")
                    first_removal = False


class DeptryTool(Tool):
    @property
    def name(self) -> str:
        return "deptry"

    @property
    def dev_deps(self) -> list[str]:
        return ["deptry"]

    def get_pre_commit_repo_configs(self) -> list[PreCommitRepoConfig]:
        return [
            PreCommitRepoConfig(
                repo="local",
                hooks=[
                    HookConfig(
                        id="deptry",
                        name="deptry",
                        entry="uv run --frozen deptry src",
                        language="system",
                        always_run=True,
                        pass_filenames=False,
                    )
                ],
            )
        ]


class PreCommitTool(Tool):
    @property
    def name(self) -> str:
        return "pre-commit"

    @property
    def dev_deps(self) -> list[str]:
        return ["pre-commit"]

    def get_managed_files(self):
        return [Path(".pre-commit-config.yaml")]


class PyprojectFmtTool(Tool):
    @property
    def name(self) -> str:
        return "pyproject-fmt"

    @property
    def dev_deps(self) -> list[str]:
        return ["pyproject-fmt"]

    def get_pre_commit_repo_configs(self) -> list[PreCommitRepoConfig]:
        return [
            PreCommitRepoConfig(
                repo="https://github.com/tox-dev/pyproject-fmt",
                rev="v2.5.0",  # Manually bump this version when necessary
                hooks=[HookConfig(id="pyproject-fmt")],
            )
        ]

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        return [
            PyProjectConfig(
                id_keys=["tool", "pyproject-fmt"],
                main_contents={"keep_full_version": True},
            )
        ]

    def get_pyproject_id_keys(self):
        return [["tool", "pyproject-fmt"]]


class PytestTool(Tool):
    @property
    def name(self) -> str:
        return "pytest"

    @property
    def dev_deps(self) -> list[str]:
        return ["pytest", "pytest-cov", "coverage[toml]"]

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        return [
            PyProjectConfig(
                id_keys=["tool", "pytest"],
                main_contents={
                    "ini_options": {
                        "testpaths": ["tests"],
                        "addopts": [
                            "--import-mode=importlib",  # Now recommended https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#which-import-mode
                        ],
                    }
                },
            ),
            PyProjectConfig(
                id_keys=["tool", "coverage", "run"],
                main_contents={
                    "source": ["src"],
                    "omit": ["*/pytest-of-*/*"],
                },
            ),
        ]

    def get_associated_ruff_rules(self) -> list[str]:
        return ["PT"]

    def get_unique_dev_deps(self):
        return ["pytest", "pytest-cov"]

    def get_pyproject_id_keys(self):
        return [["tool", "pytest"]]

    def get_managed_files(self):
        return [Path("tests/conftest.py")]


class RuffTool(Tool):
    @property
    def name(self) -> str:
        return "ruff"

    @property
    def dev_deps(self) -> list[str]:
        return ["ruff"]

    def get_pre_commit_repo_configs(self) -> list[PreCommitRepoConfig]:
        return [
            PreCommitRepoConfig(
                repo="local",
                hooks=[
                    HookConfig(
                        id="ruff-format",
                        name="ruff-format",
                        entry="uv run --frozen ruff format",
                        language="system",
                        always_run=True,
                        pass_filenames=False,
                    ),
                    HookConfig(
                        id="ruff-check",
                        name="ruff-check",
                        entry="uv run --frozen ruff check --fix",
                        language="system",
                        always_run=True,
                        pass_filenames=False,
                    ),
                ],
            )
        ]

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        return [
            PyProjectConfig(
                id_keys=["tool", "ruff"],
                main_contents={
                    "src": ["src"],
                    "line-length": 88,
                    "lint": {"select": []},
                },
            )
        ]

    def get_pyproject_id_keys(self):
        return [["tool", "ruff"]]

    def get_managed_files(self):
        return [Path("ruff.toml"), Path(".ruff.toml")]


ALL_TOOLS: list[Tool] = [
    DeptryTool(),
    PreCommitTool(),
    PyprojectFmtTool(),
    PytestTool(),
    RuffTool(),
]
