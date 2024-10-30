from abc import abstractmethod
from pathlib import Path
from typing import Protocol

from usethis._console import console
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
    @abstractmethod
    def dev_deps(self) -> list[str]:
        """The name of the tool's development dependencies."""

    @abstractmethod
    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        """Get the pre-commit repository configuration for the tool.

        Raises:
            NotImplementedError: If the tool does not have a pre-commit configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        """Get the pyproject configurations for the tool.

        Raises:
            NotImplementedError: If the tool does not have a pyproject configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def get_associated_ruff_rules(self) -> list[str]:
        """Get the ruff rule codes associated with the tool.

        Raises:
            NotImplementedError: If the tool does not have associated ruff rules.
        """
        raise NotImplementedError

    def is_used(self) -> bool:
        """Whether the tool is being used in the current project."""
        return any(is_dep_in_any_group(dep) for dep in self.dev_deps)

    def add_pre_commit_repo_config(self) -> None:
        """Add the tool's pre-commit configuration."""
        try:
            repo_config = self.get_pre_commit_repo_config()
        except NotImplementedError:
            return

        add_pre_commit_config()

        # Add the config for this specific tool.
        first_time_adding = True
        for hook in repo_config.hooks:
            if hook.id not in get_hook_names():
                # Need to add this hook, it is missing.
                if first_time_adding:
                    console.tick_print(
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
        try:
            repo_config = self.get_pre_commit_repo_config()
        except NotImplementedError:
            return

        # Remove the config for this specific tool.
        first_removal = True
        for hook in repo_config.hooks:
            if hook.id in get_hook_names():
                if first_removal:
                    console.tick_print(
                        f"Removing {self.name} config from '.pre-commit-config.yaml'."
                    )
                    first_removal = False
                remove_hook(hook.id)

    def add_pyproject_configs(self) -> None:
        """Add the tool's pyproject.toml configurations."""

        try:
            configs = self.get_pyproject_configs()
        except NotImplementedError:
            return

        first_addition = True
        for config in configs:
            try:
                set_config_value(config.id_keys, config.main_contents)
            except ConfigValueAlreadySetError:
                pass
            else:
                if first_addition:
                    console.tick_print(
                        f"Adding {self.name} config to 'pyproject.toml'."
                    )
                    first_addition = False

    def remove_pyproject_configs(self) -> None:
        """Remove the tool's pyproject.toml configuration."""
        try:
            configs = self.get_pyproject_configs()
        except NotImplementedError:
            return

        first_removal = True
        for config in configs:
            try:
                remove_config_value(config.id_keys)
            except ConfigValueMissingError:
                pass
            else:
                if first_removal:
                    console.tick_print(
                        f"Removing {self.name} config from 'pyproject.toml'."
                    )
                    first_removal = False


class PreCommitTool(Tool):
    @property
    def name(self) -> str:
        return "pre-commit"

    @property
    def dev_deps(self) -> list[str]:
        return ["pre-commit"]

    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        raise NotImplementedError

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        raise NotImplementedError

    def get_associated_ruff_rules(self) -> list[str]:
        raise NotImplementedError

    def is_used(self) -> bool:
        return (
            any(is_dep_in_any_group(dep) for dep in self.dev_deps)
            or (Path.cwd() / ".pre-commit-config.yaml").exists()
        )


class DeptryTool(Tool):
    @property
    def name(self) -> str:
        return "deptry"

    @property
    def dev_deps(self) -> list[str]:
        return ["deptry"]

    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        return PreCommitRepoConfig(
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

    def get_pyproject_configs(self) -> list[PyProjectConfig]:
        raise NotImplementedError

    def get_associated_ruff_rules(self) -> list[str]:
        raise NotImplementedError


class RuffTool(Tool):
    @property
    def name(self) -> str:
        return "ruff"

    @property
    def dev_deps(self) -> list[str]:
        return ["ruff"]

    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        return PreCommitRepoConfig(
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

    def get_associated_ruff_rules(self) -> list[str]:
        return [
            "C4",
            "E4",
            "E7",
            "E9",
            "F",
            "FURB",
            "I",
            "PLE",
            "PLR",
            "RUF",
            "SIM",
            "UP",
        ]

    def is_used(self) -> bool:
        pyproject = read_pyproject_toml()

        try:
            pyproject["tool"]["ruff"]
        except KeyError:
            is_pyproject_config = False
        else:
            is_pyproject_config = True

        is_ruff_toml_config = (Path.cwd() / "ruff.toml").exists() or (
            Path.cwd() / ".ruff.toml"
        ).exists()

        return (
            any(is_dep_in_any_group(dep) for dep in self.dev_deps)
            or is_pyproject_config
            or is_ruff_toml_config
        )


class PytestTool(Tool):
    @property
    def name(self) -> str:
        return "pytest"

    @property
    def dev_deps(self) -> list[str]:
        return ["pytest", "pytest-md", "pytest-cov", "coverage[toml]"]

    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        raise NotImplementedError

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

    def is_used(self) -> bool:
        pyproject = read_pyproject_toml()

        try:
            pyproject["tool"]["pytest"]
        except KeyError:
            is_pyproject_config = False
        else:
            is_pyproject_config = True

        is_conftest = (Path.cwd() / "tests" / "conftest.py").exists()

        return (
            any(is_dep_in_any_group(dep) for dep in self.dev_deps)
            or is_pyproject_config
            or is_conftest
        )


ALL_TOOLS: list[Tool] = [PreCommitTool(), DeptryTool(), RuffTool(), PytestTool()]
