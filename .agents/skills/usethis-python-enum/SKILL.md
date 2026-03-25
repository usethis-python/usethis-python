---
name: usethis-python-enum
description: Style and testing conventions for working with Python enums
compatibility: usethis, Python, pytest, enums
license: MIT
metadata:
  version: "1.0"
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
