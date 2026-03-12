---
name: usethis-python-code-modify
description: Modify Python code (e.g. refactor, add new code, or delete code)
compatibility: usethis, Python, pytest
license: MIT
metadata:
  version: "1.0"
---

# Modifying Python code

## Procedure

1. Run a subset of the tests for `src/<module>` regularly from the parallel module in the `tests/<module>` directory. Never run the entire test suite.
2. After finishing your modifications, run the static checks (e.g. `usethis-qa-static-checks`) to check for any issues.

## Run a subset of tests regularly

When modifying Python code, regularly run a relevant subset of the tests. The test suite is structured such that there are tests for each module in the `src` directory in the `tests` directory. For example, if we had `src/usethis/_a.py`, we would have `tests/test_a.py` with tests for that module.

### Never run the entire test suite

Running the entire test suite is unusually unnecessary and it is slow. The CI will run the entire test suite, so it is unnecessary for you to do so.

### What to do when tests fail

There are two reasons why tests might fail:

- The tests' expectations are no longer correct (e.g. because you changed the behavior of the code)
- There is a bug in the code

In the first case, update the tests to have the correct expectations, or perhaps remove the test entirely. In the second case, fix the bug in the code.

## Run static checks after finishing modifications

After finishing your modifications, run the static checks (e.g. `usethis-qa-static-checks`) to check for any issues before merging.
