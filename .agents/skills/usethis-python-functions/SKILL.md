---
name: usethis-python-functions
description: Guidelines for Python function design, including return types and signature simplicity
compatibility: usethis, Python
license: MIT
metadata:
  version: "1.4"
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

## Don't pass global config attributes as function parameters

Non-CLI functions must not accept attributes of the `usethis_config` global state object (such as `backend`, `offline`, `frozen`, `quiet`, etc.) as parameters. Instead, access `usethis_config` directly inside the function body. This avoids pass-through variable patterns where config values are threaded through multiple layers of function calls.

Only CLI interface functions (in `_ui/interface/`) should accept these as parameters, because they need to receive values from the CLI framework and apply them to the global config via `usethis_config.set()`.

### What to do instead

1. **Import and access `usethis_config` directly** in the function body.
2. **Use helper functions** like `get_backend()` that read from `usethis_config` internally.
3. **Use `usethis_config.set()` as a context manager** when you need to temporarily override a config value within a scope, rather than passing the override as a parameter.

### Example

```python
# Bad: accepting a config attribute as a parameter and passing it through.
def register_group(name: str, *, backend: BackendEnum) -> None:
    if backend is BackendEnum.uv:
        ...

def use_tool(*, backend: BackendEnum) -> None:
    register_group("dev", backend=backend)

# Good: access usethis_config directly.
from usethis._config import usethis_config
from usethis._backend.dispatch import get_backend

def register_group(name: str) -> None:
    if get_backend() is BackendEnum.uv:
        ...

def use_tool() -> None:
    register_group("dev")
```

## Never return bool to signal success or failure

Functions must not return `True` for success and `False` for failure. This is a C-style pattern that is un-Pythonic and error-prone. Use exception raising and handling instead.

### Why this matters

- Callers can silently ignore a `False` return, leading to bugs that go unnoticed.
- Exceptions carry context (message, traceback, type) that a bare `bool` cannot.
- Python's exception system is designed for this purpose — using it makes intent explicit and control flow clear.

### What to do instead

1. **Raise an exception** when an operation fails. Use a built-in exception type or define a custom one.
2. **Return `None`** (or nothing) on success if the function has no meaningful value to return.
3. **Let exceptions propagate** to callers, who can catch them at the appropriate level.

### Example

```python
# Bad: caller must remember to check the return value.
def add_config_entry(key: str, value: str) -> bool:
    if key in existing:
        return False
    existing[key] = value
    return True

# Good: raise on failure, return nothing on success.
def add_config_entry(key: str, value: str) -> None:
    if key in existing:
        raise ValueError(f"Config entry '{key}' already exists.")
    existing[key] = value
```

### When bool returns are fine

Returning `bool` is appropriate when the function answers a yes/no question (a predicate), such as `is_tool_used()` or `has_build_system()`. The guideline above applies only to functions where `bool` encodes an operation's outcome rather than a factual query.

## Avoid returning tuples

Functions should not return tuples. Tuple returns obscure the meaning of each element, making call sites harder to read and fragile to refactor.

### What to do instead

1. **Simplify the design.** Often a function that returns a tuple is doing too much. Split it into separate functions that each return a single value.
2. **Introduce a dataclass.** When the values genuinely belong together, define a dataclass to give each field a name. This makes the return type self-documenting and extensible.

### Why this matters

- Tuple elements are accessed by position, not by name. Callers must remember the order, and mistakes are silent.
- Adding a new element to a tuple return breaks every existing call site.
- A dataclass communicates intent, supports attribute access, and can be extended without breaking callers.

## Prefer dataclasses over NamedTuples for structured types

When grouping related fields into a structured type, always use `@dataclass` instead of `typing.NamedTuple`.

### Why this matters

`NamedTuple` inherits full tuple semantics: positional indexing, iteration, unpacking, and equality by position. These behaviours are rarely needed and invite fragile code that depends on field ordering rather than field names. A caller that unpacks or indexes a `NamedTuple` by position will silently break if a field is reordered.

A `@dataclass` provides named attribute access without any of the unintended tuple behaviours. It is self-documenting, extensible without breaking callers, and signals clearly that the type is a record, not a sequence.

### When NamedTuple is appropriate

Use `NamedTuple` only when tuple semantics are genuinely required — for example, when the object must be compared positionally, iterated over, or passed to code that expects a tuple.

### Example

```python
# Bad: tuple semantics leak through — callers can index by position
class Result(NamedTuple):
    stdout: str
    stderr: str

result[0]  # works silently; fragile if fields are reordered

# Good: only attribute access is available
@dataclass
class Result:
    stdout: str
    stderr: str

result.stdout  # explicit and refactor-safe
```

### Common mistakes

- **Choosing NamedTuple for conciseness.** The marginal brevity of a `NamedTuple` definition is not worth the unintended tuple API it exposes.
- **Using NamedTuple "just in case" unpacking is needed.** Only use it when unpacking is actually used at a call site today.
