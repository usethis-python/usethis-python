---
name: usethis-python-test-affected-find
description: Identify tests that are potentially affected by code changes, to catch regressions before CI
compatibility: usethis, Python, pytest
license: MIT
metadata:
  version: "1.0"
---

# Finding Potentially Affected Tests

## Procedure

After making code changes and before pushing, identify and run tests that could be affected:

1. Determine which source modules you changed.
2. Run the directly corresponding test modules for those source modules.
3. Apply the domain-specific rules below to identify additional tests that are indirectly affected.
4. Run all identified tests locally to catch regressions before CI.

## General principles

### Trace callers, not just callees

When you change a function or class, the most commonly missed regressions come from **callers** of that code, not the code itself. Search for usages of the changed function or class across the codebase and identify tests for those callers.

### Look for integration-style tests

Changes to internal logic often break higher-level tests that exercise end-to-end workflows. After identifying unit tests, also search for integration or interface-level tests that exercise the same functionality through the CLI or public API.

### Check tests that assert exact output

Tests that assert exact string output (e.g. CLI output snapshots, formatted messages) are especially fragile to changes in underlying logic. If your change could alter the content, ordering, or formatting of output, find tests that compare against expected output strings and run them.

## Domain-specific rules

### Rule management logic

Any change to how linter rules are selected, ignored, reconciled, or merged — including changes to rule configuration classes, rule reconciliation helpers, or rule-related methods on tool base classes — can affect the CLI output verified by integration tests.

**Always run the `test_readme_example` tests.** These tests verify that CLI commands produce the exact output shown in the README. They are sensitive to any change in rule management because the README examples include specific rule selections and ignores. Search for test methods named `test_readme_example` in the test suite and run them.

### Tool configuration changes

When modifying how a tool writes or reads its configuration (e.g. pyproject.toml sections, config file generation), run both:

- The tool's own test module.
- Any tests that verify CLI output for that tool, since configuration changes often alter the messages shown to users.

### File I/O and serialization changes

Changes to file reading, writing, or serialization logic (e.g. TOML, YAML, INI handling) can affect any tool that uses that file format. Identify which tools depend on the changed file format and run their tests.
