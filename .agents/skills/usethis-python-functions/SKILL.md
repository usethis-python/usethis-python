---
name: usethis-python-functions
description: Guidelines for Python function design, including return types and signature simplicity
compatibility: usethis, Python
license: MIT
metadata:
  version: "1.1"
---

# Function Design Guidelines

## YAGNI: don't add function parameters you don't need yet

Function parameters should only be introduced when they have at least two distinct values that are actually used at call sites. Do not add parameters preemptively because they might be useful in the future.

This applies especially to helper and internal functions. Public API functions sometimes benefit from optional parameters to give callers flexibility, but internal helpers should be designed around their actual use cases.

### Signs that a parameter violates YAGNI

- Every call site passes the same literal value for that parameter.
- The parameter exists only to document an assumption rather than to vary behaviour.
- The parameter is optional with a default, but every caller omits it (i.e., callers always use the default and never override it).

### What to do instead

1. **Hardcode the value** inside the function body if it is always the same.
2. **Remove the parameter entirely.** If no caller needs to vary the value, the parameter adds complexity without benefit.
3. **Add the parameter later** when a genuine second caller with a different value actually exists.

### Example

```python
# Bad: always_run is always True, pass_filenames is always False —
# no call site ever changes them, so they are noise.
def make_hook(hook_id: str, entry: str, *, always_run: bool, pass_filenames: bool) -> Hook:
    ...

# Good: hardcode the values that never change.
def make_hook(hook_id: str, entry: str) -> Hook:
    always_run = True
    pass_filenames = False
    ...
```

## Avoid returning tuples

Functions should not return tuples. Tuple returns obscure the meaning of each element, making call sites harder to read and fragile to refactor.

### What to do instead

1. **Simplify the design.** Often a function that returns a tuple is doing too much. Split it into separate functions that each return a single value.
2. **Introduce a dataclass.** When the values genuinely belong together, define a dataclass to give each field a name. This makes the return type self-documenting and extensible.

### Why this matters

- Tuple elements are accessed by position, not by name. Callers must remember the order, and mistakes are silent.
- Adding a new element to a tuple return breaks every existing call site.
- A dataclass communicates intent, supports attribute access, and can be extended without breaking callers.
