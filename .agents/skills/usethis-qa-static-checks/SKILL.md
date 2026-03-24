---
name: usethis-qa-static-checks
description: Perform static code checks
compatibility: usethis, Python, prek, basedpyright
license: MIT
metadata:
  version: "1.4"
---

# Static Checks

To perform static checks on the codebase, run:

```bash
uv run prek -a
uv run basedpyright
```

Note that we are interested in both errors and warnings from these tools - we should always fix both.

## When to run these checks

Before submitting changes for review, **always** run these static checks. This should be done every time, even for small changes, to avoid slowing down the code review process unnecessarily.
