"""pytest directory and configuration setup."""

from __future__ import annotations

import shutil

from usethis._config import usethis_config
from usethis._console import instruct_print, tick_print

_EXAMPLE_TEST_CONTENT = '''\
def test_add():
    """An example test - replace with your own tests!"""
    assert 1 + 1 == 2
'''


def add_pytest_dir() -> None:
    """Create the tests directory and conftest.py if they do not already exist."""
    tests_dir = usethis_config.cpd() / "tests"

    if not tests_dir.exists():
        tick_print("Creating '/tests'.")
        tests_dir.mkdir()

    if (tests_dir / "conftest.py").exists():
        # Early exit; conftest.py already exists
        return

    tick_print("Writing '/tests/conftest.py'.")
    (tests_dir / "conftest.py").write_text(
        "collect_ignore_glob = []\npytest_plugins = []\n", encoding="utf-8"
    )


def add_example_test() -> None:
    """Create an example test file in the tests directory if it does not already exist."""
    tests_dir = usethis_config.cpd() / "tests"

    if (tests_dir / "test_example.py").exists():
        # Early exit; example test already exists
        return

    tick_print("Writing '/tests/test_example.py'.")
    (tests_dir / "test_example.py").write_text(_EXAMPLE_TEST_CONTENT, encoding="utf-8")


def remove_pytest_dir() -> None:
    """Remove the tests directory if it contains only managed files."""
    tests_dir = usethis_config.cpd() / "tests"

    if not tests_dir.exists():
        # Early exit; tests directory does not exist
        return

    managed_files = {tests_dir / "conftest.py", tests_dir / "test_example.py"}
    if set(tests_dir.iterdir()) <= managed_files:
        # The only files in the directory are managed files
        tick_print("Removing '/tests'.")
        shutil.rmtree(tests_dir)
    else:
        instruct_print("Reconfigure the '/tests' directory to run without pytest.")
        # Note we don't actually remove the directory, just explain what needs to be done.
