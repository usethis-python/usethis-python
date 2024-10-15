import subprocess
from abc import abstractmethod
from pathlib import Path
from typing import Protocol

import tomlkit
from packaging.requirements import Requirement
from pydantic import TypeAdapter

from usethis import console
from usethis._deptry.core import PRE_COMMIT_NAME as DEPTRY_PRE_COMMIT_NAME
from usethis._pre_commit.config import HookConfig, PreCommitRepoConfig
from usethis._pre_commit.core import (
    add_single_hook,
    get_hook_names,
    make_pre_commit_config,
)


class Tool(Protocol):
    @property
    @abstractmethod
    def pypi_name(self) -> str:
        """The name of the tool on PyPI."""

    @property
    @abstractmethod
    def pre_commit_name(self) -> str:
        """The name of the hook to be used in the pre-commit configuration.

        Raises:
            NotImplementedError: If the tool does not have a pre-commit configuration.
        """

        raise NotImplementedError

    @abstractmethod
    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        """Get the pre-commit repository configuration for the tool.

        Returns:
            The pre-commit repository configuration.

        Raises:
            NotImplementedError: If the tool does not have a pre-commit configuration.
        """
        raise NotImplementedError

    def is_used(self) -> bool:
        """Whether the tool is being used in the current project."""
        return self.pypi_name in _get_dev_deps(Path.cwd())

    def add_pre_commit_repo_config(self) -> None:
        """Add the tool's pre-commit configuration."""
        # Create a new pre-commit config file if there isn't already one.
        if not (Path.cwd() / ".pre-commit-config.yaml").exists():
            make_pre_commit_config()

        try:
            pre_commit_name = self.pre_commit_name
            repo_config = self.get_pre_commit_repo_config()
        except NotImplementedError:
            return

        # Add the config for this specific tool.
        if pre_commit_name not in get_hook_names(Path.cwd()):
            console.print(
                f"✔ Adding {pre_commit_name} config to .pre-commit-config.yaml",
                style="green",
            )
            add_single_hook(repo_config)

    def ensure_dev_dep(self) -> None:
        """Add the tool as a development dependency, if it is not already."""
        console.print(
            f"✔ Ensuring {self.pypi_name} is a development dependency", style="green"
        )
        subprocess.run(["uv", "add", "--dev", "--quiet", self.pypi_name], check=True)


def _get_dev_deps(proj_dir: Path) -> list[str]:
    pyproject = tomlkit.parse((proj_dir / "pyproject.toml").read_text())
    req_strs = TypeAdapter(list[str]).validate_python(
        pyproject["tool"]["uv"]["dev-dependencies"]
    )
    reqs = [Requirement(req_str) for req_str in req_strs]
    return [req.name for req in reqs]


class PreCommitTool(Tool):
    @property
    def pypi_name(self) -> str:
        return "pre-commit"

    @property
    def pre_commit_name(self) -> str:
        raise NotImplementedError

    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        raise NotImplementedError


class DeptryTool(Tool):
    @property
    def pypi_name(self) -> str:
        return "deptry"

    @property
    def pre_commit_name(self) -> str:
        return DEPTRY_PRE_COMMIT_NAME

    def get_pre_commit_repo_config(self) -> PreCommitRepoConfig:
        return PreCommitRepoConfig(
            repo="local",
            hooks=[
                HookConfig(
                    id=self.pre_commit_name,
                    name=self.pre_commit_name,
                    entry="uv run --frozen deptry src",
                    language="system",
                    always_run=True,
                    pass_filenames=False,
                )
            ],
        )


ALL_TOOLS: list[Tool] = [PreCommitTool(), DeptryTool()]
