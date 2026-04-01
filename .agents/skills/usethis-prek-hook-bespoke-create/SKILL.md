---
name: usethis-prek-hook-bespoke-create
description: Write bespoke prek hooks as reusable Python scripts for custom checks
compatibility: usethis, prek, git, Python
license: MIT
metadata:
  version: "1.1"
---

# Bespoke Prek Hooks

Use this skill when creating custom prek hooks that aren't provided by an
existing third-party tool.

## Procedure

1. Create a `.py` script in the `hooks/` directory at the project root.
2. Write the hook logic in pure Python — no subprocessing.
3. Keep the hook generalized and reusable (see "Generalization" below).
4. Wire the hook into `.pre-commit-config.yaml` using `uv run`.
5. Assign a priority following the `usethis-prek-add-hook` skill's guidance.

## Generalization

Hooks must be written as general-purpose tools that could work in any project.
Do not hard-code project-specific names, paths, section headers, or other logic
into the hook script itself. Instead, accept all project-specific configuration
via command-line arguments.

For example:

- **Don't** hard-code a project name or package name in the script. Instead,
  accept it as a `--name` or `--prefix` argument.
- **Don't** hard-code file paths or directory names. Instead, accept
  `--source-root`, `--output-file`, or similar arguments.
- **Don't** hard-code custom section headers, categories, or groupings that are
  specific to one project's structure. Prefer flat, order-of-appearance output
  unless the user provides grouping configuration via arguments.

The `.pre-commit-config.yaml` entry is where project-specific values belong —
passed as `args` to the hook. The hook script itself should be reusable as-is in
a different project.

## Writing the hook script

### Location and naming

Place scripts in the `hooks/` directory at the project root. Use kebab-case for
the filename with a `.py` extension (e.g., `hooks/check-skills-documented.py`).

### Script structure

Scripts should:

- **Follow the step-down rule:** define `main()` first, then helper functions
  below it. Readers should encounter the high-level logic before the
  implementation details.
- Use `sys.exit(0)` for success and `sys.exit(1)` for failure.
- **Hooks that modify files must return exit code 1 when they change a file.**
  This is a pre-commit convention: exit code 1 signals that files were modified,
  so pre-commit will re-stage the changes and re-run checks. Compare the new
  content with the existing file content before writing, and only write if they
  differ. Return 1 if the file was changed, 0 if it was already up to date.
- Print error details to stderr.
- Print a success summary to stdout.
- Accept `--fix` as an optional flag when the hook can auto-correct issues. When
  `--fix` is passed, the hook should fix problems in-place and exit 0 if all
  issues were resolved.
- Use `argparse` for argument parsing when flags are needed.

### Pure Python only

Hooks must use only the Python standard library. Do not subprocess external
tools — if a check requires an external tool, it should be a separate
third-party hook instead of a bespoke one.

### Performance

Hooks run on every commit, so they must be fast:

- Read only the files you need.
- Use `pathlib.Path.glob()` or `os.scandir()` instead of walking entire trees.
- Avoid importing heavy third-party libraries.
- Prefer string operations over regular expressions when a simple check suffices.

## Wiring into `.pre-commit-config.yaml`

Register the hook as a local system hook with `uv run`:

```yaml
- repo: local
  hooks:
    - id: <hook-id>
      name: <hook-id>
      entry: uv run --frozen --offline hooks/<hook-id>.py
      language: system
      always_run: true
      pass_filenames: false
      priority: 0
```

Key points:

- `entry` uses `uv run --frozen --offline` so the hook runs without network
  access and with locked dependencies.
- `id` and `name` should match the script filename (without `.py`).
- Set `pass_filenames: false` since bespoke hooks typically determine their own
  file targets.
- Follow the `usethis-prek-add-hook` skill for priority assignment and placement
  within the file.
