---
name: usethis-python-test
description: General guidelines for writing tests in the usethis project, including test class organization
compatibility: usethis, Python, pytest
license: MIT
metadata:
  version: "1.0"
---

# Python Test Guidelines

Use the `usethis-python-test-full-coverage` skill when you need to measure and verify test coverage. This skill covers general test organization and conventions.

## Test class organization

Tests are organized into nested pytest classes that mirror the structure of the code being tested. Understanding and following this convention is essential when adding new tests.

### Top-level classes: one per function or class under test

Each public function or class in a module gets its own top-level test class in the corresponding test file. Name it `Test<FunctionOrClassName>`.

For example, if a module defines `add_deps_to_group()` and `remove_deps_from_group()`, the test file should have `TestAddDepsToGroup` and `TestRemoveDepsFromGroup` as separate top-level classes.

### Nested classes: group by method, operation, or variant

Within a top-level test class, use nested classes to organize tests by sub-concern. Common nesting patterns include:

- **By method or operation:** `TestMyClass` contains `TestAdd` and `TestRemove` for add/remove operations on that class.
- **By scenario or condition:** `TestIgnoreRules` contains `TestWhenRulesAreNew`, `TestWhenSomeRulesAlreadyIgnored`, etc.
- **By variant or backend:** `TestAddDepsToGroup` contains `TestPoetry` and/or `TestUv` for backend-specific behavior of the same function.

### Adding variant-specific tests (e.g. backend tests)

When adding tests for a new variant of existing functionality (such as Poetry backend support for a function that already has uv tests), **nest the variant tests inside the existing top-level test class**. Do not create a new standalone top-level class.

For example, to add Poetry backend tests for `add_default_groups()`:

- **Correct:** Add a `TestPoetry` nested class inside the existing `TestAddDefaultGroups`.
- **Wrong:** Create a new top-level `TestAddDefaultGroupsPoetry` class.

This keeps all tests for the same function grouped together, making it easy to see all variants at a glance and ensuring consistent test coverage across backends.

### Nesting depth

Nesting can go two or three levels deep when the logical structure demands it. For example:

- Two levels: `TestCodespell` → `TestAdd` → `test_config()`
- Three levels: `TestPyprojectFmt` → `TestAdd` → `TestDeps` → `test_added()`

Use the minimum depth needed to clearly communicate the test's context. Avoid nesting beyond three levels.

### No docstrings on test classes or functions

Test classes and test functions should not have docstrings. The class and function names should be descriptive enough to communicate what is being tested.
