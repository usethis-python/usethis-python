---
name: usethis-python-code-modify
description: Modify Python code (e.g. refactor, add new code, or delete code)
compatibility: usethis, Python, pytest
license: MIT
metadata:
  version: "1.1"
---

# Modifying Python code

## Procedure

1. Run a subset of the tests for `src/<module>` regularly from the parallel module in the `tests/<module>` directory. Never run the entire test suite.
2. After finishing your modifications, check if documentation needs updating.
3. After finishing your modifications, run the static checks (e.g. `usethis-qa-static-checks`) to check for any issues.

## Run a subset of tests regularly

When modifying Python code, regularly run a relevant subset of the tests. The test suite is structured such that there are tests for each module in the `src` directory in the `tests` directory. For example, if we had `src/usethis/_a.py`, we would have `tests/test_a.py` with tests for that module.

### Never run the entire test suite

Running the entire test suite is unusually unnecessary and it is slow. The CI will run the entire test suite, so it is unnecessary for you to do so.

### What to do when tests fail

There are two reasons why tests might fail:

- The tests' expectations are no longer correct (e.g. because you changed the behavior of the code)
- There is a bug in the code

In the first case, update the tests to have the correct expectations, or perhaps remove the test entirely. In the second case, fix the bug in the code.

## Check if documentation needs updating

When you modify code, check whether the change affects areas that are documented in `CONTRIBUTING.md`, `README.md`, or `docs/`. If so, update the documentation to reflect the change.

### Areas needing special attention

- **Guides in CONTRIBUTING.md**: The "Guides" section in `CONTRIBUTING.md` documents step-by-step processes for common tasks like adding a new tool or adding a new badge. If your change modifies the classes, functions, or patterns described in these guides (e.g. `Tool`, `ToolSpec`, `ConfigSpec`, `use_*` functions, `typer` commands, badge functions), read the relevant guide and check whether it still accurately describes the current code. Update it if not.
- **Conventions in CONTRIBUTING.md**: The "Conventions" section documents project-wide conventions (e.g. `plain_print` instead of `print`, branding rules). If your change introduces a new convention or modifies an existing one, update this section.
- **README.md**: If your change adds, removes, or renames CLI commands or tool integrations, update `README.md` to reflect this.

## Run static checks after finishing modifications

After finishing your modifications, run the static checks (e.g. `usethis-qa-static-checks`) to check for any issues before merging.
