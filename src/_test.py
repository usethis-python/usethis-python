"""Test utilities and fixtures for the usethis test suite."""

from __future__ import annotations

import copy
import os
import socket
from contextlib import contextmanager
from pathlib import Path
from typing import IO, TYPE_CHECKING

import requests
from requests.exceptions import RequestException
from ruamel.yaml.error import YAMLError
from typer.testing import CliRunner as TyperCliRunner  # noqa: TID251
from typing_extensions import assert_never, override

from usethis._backend.uv.call import call_uv_subprocess
from usethis._config import usethis_config
from usethis._core.tool import (
    use_codespell,
    use_coverage_py,
    use_deptry,
    use_import_linter,
    use_mkdocs,
    use_pre_commit,
    use_pyproject_fmt,
    use_pyproject_toml,
    use_pytest,
    use_requirements_txt,
    use_ruff,
    use_tach,
    use_ty,
    use_zensical,
)
from usethis._fallback import FALLBACK_PRE_COMMIT_VERSION
from usethis._file.yaml.errors import YAMLDecodeError
from usethis._file.yaml.io_ import get_yaml_document
from usethis._integrations.pre_commit.hooks import hook_ids_are_equivalent
from usethis._integrations.pre_commit.version import get_minimum_pre_commit_version
from usethis._tool.impl.base.codespell import CodespellTool
from usethis._tool.impl.base.coverage_py import CoveragePyTool
from usethis._tool.impl.base.deptry import DeptryTool
from usethis._tool.impl.base.import_linter import ImportLinterTool
from usethis._tool.impl.base.mkdocs import MkDocsTool
from usethis._tool.impl.base.pre_commit import PreCommitTool
from usethis._tool.impl.base.pyproject_fmt import PyprojectFmtTool
from usethis._tool.impl.base.pyproject_toml import PyprojectTOMLTool
from usethis._tool.impl.base.pytest import PytestTool
from usethis._tool.impl.base.requirements_txt import RequirementsTxtTool
from usethis._tool.impl.base.ruff import RuffTool
from usethis._tool.impl.base.tach import TachTool
from usethis._tool.impl.base.ty import TyTool
from usethis._tool.impl.base.zensical import ZensicalTool
from usethis.errors import UsethisError

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping, Sequence

    from click.testing import Result
    from typer import Typer

    from usethis._file.yaml.io_ import YAMLDocument
    from usethis._integrations.pre_commit import schema
    from usethis._tool.all_ import SupportedToolType


@contextmanager
def change_cwd(new_dir: Path) -> Generator[None, None, None]:
    """Change the working directory temporarily.

    Args:
        new_dir: The new directory to change to.
    """
    old_dir = Path.cwd()
    os.chdir(new_dir)
    try:
        with usethis_config.set(project_dir=new_dir):
            yield
    finally:
        os.chdir(old_dir)


def is_offline() -> bool:
    """Return True if the current environment has no internet connectivity."""
    try:
        # Connect to Google's DNS server
        s = socket.create_connection(("8.8.8.8", 53), timeout=3)
    except OSError:
        return True
    else:
        s.close()
        return False


class CliRunner(TyperCliRunner):
    def invoke_safe(
        self,
        app: Typer,
        args: str | Sequence[str] | None = None,
        input: bytes | str | IO[str] | None = None,  # noqa: A002
        env: Mapping[str, str] | None = None,
        color: bool = False,
        **extra: object,
    ) -> Result:
        return self.invoke(
            app,
            args=args,
            input=input,
            env=env,
            catch_exceptions=False,
            color=color,
            **extra,
        )

    @override
    def invoke(
        self,
        app: Typer,
        args: str | Sequence[str] | None = None,
        input: bytes | str | IO[str] | None = None,
        env: Mapping[str, str] | None = None,
        catch_exceptions: bool = True,
        color: bool = False,
        **extra: object,
    ) -> Result:
        if catch_exceptions:
            msg = "`catch_exceptions=True` is forbidden in usethis tests. Use `.invoke_safe()` instead."
            raise NotImplementedError(msg)

        return super().invoke(
            app,
            args=args,
            input=input,
            env=env,
            catch_exceptions=catch_exceptions,
            color=color,
            **extra,
        )


def get_pre_commit_version() -> str:
    """Get an inferred pre-commit version for usethis to target.

    If no version can be inferred, a hard-coded version is used, corresponding to a
    recent release (see `FALLBACK_PRE_COMMIT_VERSION`).
    """
    version = get_minimum_pre_commit_version()
    if version is not None:
        return version
    return FALLBACK_PRE_COMMIT_VERSION


def hooks_are_equivalent(
    hook: schema.HookDefinition, other: schema.HookDefinition
) -> bool:
    """Check if two hooks are equivalent."""
    if hook_ids_are_equivalent(hook.id, other.id):
        return True

    # Same contents, different name
    hook = hook.model_copy()
    hook.name = other.name
    return hook == other


