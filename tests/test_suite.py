import sys
from pathlib import Path

from git import InvalidGitRepositoryError, Repo

from _test import change_cwd
from usethis._config_file import files_manager
from usethis._file.pyproject_toml.requires_python import get_requires_python


class PytestSuiteConfigurationError(Exception):
    pass


def test_uv_init_not_git_repo(uv_init_dir: Path):
    # We shouldn't be in a git repo when running uv_init_dir, only uv_init_repo_dir
    # should be in a git repo
    # If we don't do this, we can have test interference when installing pre-commit,
    # which looks in parents.
    try:
        repo = Repo(uv_init_dir, search_parent_directories=True)
    except InvalidGitRepositoryError:
        pass
    else:
        path = repo.working_tree_dir
        msg = (
            f"{path} is a git repository, but it shouldn't be for uv_init_dir fixture."
        )
        raise PytestSuiteConfigurationError(msg)


def test_uv_init_dir_requires_python_compatible(uv_init_dir: Path):
    # The uv_init_dir fixture should create a project whose requires-python is
    # compatible with the Python version running the test suite. Otherwise, uv
    # commands run in the fixture directory will fail trying to locate an
    # interpreter that doesn't match the test runner's Python.
    with change_cwd(uv_init_dir), files_manager():
        specifier = get_requires_python()

    current_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    if current_version not in specifier:
        requires_python_str = str(specifier)
        msg = (
            f"The uv_init_dir fixture has requires-python = '{requires_python_str}', "
            f"which is not satisfied by the current Python version {current_version}. "
            f"Update the _uv_init_dir fixture in conftest.py to use the current Python "
            f"version so that uv commands run in this directory work correctly."
        )
        raise PytestSuiteConfigurationError(msg)
