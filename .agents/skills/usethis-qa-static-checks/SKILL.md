---
name: usethis-qa-static-checks
description: Perform static code checks
compatibility: usethis, Python, prek, basedpyright
license: MIT
metadata:
  version: "1.7"
---

# Static Checks

To perform static checks on the codebase, run:

```bash
uv run prek -a
uv run basedpyright
```

Note that we are interested in both errors and warnings from these tools - we should always fix both.

## When to run these checks

Before submitting changes for review, **always** run these static checks. This applies to **every** change, no matter how small — including documentation-only changes, skill file edits, and configuration updates. Hooks like `check-doc-sync` and `export-functions` validate generated files that can go out of sync even from non-code changes. Skipping static checks is a common cause of avoidable CI failures.

## What to do when prek checks fail

**Important:** A prek run is a failure if it reports `Files were modified by following hooks`, even if every individual hook shows "Passed" or "Skipped". File modifications by hooks (e.g. auto-formatting by Ruff or prettier) count as a failure because the working tree was changed. You must re-run prek after such modifications to confirm a clean pass.

It's quite common for minor cosmetic changes to be made automatically when running the prek checks, even by linters such as Ruff and mkdownlint-cli2. Since auto-fixes may have been applied during the first run, if checks fail, you should re-run a second time to see if any issues remain. Only then should you proceed to fix any remaining issues manually.
