from __future__ import annotations

import shutil

from usethis._config import usethis_config
from usethis._console import box_print, tick_print


def add_pytest_dir() -> None:
    tests_dir = usethis_config.cpd() / "tests"

    if not tests_dir.exists():
        tick_print("Creating '/tests'.")
        tests_dir.mkdir()

    if (tests_dir / "conftest.py").exists():
        # Early exit; conftest.py already exists
        return

    tick_print("Writing '/tests/conftest.py'.")
    (tests_dir / "conftest.py").write_text(
        "collect_ignore_glob = []\npytest_plugins = []\n"
    )


def remove_pytest_dir() -> None:
    tests_dir = usethis_config.cpd() / "tests"

    if not tests_dir.exists():
        # Early exit; tests directory does not exist
        return

    if set(tests_dir.iterdir()) <= {tests_dir / "conftest.py"}:
        # The only file in the directory is conftest.py
        tick_print("Removing '/tests'.")
        shutil.rmtree(tests_dir)
    else:
        box_print("Reconfigure the '/tests' directory to run without pytest.")
        # Note we don't actually remove the directory, just explain what needs to be done.
