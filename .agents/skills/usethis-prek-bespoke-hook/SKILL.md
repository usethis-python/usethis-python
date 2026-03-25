---
name: usethis-prek-bespoke-hook
description: Write bespoke prek hooks as Python scripts for custom project-specific checks
compatibility: usethis, prek, git, Python
license: MIT
metadata:
  version: "1.0"
---

# Bespoke Prek Hooks

Use this skill when creating custom, project-specific prek hooks that aren't
provided by an existing third-party tool.

## Procedure

1. Create a `.py` script in the `hooks/` directory at the project root.
2. Write the hook logic in pure Python — no subprocessing.
3. Wire the hook into `.pre-commit-config.yaml` using `uv run`.
4. Assign a priority following the `usethis-prek-add-hook` skill's guidance.

## Writing the hook script

### Location and naming

Place scripts in the `hooks/` directory at the project root. Use kebab-case for
the filename with a `.py` extension (e.g., `hooks/check-skills-documented.py`).

### Script structure

Scripts should:

- Use `sys.exit(0)` for success and `sys.exit(1)` for failure.
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
