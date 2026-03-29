---
name: usethis-python-functions
description: Guidelines for Python function design, including return types and signature simplicity
compatibility: usethis, Python
license: MIT
metadata:
  version: "1.0"
---

# Function Design Guidelines

## Avoid returning tuples

Functions should not return tuples. Tuple returns obscure the meaning of each element, making call sites harder to read and fragile to refactor.

### What to do instead

1. **Simplify the design.** Often a function that returns a tuple is doing too much. Split it into separate functions that each return a single value.
2. **Introduce a dataclass.** When the values genuinely belong together, define a dataclass to give each field a name. This makes the return type self-documenting and extensible.

### Why this matters

- Tuple elements are accessed by position, not by name. Callers must remember the order, and mistakes are silent.
- Adding a new element to a tuple return breaks every existing call site.
- A dataclass communicates intent, supports attribute access, and can be extended without breaking callers.
