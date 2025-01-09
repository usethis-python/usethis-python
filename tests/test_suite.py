from pathlib import Path

from git import InvalidGitRepositoryError, Repo


class PytestSuiteConfigurationError(Exception):
    pass


def test_skeleton_matches():
    # If a tests/usethis/**/test_*.py exists, it should have a matching module named
    # src/usethis/**/*.py

    for test_py in Path("tests/usethis").rglob("test_*.py"):
        path = Path("src") / test_py.relative_to("tests")
        std_path = path.parent / path.name.removeprefix("test_")
        underscore_path = path.parent / path.name.removeprefix("test")

        if not std_path.exists() and not underscore_path.exists():
            msg = (
                f"{std_path} expected to exist by test suite structure, but is missing"
            )
            raise PytestSuiteConfigurationError(msg)


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
        msg = f"{path} is a git repository, but it shouldn't be for uv_init_dir fixture"
        raise PytestSuiteConfigurationError(msg)
