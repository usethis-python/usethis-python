---
name: usethis-python-code
description: Guidelines for Python code design decisions such as when to share vs. duplicate code
compatibility: usethis, Python
license: MIT
metadata:
  version: "1.7"
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

## Avoiding deep attribute nesting across layers

When code accesses deeply nested attributes of an object (e.g. `result.solution.root`), it is reaching through multiple abstraction layers. This is a sign that the logic is at the wrong level — it belongs in a lower layer, closer to the objects being accessed.

### Procedure

1. When you find yourself writing an attribute chain that crosses two or more levels of abstraction (e.g. `obj.inner.deep_attr`), stop and consider which layer owns that information.
2. Determine whether the logic operating on the deeply nested attribute can be moved into the lower layer that owns the object. This is the preferred approach — move the logic down, not just the access.
3. If moving the logic is not feasible, add a method or property to the intermediate object that exposes the needed information at the right abstraction level. The caller should only need to access one level of the object's interface.
4. Never work around deep nesting by extracting low-level details (indexes, type assertions, internal structure) into a higher layer. This couples the higher layer to implementation details it should not know about.

### Key principle

If you are accessing low-level attributes via deep nesting, the logic is in the wrong place. Always move it into a lower layer — either the layer that owns the deeply nested object, or an interface on the intermediate object.

### Example

```python
# Bad: higher layer reaches through result -> solution -> root and operates on it
result = adder.add()
flat = result.solution.root
idx = flat.index(step_name)
predecessor = flat[idx - 1] if idx > 0 else None

# Good: lower layer exposes a method that encapsulates the logic
result = adder.add()
predecessor = result.get_predecessor(step_name)
```

In the bad example, the caller knows that `solution` is a `Series`, that `Series` has a `root` list, and how to find a predecessor by index. In the good example, the `result` object owns that logic and the caller only interacts with one level of abstraction.

### Common mistakes

- **Extracting internal structure into variables.** Writing `flat = result.solution.root` does not fix the problem — it only hides the nesting in a local variable while the caller still depends on the internal structure.
- **Adding type assertions for deeply nested objects.** If you need `assert isinstance(item, str)` after accessing a nested attribute, the logic almost certainly belongs in the layer that produces the object, where the type is already known.
- **Adding a thin wrapper instead of moving logic.** A wrapper that merely returns `self.solution.root` is not enough. The goal is to move the _logic that uses_ the low-level data into the lower layer, not just to add an accessor.

## Preferring context managers for resource cleanup

When code needs to preserve and restore state around a block of operations (e.g. backing up a file before a subprocess and restoring it afterwards), always use a `@contextmanager` instead of separate setup and teardown helper functions with a `try`/`finally` block.

### Procedure

1. Identify paired operations where one sets up state and the other tears it down (e.g. backup/restore, acquire/release, redirect/revert).
2. Combine them into a single `@contextmanager` generator function that yields between the setup and teardown.
3. Use a `try`/`finally` inside the context manager to guarantee cleanup runs even if the body raises.

### Key principle

A context manager encapsulates the setup/teardown lifecycle into a single construct, making the calling code cleaner and eliminating the risk of forgetting the `finally` block or mismatching the paired calls. It also makes the intent clearer at the call site.

### Example

```python
# Bad: separate helpers require the caller to manage the lifecycle
def _backup(path: Path) -> Path:
    ...

def _restore(path: Path, backup: Path) -> None:
    ...

backup = _backup(lock_path)
try:
    run_subprocess()
finally:
    _restore(lock_path, backup)

# Good: context manager encapsulates the lifecycle
@contextmanager
def _preserved(path: Path) -> Generator[None, None, None]:
    with tempfile.TemporaryDirectory() as tmp:
        backup = shutil.copy2(path, tmp)
        try:
            yield
        finally:
            shutil.copy2(backup, path)

with _preserved(lock_path):
    run_subprocess()
```

### Common mistakes

- **Separate backup and restore helpers.** Splitting setup and teardown into two functions forces every caller to remember both calls and wire up `try`/`finally` correctly. A context manager removes this burden.
- **Forgetting `finally` in the caller.** Without a context manager, it is easy to forget the `finally` block, leaving state unrestored if an exception occurs. A context manager guarantees cleanup.

## Ordering functions: the step-down rule

Within a module, place caller functions **above** their callees. The module should read top-to-bottom like a newspaper: the most important, high-level logic appears first, and helper details appear further down.

### Procedure

1. Before adding a new private helper function to a module, locate every function that will call it.
2. Place the new helper **below** its highest caller in the file, not at the top of the file.
3. If a helper is called by multiple functions, place it below the last (lowest) caller that precedes it; it must appear after all callers that precede it.

### Key principle

A reader scanning a module should encounter each function before its helpers, never the other way around. If a helper appears above its caller, the reader is confronted with implementation details before knowing what they are for.

### Example

```python
# Bad: helper placed above its caller
def _format_version(v: str) -> str:
    return v.strip()

def get_version() -> str:
    """Return the formatted version string."""
    return _format_version(read_version_file())


# Good: caller appears first, helper appears below
def get_version() -> str:
    """Return the formatted version string."""
    return _format_version(read_version_file())

def _format_version(v: str) -> str:
    return v.strip()
```

### Common mistakes

- **Adding helpers at the top of the file.** It is tempting to place a new helper near the top, before any existing function. Always scroll down to find the caller first, then add the helper below it.
- **Placing a helper above the function that introduces it.** Even if a helper is only a few lines long, it should still follow its caller so the intent is clear before the detail.

## Caching IO-intensive private helpers

When a private helper function performs file I/O or another expensive operation and may be called more than once during a single high-level operation, decorate it with `@functools.cache` to avoid redundant work.

### When to apply

Apply `@functools.cache` to a private helper when all of the following are true:

- It performs file I/O, a subprocess call, or another expensive operation.
- It can be called more than once within a single invocation of its public caller(s).
- Its return value is deterministic with respect to the project state — the same inputs always produce the same result within a single process run.

Do **not** cache functions that write files, mutate state, or produce side effects.

### Procedure

1. Add `import functools` to the module if not already present.
2. Decorate the private helper with `@functools.cache`.
3. Register the function's cache-clear call in the `clear_functools_caches` autouse fixture in `tests/conftest.py` (see `usethis-python-test` for details).

### Common mistakes

- **Caching functions with side effects.** `@functools.cache` is only appropriate for pure, read-only operations. Functions that write files or change state should never be cached.
- **Forgetting to register cache clearing.** A cached function whose cache is never cleared between tests will cause test pollution — one test's cached value silently affects the next.
