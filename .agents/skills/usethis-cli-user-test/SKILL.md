---
name: usethis-cli-user-test
description: Simulate user testing for CLI commands by running them in a fresh temporary project to verify the happy path
compatibility: usethis, Python, CLI, testing
license: MIT
metadata:
  version: "1.1"
---

# User Testing CLI Commands

## Procedure

After implementing or modifying a CLI command:

1. Create a fresh temporary directory and `cd` into it.
2. Initialize a minimal project with `usethis init`.
3. Run the command under test using `uvx --from <repo-path> usethis <command>`.
4. Verify the command succeeds and produces the expected output.
5. If the command revealed issues, write tests that reproduce them, then fix the code.
6. **Re-run the exact same steps from scratch** (new temp dir, `usethis init`, same command) to confirm the fix works on the real happy path.
7. Clean up the temporary directory.

## When this skill applies

Use this skill whenever you add a new CLI command or significantly modify the behavior of an existing one. Unlike dogfooding (which runs against the usethis repo itself), user testing runs against a **fresh project** — this catches issues with initial setup, missing files, or assumptions about pre-existing configuration that a mature project would already have.

User testing and dogfooding (`usethis-cli-dogfood`) are complementary. Dogfooding catches edge cases from a complex real-world project; user testing catches problems on the happy path in a clean environment.

## Critical rule: never deviate from the happy path

The entire purpose of user testing is to prove that a real user, starting from scratch, can successfully use the command. This means:

- **Always follow the exact steps above.** Do not skip `usethis init`, do not manually create or edit files to set up "convenient" preconditions, and do not substitute an alternative scenario that avoids the failure.
- **If the happy path fails, fix the code — not the test.** When a command fails after `usethis init` in a fresh project, the bug is in the code, not in the test scenario. Write a unit or integration test that reproduces the failure, fix the underlying issue, then re-run the full happy path from scratch to confirm the fix.
- **Never manually construct hypothetical scenarios to pass user testing.** For example, do not pre-populate configuration files, create dependencies by hand, or set up project state that `usethis init` would not produce. If the command only works under manually-arranged conditions, it does not work for real users.
- **Re-run from a clean slate after every fix.** Create a new temporary directory and repeat the full procedure. Do not reuse a directory where you have already run commands or made manual edits — leftover state can mask problems.

If user testing reveals that the happy path is broken, this is the most valuable finding of the test. Changing the test to avoid the failure defeats the purpose entirely.

## Detailed steps

### 1. Create a temporary directory

Create a temporary directory to simulate a fresh user environment. Use a system temp directory so it is automatically isolated from the repository worktree:

```bash
TESTDIR=$(mktemp -d)
cd "$TESTDIR"
git init
```

### 2. Initialize a project

Most commands expect a project to already exist. Start by initializing one:

```bash
uvx --from <repo-path> usethis init
```

Replace `<repo-path>` with the absolute path to your local checkout of the usethis repository (e.g. `~/repositories/usethis-python`).

### 3. Run the command under test

Run the CLI command you are testing:

```bash
uvx --from <repo-path> usethis <command> [options]
```

For example:

```bash
uvx --from <repo-path> usethis tool ruff
```

#### Non-uv backends

If the command supports a non-uv, non-none backend (e.g. Poetry), include it in the isolated environment so it is available:

```bash
uvx --from <repo-path> --with poetry usethis <command> --backend=poetry
```

### 4. Verify the result

Check that:

- **The command exits successfully** — no tracebacks or non-zero exit codes.
- **Output messages are correct** — ✔/☐/ℹ messages match expectations.
- **Configuration files are valid** — inspect generated or modified files.
- **Follow-up commands work** — if the command sets up a tool, try running that tool.

### 5. Write tests for discovered issues

If user testing revealed bugs or unexpected behavior:

1. Write a test that reproduces the problem in a test fixture.
2. Confirm the test fails.
3. Fix the code.
4. Confirm the test passes.
5. **Re-run the full user testing procedure from step 1** (new temp dir, fresh `usethis init`, same command) to confirm the happy path now succeeds end-to-end.

This converts a real-world observation into a regression test. Do not consider user testing complete until the happy path passes without manual intervention.

### 6. Clean up

Remove the temporary directory:

```bash
rm -rf "$TESTDIR"
```
