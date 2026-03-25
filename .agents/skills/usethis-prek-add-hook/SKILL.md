---
name: usethis-prek-add-hook
description: Add a prek hook for dev
compatibility: usethis, prek, git
license: MIT
metadata:
  version: "2.0"
---

# Adding a prek Hook

## About

This project uses [prek](https://prek.j178.dev/) to manage Git hooks. Hooks are configured in `.pre-commit-config.yaml`. When adding a new hook, follow the procedures below.

## Procedure

1. Add the hook entry to `.pre-commit-config.yaml`.
2. Set the `priority` field on the hook.
3. If the tool is available as a Python package, add it as a dev dependency with `uv add --dev`.

## Adding a hook entry

There are two kinds of hooks: **remote** (from a GitHub repo) and **local** (run a local command).

### Remote hooks

For remote hooks, add a new `repo` entry under `repos` in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/owner/repo
    rev: v1.2.3
    hooks:
      - id: hook-id
        priority: 0
```

#### Use a tag for `rev`, not a commit SHA

The `rev` field **must** be a tag (e.g. `v2.1.0`), not a hard-coded commit SHA (e.g. `5630322d0f5b6675af7e16051cc3de22`). Tags are human-readable, easy to update, and clearly communicate the version being used.

If the repository does not have any tagged releases, wait until a tag is available before adding the hook, or raise this as a concern.

### Local hooks

For local hooks, add a new `repo: local` entry:

```yaml
repos:
  - repo: local
    hooks:
      - id: my-tool
        name: my-tool
        entry: uv run --frozen --offline my-tool src
        language: system
        always_run: true
        pass_filenames: false
        priority: 2
```

## Setting the `priority` field

Every hook **must** have an explicit `priority` field. prek uses `priority` to enable concurrent execution of hooks — hooks at the same priority level run in parallel, while different priority levels run sequentially (lower numbers first). See the [prek priority documentation](https://prek.j178.dev/configuration/#priority) for more details.

### Avoiding write conflicts

Hooks at the same priority level run concurrently. If two hooks both **write** to the same files (e.g. two formatters targeting Python files), they **must not** share a priority level — otherwise they will produce conflicted writes. Assign them to different priority levels so they run sequentially.

Read-only hooks (pure linters, validators, checkers) do not cause write conflicts and can safely share a priority level with other hooks, even those that write.

### Ordering: bespoke before comprehensive

When multiple hooks modify the same files at different priority levels, always run the **less advanced / more bespoke** tool **before** the **more sophisticated / more comprehensive** tool. This means:

- Niche, single-purpose formatters or fixers → **lower** priority number (run first).
- General-purpose, comprehensive formatters or linters (e.g. Ruff) → **higher** priority number (run after).

This ordering ensures that the comprehensive tool gets the final say and can clean up any style inconsistencies introduced by the bespoke tool.

### Priority level guidelines

- **`priority: 0`** — Fast, file-level checks and bespoke formatters or fixers. These are the first hooks to run.
- **`priority: 1`** — Fast, comprehensive formatters and linters (e.g. Ruff). These run after the bespoke hooks and normalize the codebase.
- **`priority: 2`** — Slower, project-wide checks (type checkers, import linters, dependency checkers). These run last.

When adding a new hook, inspect the existing `.pre-commit-config.yaml` to determine the correct priority level. If the new hook writes to files already covered by another hook at a given priority level, use a **different** priority level and follow the ordering principle above.

## Adding as a dev dependency

If the tool being added as a hook is available as a Python package, it should also be added as an explicit dev dependency:

```shell
uv add --dev <package-name>
```

This ensures the tool is available in the development environment for direct invocation (e.g. `uv run <tool>`), not only through the hook.
