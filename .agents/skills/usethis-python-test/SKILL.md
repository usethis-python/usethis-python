---
name: usethis-python-test
description: General guidelines for writing tests in the usethis project, including test class organization
compatibility: usethis, Python, pytest
license: MIT
metadata:
  version: "1.5"
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


### Test file placement mirrors source file structure

Tests for a class method must live in the test file that corresponds to the source file where the class is defined — not in a test file for a utility that the method happens to call internally.

If a method is defined on `SomeClass` in `some_module.py`, its tests belong under `TestSomeClass` in `test_some_module.py`, regardless of which helper utilities the method uses at runtime.

Placing tests near the utility they exercise (rather than near the class they belong to) breaks the structural correspondence between source and test files, making tests harder to find and maintain.

### No redundant docstrings on test classes or functions

Avoid adding docstrings to test classes and test functions when the name alone is sufficient. For example, `"""Tests for validate_or_raise."""` on `TestValidateOrRaise` is redundant — the class name already communicates this.

However, a docstring is appropriate when it adds genuinely new information that the name does not convey, such as explaining the test strategy, describing a non-obvious constraint, or clarifying how the test output is validated.

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

## Asserting console output

When a test captures console output (via `capfd.readouterr()` or similar), always assert the **complete, exact output string** using equality (`assert out == "..."`), not a substring check (`assert "..." in out`).

Substring checks allow partial output to pass silently: they do not detect missing messages or unexpected extra messages. Exact equality catches both problems immediately.

### Set the backend explicitly

Console output often depends on the detected package manager backend. Always set the backend explicitly in tests that assert console output, so the result is fully deterministic:

```python
with usethis_config.set(backend=BackendEnum.uv):
    use_some_tool()

out, err = capfd.readouterr()
assert out == "✔ Some message.\n"
```

### Multi-line output

When multiple messages are printed, assert the entire combined string at once:

```python
assert out == (
    "✔ First message.\n"
    "☐ Second message.\n"
)
```

### `# noqa: RUF001` for ambiguous Unicode characters

Some console icons (e.g. `ℹ`, `×`) trigger the Ruff `RUF001` rule ("ambiguous Unicode character"). Place the `# noqa: RUF001` comment on the line that contains the character:

```python
assert out == "ℹ Some info message.\n"  # noqa: RUF001
```

### When exact equality is not appropriate

Exact equality is not appropriate for Rich table output (from `table_print` or `show_usage_table`), where the rendered string depends on terminal width and Rich's internal formatting. For table tests, substring or structural checks are acceptable.

## Clearing functools caches between tests

### Procedure

When adding `@functools.cache` to a function:

1. Import the function at the top of `tests/conftest.py`.
2. Add a `<function_name>.cache_clear()` call in the body of the `clear_functools_caches` autouse fixture.

### Why

The `clear_functools_caches` autouse fixture runs before each test, ensuring every test starts with a clean cache. Without this registration, a test that triggers caching will leave stale values in memory that silently affect subsequent tests, causing order-dependent failures that are hard to diagnose.

## Testing combinations of independent axes of variation

When a feature has two or more independent dimensions of variation, tests that vary only one dimension at a time are necessary but not sufficient. Always include at least one test that exercises non-trivial values on **multiple axes simultaneously**.

### Why varying one axis at a time is not enough

A feature that composes two independent behaviours (e.g. path traversal depth and value nesting depth) may work correctly for each behaviour in isolation while failing when both are exercised together. The interaction between dimensions is a distinct code path that single-axis tests cannot reach.

### How to apply this principle

1. **Identify the independent axes.** Before writing tests, list each dimension along which inputs or behaviour can vary (e.g. path length, value complexity, number of items, nesting level).
2. **Write single-axis tests first.** Cover the trivial and non-trivial cases for each axis independently.
3. **Add at least one cross-axis test.** Write a test that uses a non-trivial value on at least two axes simultaneously. This test verifies the interaction between dimensions.

### Example

For a function that sets a value at a key path, the two axes are:

- **Path depth** — single key vs. multiple keys (e.g. `["tool"]` vs. `["tool", "ruff"]`)
- **Value complexity** — scalar vs. nested dict (e.g. `"pep257"` vs. `{"select": ["A"], "pydocstyle": {"convention": "pep257"}}`)

Single-axis tests cover multiple keys with a scalar value, and a single key with a nested dict value. The cross-axis test uses multiple keys **and** a multiply-nested dict value together.
