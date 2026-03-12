---
name: usethis-python-module-layout-modify
description: Modify the Python module layout (create, move, rename, or delete modules)
compatibility: usethis, Python, pytest
license: MIT
metadata:
  version: "1.3
---

# Modifying the module layout for Python projects

## Procedure

When creating, moving, renaming, or deleting Python modules in the `src` directory:

1. Make the necessary changes to the module layout in the `src` directory.
2. Update the test directory structure to match any changes in the `src` directory, validate with `uv run pytest tests\test_suite.py::test_skeleton_matches`.
3. Check for any broken references (e.g. import statements) and fix them.
4. Update the Import Linter contracts using the `usethis-qa-import-linter` skill.

## Updating the test directory structure

Any changes in the `src` directory should be matched in the `tests` directory. For example, if we had `src/usethis/_a.py` and were splitting it into new submodules `usethis/_a/b.py` and `usethis/_a/c.py`, we would also need to split `tests/test_a.py` into `tests/_a_/test_b.py` and `tests/_a_/test_c.py`.

You should validate the changes are successful via the command `uv run pytest tests\test_suite.py::test_skeleton_matches`.

## Strategy for broken references

Whenever:

- creating a new module and moving code into it from another module
- moving an existing module to a different location
- renaming an existing module

There is the possibility of breaking references (e.g. import statements). Make sure to check for these and fix any.

### Preserving backwards compatibility

usethis adheres to a convention where modules starting with an underscore (e.g. `usethis._internal`) are considered internal (including all their submodules) and are not part of the public API. As such, it is not necessary to maintain backwards compatibility for these modules.

For example, if we had `src/usethis/_a.py` and were splitting it into new submodules `usethis/_a/b.py` and `usethis/_a/c.py`, we would not need to maintain backwards compatibility for `usethis._a` (e.g. by keeping an `__init__.py` file with imports of the new submodules).

However, in other cases, backwards compatibility should be maintained.

## Updating Import Linter Contracts

Make sure to adhere to the Import Linter checks using the `usethis-qa-import-linter` skill.
