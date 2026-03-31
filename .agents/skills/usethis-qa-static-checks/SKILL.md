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

## Fix all failures, including pre-existing ones

When static checks report failures, you **must** fix all of them — not just those caused by your changes. This includes pre-existing failures that were already present before your PR. Do not skip or ignore a failure because it is "unrelated" to your task.

**Why this matters:** CI enforces static checks on the entire codebase, not just changed files. If you leave pre-existing failures unfixed, CI will fail and your PR cannot be merged. Fixing these failures as you encounter them keeps the codebase healthy and avoids blocking your own work.

If a pre-existing failure requires a fix that is outside the scope of your task (e.g. a large refactor), document the issue and create a GitHub issue to track it. But in most cases, pre-existing static check failures are minor and should be fixed in your PR.
