---
name: usethis-python-enum
description: Style and testing conventions for working with Python enums
compatibility: usethis, Python, pytest, enums
license: MIT
metadata:
  version: "1.1"
---

# Working with Enums

## Exhaustiveness via `assert_never`

When handling all cases of an enum in `if`/`elif` chains, always include a final `else` branch that calls `assert_never` from `typing_extensions`. This ensures the type checker will flag any unhandled enum members if the enum is extended in the future.

```python
from typing_extensions import assert_never

from usethis._types.backend import BackendEnum

def handle_backend(backend: BackendEnum) -> str:
    if backend is BackendEnum.uv:
        return "uv"
    elif backend is BackendEnum.none:
        return "none"
    else:
        assert_never(backend)
```

## Nesting order: outer guards, inner enum dispatch

When a block of code dispatches on enum values **and** also has conditions that apply to a subset of those enum values, keep the enum dispatch at the **innermost** level of nesting, not the outermost.

The correct structure is:

1. Outer level: conditions that narrow the context (e.g. "is this feature active?", "does this apply to these backends?").
2. Inner level: enum dispatch that selects the specific behaviour.

A reliable signal that the nesting is inverted is when the same guard condition appears inside **multiple** arms of an enum `if`/`elif` chain. When you spot that duplication, swap the levels: hoist the shared guard outward and push the enum dispatch inward.

```python
# ❌ Inverted: guard duplicated inside each enum arm
if backend is BackendEnum.uv:
    if _some_guard():
        _do_uv_thing()
elif backend is BackendEnum.poetry:
    if _some_guard():
        _do_poetry_thing()

# ✅ Correct: shared guard outer, enum dispatch inner
if backend in (BackendEnum.uv, BackendEnum.poetry):
    if _some_guard():
        if backend is BackendEnum.uv:
            _do_uv_thing()
        elif backend is BackendEnum.poetry:
            _do_poetry_thing()
        else:
            assert_never(backend)
```

## Dicts with enum keys must have comprehensiveness tests

When a module-level dict uses an enum's members as its keys, add a unit test that asserts the dict's keys exactly match the set of all enum members. This prevents the dict from silently becoming incomplete when new members are added to the enum.

### Example test

```python
from usethis._core.status import _STATUS_TO_CLASSIFIER_MAP
from usethis._types.status import DevelopmentStatusEnum

class TestStatusToClassifierMap:
    def test_keys_match_enum(self):
        assert set(_STATUS_TO_CLASSIFIER_MAP.keys()) == set(DevelopmentStatusEnum)
```

### Why this matters

Type checkers can catch missing cases in `if`/`elif` chains when `assert_never` is used, but they **cannot** catch missing keys in a dict literal. A dedicated unit test is the only reliable way to ensure that all enum members are represented.
