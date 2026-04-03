---
name: usethis-qa-static-checks
description: Perform static code checks
compatibility: usethis, Python, prek, basedpyright
license: MIT
metadata:
  version: "1.11"
---

# Static Checks

To perform static checks on the codebase, run:

```bash
stdbuf -o0 uv run prek -a  # Linux only
uv run basedpyright
```

On macOS or other non-Linux platforms, omit `stdbuf -o0`:

```bash
uv run prek -a
uv run basedpyright
```

Note that we are interested in both errors and warnings from these tools - we should always fix both.

## How to run prek correctly

**On Linux, always prefix the prek command with `stdbuf -o0`.** Prek's progress bar spinner flushes on every update, which creates bloated logs in cloud agent environments. Wrapping the command with `stdbuf -o0` suppresses this by disabling stdout buffering at the OS level, preventing the spinner's incremental writes from polluting captured output. `stdbuf` is part of GNU coreutils and is available on all standard Linux systems. On macOS, `stdbuf` is not available by default; run `uv run prek -a` directly instead.

**Never truncate prek output.** Do not pipe prek through `tail`, `head`, or any other command that discards lines (e.g. `uv run prek -a 2>&1 | tail -30`). This project has many hooks and truncating the output can hide failures, leading you to incorrectly conclude that all checks passed.

**Use the exit code as the source of truth.** The exit code of `uv run prek -a` (or `stdbuf -o0 uv run prek -a`) is the definitive indicator of success or failure — not the visible output. A zero exit code means all hooks passed; a non-zero exit code means at least one hook failed. Always check the exit code rather than scanning the output for pass/fail keywords.

## When to run these checks

Before submitting changes for review, **always** run these static checks. This applies to **every** change, no matter how small — including documentation-only changes, skill file edits, and configuration updates. Hooks like `fix-doc-sync` and `export-functions` validate generated files that can go out of sync even from non-code changes. Skipping static checks is a common cause of avoidable CI failures.

**Run static checks repeatedly until they pass.** After fixing any failure — or after making any further change for any reason — you must re-run **all** static checks again from scratch, even if you ran them moments ago. A single passing run is not enough if changes have been made since that run. It is expected and normal to invoke this skill multiple times in a loop until every check passes cleanly with no further modifications.

## What to do when prek checks fail

**Important:** A prek run is a failure if it reports `Files were modified by following hooks`, even if every individual hook shows "Passed" or "Skipped". File modifications by hooks (e.g. auto-formatting by Ruff or prettier) count as a failure because the working tree was changed. You must re-run prek after such modifications to confirm a clean pass.

It's quite common for minor cosmetic changes to be made automatically when running the prek checks, even by linters such as Ruff and markdownlint-cli2. Since auto-fixes may have been applied during the first run, if checks fail, you should re-run a second time to see if any issues remain. Only then should you proceed to fix any remaining issues manually.

## Fix all failures, including pre-existing ones

When static checks report failures, you **must** fix all of them — not just those caused by your changes. This includes pre-existing failures that were already present before your PR. Do not skip or ignore a failure because it is "unrelated" to your task.

**Why this matters:** CI enforces static checks on the entire codebase, not just changed files. If you leave pre-existing failures unfixed, CI will fail and your PR cannot be merged. Fixing these failures as you encounter them keeps the codebase healthy and avoids blocking your own work.

If a pre-existing failure requires a fix that is outside the scope of your task (e.g. a large refactor), document the issue and create a GitHub issue to track it. But in most cases, pre-existing static check failures are minor and should be fixed in your PR.
