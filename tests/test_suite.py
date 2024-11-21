from pathlib import Path


class TestSuiteConfigurationError(Exception):
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
            raise TestSuiteConfigurationError(msg)
