---
name: usethis-python-test
description: General guidelines for writing tests in the usethis project, including test class organization
compatibility: usethis, Python, pytest
license: MIT
metadata:
  version: "1.2"
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

## Using `files_manager` in tests

The `files_manager()` context manager defers all configuration file writes until the context exits. This has important implications for how tests are structured, especially when subprocess calls are involved.

### When to exit `files_manager` before a subprocess

Any subprocess that reads configuration files from the filesystem (e.g. `ruff`, `pytest`, `pre-commit`, `deptry`, `codespell`) will **not** see in-memory changes made inside a `files_manager()` context. You must exit the context (flush writes to disk) before running the subprocess.

```python
# Correct: exit files_manager before the subprocess reads config from disk
with change_cwd(tmp_path), files_manager():
    use_ruff()

call_uv_subprocess(["run", "ruff", "check", "."], change_toml=False)
```

```python
# Wrong: subprocess runs inside the context, but config hasn't been flushed yet
with change_cwd(tmp_path), files_manager():
    use_ruff()
    call_uv_subprocess(["run", "ruff", "check", "."], change_toml=False)
    # ruff may not see the configuration written by use_ruff()
```

### When it is safe to stay inside the same context

Multiple usethis function calls that operate through `FileManager`-based access (not subprocesses) can safely share a single `files_manager()` context. They see each other's uncommitted in-memory changes via `get()` and `commit()`.

```python
# Safe: both functions use FileManager access, no subprocess involved
with change_cwd(tmp_path), files_manager():
    use_ruff()
    use_deptry()
    # Both tools' config changes are visible to each other in memory
```

### Rule of thumb

- **FileManager-only operations** (e.g. `use_*` functions, `get_deps_from_group`, assertions on config state): safe to combine in one context.
- **Subprocess calls** (e.g. `call_uv_subprocess`, `subprocess.run`, `call_subprocess`): require an atomic write first, so exit the `files_manager` context before running them.

## Clearing functools caches between tests

When `@functools.cache` is added to a production function (see `usethis-python-code`), its cache must be cleared between tests to prevent one test's cached result from polluting subsequent tests.

### Procedure

When adding `@functools.cache` to a function:

1. Import the function at the top of `tests/conftest.py`.
2. Add a `<function_name>.cache_clear()` call in the body of the `clear_functools_caches` autouse fixture.

### Why

The `clear_functools_caches` autouse fixture runs before each test, ensuring every test starts with a clean cache. Without this registration, a test that triggers caching will leave stale values in memory that silently affect subsequent tests, causing order-dependent failures that are hard to diagnose.
