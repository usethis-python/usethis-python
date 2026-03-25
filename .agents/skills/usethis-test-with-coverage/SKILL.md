---
name: usethis-test-with-coverage
description: Write tests that achieve full code coverage and verify coverage locally before pushing
compatibility: usethis, Python, pytest, coverage
license: MIT
metadata:
  version: "1.0"
---

# Writing Tests with Full Coverage

## Procedure

1. Identify the source modules affected by your changes.
2. Write or update tests for each affected module.
3. Run tests with coverage measurement, scoped to the affected modules.
4. Inspect the coverage report for uncovered lines and write additional tests to cover them.
5. Repeat steps 3–4 until coverage meets the target.

## Running tests with coverage

Use `pytest-cov` to measure coverage while running tests. Scope both the tests and the coverage measurement to the modules you changed.

### Measure coverage for a specific module

```bash
uv run pytest tests/path/to/test_module.py --cov=usethis.module_name --cov-report=term-missing -x -v
```

- `--cov=usethis.module_name` — measures coverage only for the specified source module. Use dotted Python import paths (e.g. `usethis._core.tool`).
- `--cov-report=term-missing` — prints a summary with the exact line numbers not covered.
- `-x` — stops on the first failure for fast feedback.

You can combine multiple `--cov` flags to cover several modules at once:

```bash
uv run pytest tests/path/to/ --cov=usethis._module_a --cov=usethis._module_b --cov-report=term-missing -x -v
```

### Generate an HTML coverage report

For a detailed, browsable view of which lines are covered:

```bash
uv run pytest tests/path/to/test_module.py --cov=usethis.module_name --cov-report=html -x -v
```

Then open `htmlcov/index.html` in a browser. This is especially useful for understanding coverage gaps in complex branching logic.

## Coverage targets

The project's Codecov configuration enforces these targets:

- **Patch coverage**: 95% — lines changed in your PR must be ≥95% covered.
- **Project coverage**: 95% — overall project coverage must remain ≥95%.

Aim for 100% coverage on new code. If you cannot cover certain lines (e.g. platform-specific branches), document why.

## Understanding coverage exclusions

The project's coverage configuration automatically excludes certain patterns from measurement. These include type-checking blocks, abstract methods, protocol classes, and exhaustiveness assertions. Check the `[tool.coverage.report]` section in `pyproject.toml` for the current list of `exclude_also` patterns.

Lines matching these patterns will not count against your coverage, so you do not need to write tests for them.

## Iterating toward full coverage

After running coverage, the `term-missing` report shows uncovered line ranges (e.g. `42-45, 78`). For each gap:

1. Read the uncovered lines to understand what conditions trigger them.
2. Write a test that exercises that specific code path.
3. Re-run with `--cov` to confirm the lines are now covered.

### Common sources of coverage gaps

- **Error handling branches** — test with invalid inputs or mocked failures.
- **Early returns or guard clauses** — test the condition that triggers the early exit.
- **Conditional logic** — ensure both branches of `if/else` are tested.
- **Loop edge cases** — test with empty collections, single items, and multiple items.

## Verifying full coverage before pushing

Before pushing, run coverage one final time for all affected modules and confirm no lines are missing:

```bash
uv run pytest tests/path/to/ --cov=usethis.module_name --cov-report=term-missing --cov-fail-under=95 -v
```

The `--cov-fail-under=95` flag causes the test run to fail if coverage drops below 95%, matching the project's Codecov threshold.
