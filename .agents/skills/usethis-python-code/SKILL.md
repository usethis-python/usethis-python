---
name: usethis-python-code
description: Guidelines for Python code design decisions such as when to share vs. duplicate code
compatibility: usethis, Python
license: MIT
metadata:
  version: "1.0"
---

# Python Code Guidelines

Use the `usethis-python-code-modify` skill when making code changes. This skill covers design decisions that inform those changes.

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
