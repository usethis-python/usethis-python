import subprocess
from abc import abstractmethod
from pathlib import Path
from typing import Protocol

import mergedeep
import tomlkit

from usethis import console
from usethis._pre_commit.config import HookConfig, PreCommitRepoConfig
from usethis._pre_commit.core import (
    add_single_hook,
    ensure_pre_commit_config,
    get_hook_names,
)
from usethis._pyproject.config import PyProjectConfig
from usethis._uv.deps import get_dev_deps


class Tool(Protocol):
    @property
    @abstractmethod
    def pypi_name(self) -> str:
        """The name of the tool on PyPI."""

    @property
    def name(self) -> str:
        """The name of the tool, for display purposes."""
        return self.pypi_name

    @abstractmethod
    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        """Get the pre-commit repository configuration for the tool.

        Raises:
            NotImplementedError: If the tool does not have a pre-commit configuration.
        """
        raise NotImplementedError

    @abstractmethod
    def get_pyproject_config(self) -> PyProjectConfig:
        """Get the pyproject configuration for the tool.

        Raises:
            NotImplementedError: If the tool does not have a pyproject configuration.
        """
        raise NotImplementedError

    def is_used(self) -> bool:
        """Whether the tool is being used in the current project."""
        return self.pypi_name in get_dev_deps(Path.cwd())

    def add_pre_commit_repo_config(self) -> None:
        """Add the tool's pre-commit configuration."""
        try:
            repo_config = self.get_pre_commit_repo_config()
        except NotImplementedError:
            return

        ensure_pre_commit_config()

        # Add the config for this specific tool.
        first_time_adding = True
        for hook in repo_config.hooks:
            if hook.id not in get_hook_names(Path.cwd()):
                # Need to add this hook, it is missing.
                if first_time_adding:
                    console.print(
                        f"✔ Adding {self.name} config to .pre-commit-config.yaml",
                        style="green",
                    )
                    first_time_adding = False

                add_single_hook(
                    PreCommitRepoConfig(
                        repo=repo_config.repo, rev=repo_config.rev, hooks=[hook]
                    )
                )

    def add_pyproject_config(self) -> None:
        """Add the tool's pyproject.toml configuration."""

        try:
            config = self.get_pyproject_config()
        except NotImplementedError:
            return

        pyproject = tomlkit.parse((Path.cwd() / "pyproject.toml").read_text())

        # Exit early if the configuration is already present.
        try:
            p = pyproject
            for key in config.id_keys:
                p = p[key]
        except KeyError:
            pass
        else:
            # The configuration is already present.
            return

        console.print(
            f"✔ Adding {self.pypi_name} configuration to pyproject.toml", style="green"
        )

        # The old configuration should be kept for all ID keys except the final/deepest
        # one which shouldn't exist anyway since we checked as much, above. For example,
        # If there is [tool.ruff] then we shouldn't overwrite it with [tool.deptry];
        # they should coexist. So under the "tool" key, we need to merge the two dicts.
        pyproject = mergedeep.merge(pyproject, config.contents)

        (Path.cwd() / "pyproject.toml").write_text(tomlkit.dumps(pyproject))

    def ensure_dev_dep(self) -> None:
        """Add the tool as a development dependency, if it is not already."""
        console.print(
            f"✔ Ensuring {self.pypi_name} is a development dependency", style="green"
        )
        subprocess.run(["uv", "add", "--dev", "--quiet", self.pypi_name], check=True)


class PreCommitTool(Tool):
    @property
    def pypi_name(self) -> str:
        return "pre-commit"

    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        raise NotImplementedError

    def get_pyproject_config(self) -> PyProjectConfig:
        raise NotImplementedError


class DeptryTool(Tool):
    @property
    def pypi_name(self) -> str:
        return "deptry"

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

    def get_pyproject_config(self) -> PyProjectConfig:
        raise NotImplementedError


class RuffTool(Tool):
    @property
    def pypi_name(self) -> str:
        return "ruff"

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

    def get_pyproject_config(self) -> PyProjectConfig:
        return PyProjectConfig(
            id_keys=["tool", "ruff"],
            main_contents={
                "src": ["src"],
                "line-length": 88,
                "lint": {
                    "select": [
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
                },
            },
        )


ALL_TOOLS: list[Tool] = [PreCommitTool(), DeptryTool(), RuffTool()]
