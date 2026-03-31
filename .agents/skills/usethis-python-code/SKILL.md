---
name: usethis-python-code
description: Guidelines for Python code design decisions such as when to share vs. duplicate code
compatibility: usethis, Python
license: MIT
metadata:
  version: "1.3"
---

# Python Code Guidelines

Use the `usethis-python-code-modify` skill when making code changes. This skill covers design decisions that inform those changes.

## Docstring code references

When referencing code names (functions, classes, modules, parameters, etc.) in docstrings, always use single backticks (`` ` ``), not double backticks (` `` `). This applies to all identifiers mentioned in docstring text.

### Example

```python
# Good: single backticks
def add_dep(name: str) -> None:
    """Add a dependency using `uv add`."""

# Bad: double backticks (RST style)
def add_dep(name: str) -> None:
    """Add a dependency using ``uv add``."""
```

### Why

The project uses Markdown-compatible formatting for docstrings. Single backticks are the Markdown standard for inline code, and the project's export hooks normalize double backticks to single backticks. Using single backticks from the start avoids this normalization and keeps docstrings consistent with their rendered output.

## Avoiding unnecessary duplication

When writing new code or replacing a dependency with custom code, prefer a single shared implementation over duplicating logic across modules. Only introduce duplication when there is a concrete, present-day reason to do so.

### Procedure

1. Before writing a new helper or utility, check whether the same logic already exists elsewhere in the codebase.
2. If the logic is used by multiple modules, place it in a shared location that both modules can import from.
3. Do not preemptively duplicate code based on speculation that implementations might diverge in the future. Wait until divergence actually occurs.

### When duplication is acceptable

Duplication is acceptable when the implementations genuinely differ in behavior or intent, even if they look superficially similar. Ask:

- Do the two pieces of code serve **different purposes** that happen to look alike today?
- Are there **concrete, present-day differences** in their behavior or constraints?
- Would coupling them together create a **fragile dependency** where a change for one caller would break the other?

If the answer to any of these is yes, duplication may be the right choice. If the answer to all is no, share the code.

### Common mistakes

- **Duplicating when replacing a dependency.** If a single dependency provided shared functionality to multiple callers, the replacement should also be shared. The dependency was already proof that a unified implementation works.
- **Speculative divergence.** Do not duplicate code because the implementations "might need to diverge someday." Refactoring to split a shared implementation later is straightforward; discovering and reconciling divergent copies is not.

## Choosing where to place a function

Before adding a new function to a module, consider at least two candidate locations. Placement should be driven by the level of abstraction the function belongs to, not by proximity to the call site.

### Procedure

1. Identify the function's level of abstraction: is it a low-level utility, a mid-level integration helper, or a high-level orchestration step?
2. Consider at least two candidate modules at different abstraction levels before committing to a location.
3. Prefer the module whose abstraction level most closely matches the function's own level, even if that module is lower in the call stack than where the function will be used.
4. Verify that placing the function in the chosen module does not violate any Import Linter contracts (run the `usethis-qa-import-linter` skill). If it would, introduce a new shared lower-level module that both the chosen module and its callers can depend on, and declare it in the relevant contract.

### Key principle

A function that extends a lower-level utility module with follow-up logic belongs in that utility module, not in the higher-level module that happens to call it. Placing logic too high in the stack couples the lower-level module's behavior to the higher-level module's concerns.

### Example

If a function processes the output of a file-reading utility and belongs conceptually to the file layer, place it in the file module — even if the only current caller is an integration module. The integration module imports from the file module, so the direction of dependency is already correct.

### Common mistakes

- **Placing a function where it is first used.** The call site is not the right guide for placement; the function's own abstraction level is.
- **Ignoring import linter contracts.** Import Linter enforces the layer hierarchy. A placement that satisfies the architecture will naturally satisfy the contracts; if it does not, that is a signal that the chosen location is wrong.