class GitHubTagError(UsethisError):
    """Custom exception for GitHub tag-related errors."""


class NoGitHubTagsFoundError(GitHubTagError):
    """Custom exception raised when no tags are found."""


def get_github_latest_tag(owner: str, repo: str) -> str:
    """Get the name of the most recent tag on the default branch of a GitHub repository.

    Args:
        owner: GitHub repository owner (username or organization).
        repo: GitHub repository name.

    Returns:
        The name of the most recent tag of the repository.

    Raises:
        GitHubTagError: If there's an issue fetching the tags from the GitHub API.
        NoGitHubTagsFoundError: If the repository has no tags.
    """
    # GitHub API URL for repository tags
    api_url = f"https://api.github.com/repos/{owner}/{repo}/tags"

    # Fetch the tags using the GitHub API
    try:
        response = requests.get(api_url, timeout=1)
        response.raise_for_status()  # Raise an error for HTTP issues
    except RequestException as err:
        msg = f"Failed to fetch tags from GitHub API:\n{err}"
        raise GitHubTagError(msg) from None

    tags = response.json()

    if not tags:
        msg = f"No tags found for repository '{owner}/{repo}'."
        raise NoGitHubTagsFoundError(msg)

    # Most recent tag's name
    return tags[0]["name"]


@contextmanager
def edit_yaml(
    yaml_path: Path,
    *,
    guess_indent: bool = True,
) -> Generator[YAMLDocument, None, None]:
    """A context manager to modify a YAML file in-place, with managed read and write."""
    with read_yaml(yaml_path, guess_indent=guess_indent) as yaml_document:
        original_content = copy.deepcopy(yaml_document.content)

        yield yaml_document

        if yaml_document.content == original_content:
            return

        yaml_document.roundtripper.dump(yaml_document.content, stream=yaml_path)


@contextmanager
def read_yaml(
    yaml_path: Path,
    *,
    guess_indent: bool = True,
) -> Generator[YAMLDocument, None, None]:
    """A context manager to read a YAML file."""
    with yaml_path.open(mode="r", encoding="utf-8") as f:
        try:
            yaml_document = get_yaml_document(f, guess_indent=guess_indent)
        except YAMLError as err:
            msg = f"Error reading '{yaml_path}':\n{err}"
            raise YAMLDecodeError(msg) from None

    yield yaml_document


def use_tool(  # noqa: PLR0912
    tool: SupportedToolType,
    *,
    remove: bool = False,
    how: bool = False,
) -> None:
    """General dispatch function to add or remove a tool to/from the project.

    This is mostly intended for situations when the exact tool being added is not known
    dynamically. If you know the specific tool you wish to add, it is strongly
    recommended to call the specific function directly, e.g. `use_codespell()`, etc.
    """
    # One might wonder why we don't just implement a `use` method on the Tool class
    # itself. Basically it's for architectural reasons: we want to keep a layer of
    # abstraction between the tool and the logic to actually configure it.
    # In the future, that might change if we can create a sufficiently generalized logic
    # for all tools such that bespoke choices on a per-tool basis are not required, and
    # all the logic is just deterministic based on the tool's properties/methods, etc.
    if isinstance(tool, CodespellTool):
        use_codespell(remove=remove, how=how)
    elif isinstance(tool, CoveragePyTool):
        use_coverage_py(remove=remove, how=how)
    elif isinstance(tool, DeptryTool):
        use_deptry(remove=remove, how=how)
    elif isinstance(tool, ImportLinterTool):
        use_import_linter(remove=remove, how=how)
    elif isinstance(tool, MkDocsTool):
        use_mkdocs(remove=remove, how=how)
    elif isinstance(tool, PreCommitTool):
        use_pre_commit(remove=remove, how=how)
    elif isinstance(tool, PyprojectFmtTool):
        use_pyproject_fmt(remove=remove, how=how)
    elif isinstance(tool, PyprojectTOMLTool):
        use_pyproject_toml(remove=remove, how=how)
    elif isinstance(tool, PytestTool):
        use_pytest(remove=remove, how=how)
    elif isinstance(tool, RequirementsTxtTool):
        use_requirements_txt(remove=remove, how=how)
    elif isinstance(tool, RuffTool):
        use_ruff(remove=remove, how=how)
    elif isinstance(tool, TachTool):
        use_tach(remove=remove, how=how)
    elif isinstance(tool, TyTool):
        use_ty(remove=remove, how=how)
    elif isinstance(tool, ZensicalTool):
        use_zensical(remove=remove, how=how)
    else:
        # Having the assert_never here is effectively a way of testing cases are
        # exhaustively handled, which ensures it is kept up to date with ALL_TOOLS,
        # together with the type annotation on ALL_TOOLS itself. That's why this
        # function is implemented as a series of `if` statements rather than a
        # dictionary or similar alternative.
        assert_never(tool)


def uv_python_pin(version: str) -> None:
    """Pin the Python version for the project using uv."""
    call_uv_subprocess(["python", "pin", version], change_toml=False)
