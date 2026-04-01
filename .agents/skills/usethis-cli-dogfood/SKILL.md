---
name: usethis-cli-dogfood
description: Dogfood new or modified CLI commands by running them against the usethis repo itself to catch edge cases
compatibility: usethis, Python, CLI, testing
license: MIT
metadata:
  version: "1.0"
---

# Dogfooding CLI Commands

## Procedure

After implementing or modifying a CLI command:

1. Ensure all code changes are committed (clean worktree).
2. Run the command against the usethis repo itself using `uvx --from . usethis <command>`.
3. Observe the output for errors, unexpected behavior, or edge cases.
4. Revert any side-effects the command caused in the worktree.
5. If the dogfood run revealed bugs or edge cases, write failing tests that reproduce them, then fix the code.

## When this skill applies

Use this skill whenever you add a new CLI command or significantly modify the behavior of an existing one. Running the command against the project's own repository is a practical way to catch edge cases that unit tests may miss — for example, real-world configuration shapes, file layouts, or dependency structures that are hard to anticipate in isolated test fixtures.

## Detailed steps

### 1. Commit all changes first

Before dogfooding, ensure the worktree is clean by committing all pending changes. This is critical because the dogfood run will modify files in the repository (e.g. writing configuration, adding dependencies), and you need to cleanly revert those side-effects afterward.

```bash
git add . && git commit -m "WIP: pre-dogfood checkpoint"
```

### 2. Run the command

Run the command from the repository root so it operates on the project's own configuration. Use `uvx --from .` instead of `uv run` to avoid clashing with the `usethis` executable in the project virtual environment:

```bash
uvx --from . usethis <command> [options]
```

For example, if you added a new tool command:

```bash
uvx --from . usethis tool <newtool>
```

Or if you modified a show command:

```bash
uvx --from . usethis show <subcommand>
```

### 3. Analyze the output

Look for:

- **Crashes or tracebacks** — these indicate unhandled edge cases.
- **Incorrect or misleading output messages** — compare against what you expect.
- **Missing or malformed configuration** — check if the command wrote valid config.
- **Unexpected interactions** — the real project may have configuration or dependencies that your test fixtures don't cover.

### 4. Revert the side-effects

After observing the results, revert all changes the command made to the worktree. The side-effects of the dogfood run should not be committed:

```bash
git checkout -- .
```

If the command created new untracked files, also clean those:

```bash
git clean -fd
```

### 5. Write tests for discovered issues

If the dogfood run revealed bugs or unexpected behavior:

1. Write a test that reproduces the problem in a test fixture.
2. Confirm the test fails.
3. Fix the code.
4. Confirm the test passes.

This converts a real-world observation into a regression test, which is more valuable than a test written speculatively.

## Safety considerations

- **Always commit before dogfooding.** If you skip this step, the revert in step 4 will discard your uncommitted work.
- **Always revert after dogfooding.** The command's side-effects (modified config files, added dependencies, etc.) are not appropriate to commit as part of the feature PR.
- **Do not dogfood destructive remove commands** unless you are confident the revert will restore the original state. For commands that remove files or configuration, verify with `git status` before reverting.
