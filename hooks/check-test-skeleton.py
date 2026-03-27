"""Check that every test file has a matching source module.

For each tests/usethis/**/test_*.py file, at least one of the following source
paths must exist under src/usethis/:

- Direct name match (test_foo.py -> foo.py)
- Underscore-prefixed match (test_foo.py -> _foo.py)
- Parent-stripped match (test_parent_foo.py -> foo.py)
- Underscore parent-stripped match (test_parent_foo.py -> _foo.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

TESTS_DIR = Path("tests/usethis")
SRC_DIR = Path("src")


def main() -> int:
    if not TESTS_DIR.is_dir():
        print(f"ERROR: {TESTS_DIR} directory not found.", file=sys.stderr)
        return 1

    errors: list[str] = []

    for test_py in sorted(TESTS_DIR.rglob("test_*.py")):
        path = SRC_DIR / test_py.relative_to("tests")
        std_path = path.parent / path.name.removeprefix("test_")
        underscore_path = path.parent / ("_" + path.name.removeprefix("test_"))
        parent_prefix = "test_" + path.parent.name.strip("_") + "_"
        std_parent_path = path.parent / path.name.removeprefix(parent_prefix)
        underscore_parent_path = path.parent / (
            "_" + path.name.removeprefix(parent_prefix)
        )

        if (
            not std_path.exists()
            and not underscore_path.exists()
            and not std_parent_path.exists()
            and not underscore_parent_path.exists()
        ):
            errors.append(
                f"  {test_py}\n"
                f"    Expected one of:\n"
                f"      {std_path}\n"
                f"      {underscore_path}\n"
                f"      {std_parent_path}\n"
                f"      {underscore_parent_path}"
            )

    if errors:
        print(
            "ERROR: The following test files have no matching source module:",
            file=sys.stderr,
        )
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("All test files have matching source modules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
