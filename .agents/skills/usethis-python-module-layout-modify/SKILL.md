---
name: usethis-python-module-layout-modify
description: Modify the Python module layout (create, move, rename, or delete modules)
compatibility: usethis, Python
license: MIT
metadata:
  version: "1.1"
---

# Modifying the module layout for Python projects

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
