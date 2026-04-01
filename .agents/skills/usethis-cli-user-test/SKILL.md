---
name: usethis-cli-user-test
description: Simulate user testing for CLI commands by running them in a fresh temporary project to verify the happy path
compatibility: usethis, Python, CLI, testing
license: MIT
metadata:
  version: "1.0"
---

# User Testing CLI Commands

## Procedure

After implementing or modifying a CLI command:

1. Create a fresh temporary directory and `cd` into it.
2. Initialize a minimal project with `usethis init`.
3. Run the command under test using `uvx --from <repo-path> usethis <command>`.
4. Verify the command succeeds and produces the expected output.
5. If the command revealed issues, write tests that reproduce them, then fix the code.
6. Clean up the temporary directory.

## When this skill applies

Use this skill whenever you add a new CLI command or significantly modify the behavior of an existing one. Unlike dogfooding (which runs against the usethis repo itself), user testing runs against a **fresh project** — this catches issues with initial setup, missing files, or assumptions about pre-existing configuration that a mature project would already have.

User testing and dogfooding (`usethis-cli-dogfood`) are complementary. Dogfooding catches edge cases from a complex real-world project; user testing catches problems on the happy path in a clean environment.

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

This converts a real-world observation into a regression test.

### 6. Clean up

Remove the temporary directory:

```bash
rm -rf "$TESTDIR"
```
