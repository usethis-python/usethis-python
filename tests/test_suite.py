from pathlib import Path

from git import InvalidGitRepositoryError, Repo


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
