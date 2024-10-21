from pathlib import Path

from usethis import console


def add_pytest_dir():
    tests_dir = Path.cwd() / "tests"

    if not tests_dir.exists():
        console.print("✔ Creating '/tests'.", style="green")
        tests_dir.mkdir()

    if (tests_dir / "conftest.py").exists():
        # Early exit; conftest.py already exists
        return

    console.print("✔ Writing '/tests/conftest.py'.", style="green")
    (tests_dir / "conftest.py").write_text(
        "collect_ignore_glob = []\npytest_plugins = []\n"
    )


def remove_pytest_dir():
    tests_dir = Path.cwd() / "tests"

    if not tests_dir.exists():
        # Early exit; tests directory does not exist
        return

    console.print(
        "☐ Reconfigure the /tests directory to run without pytest", style="blue"
    )
    # Note we don't actually remove the directory, just explain what needs to be done.
