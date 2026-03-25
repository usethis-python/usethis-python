---
name: usethis-prek-add-hook
description: Add a prek hook for dev
compatibility: usethis, prek, git
license: MIT
metadata:
  version: "1.3"
---

# Adding a prek Hook

## About

This project uses [prek](https://prek.j178.dev/) to manage Git hooks. Hooks are configured in `.pre-commit-config.yaml`. When adding a new hook, follow the procedures below.

## Procedure

1. Add the hook entry to `.pre-commit-config.yaml`.
2. Set the `priority` field on the hook.
3. Place the hook entry at the correct position in the file.
4. If the tool is available as a Python package, add it as a dev dependency with `uv add --dev`.

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

If the repository does not have any tagged releases, do not use a remote hook. Instead, use a **local hook** with `uv run` (see the "Local hooks" section below). This avoids the need for a tag while still running the tool correctly. Ensure the tool is added as a dev dependency with `uv add --dev` so that `uv run` can invoke it.

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
        priority: 1
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

### Choosing a priority level

When adding a new hook, inspect the existing `.pre-commit-config.yaml` to determine the correct priority level. If the new hook writes to files already covered by another hook at a given priority level, use a **different** priority level and follow the ordering principle above. Introduce a new priority level if needed — there is no fixed limit on the number of levels.

## Placement within the file

Beyond priority levels, the **position** of a hook entry within `.pre-commit-config.yaml` matters for readability and maintainability. Follow these principles when deciding where to insert a new hook entry:

### Configuration hooks before code hooks

Place hooks that operate on **meta-programming or configuration files** (e.g. dependency syncing, pyproject.toml validation/formatting, lock file exports) **before** hooks that operate on **source code** (e.g. code formatters, linters, type checkers). This keeps the file logically structured: project setup and configuration concerns come first, then code quality concerns.

### Similar-purpose hooks close together

Place a new hook **close to existing hooks with a similar purpose or motivation**. For example, a new code formatter should be placed near other code formatters, not at the opposite end of the file from them. If two hooks need to be at different priority levels (e.g. to avoid write conflicts), they may still be placed adjacently in the file — priority ordering does not require physical separation.

Within the same priority group, **re-order hooks** if needed to maintain cosmetic proximity between the newly added hook and the most closely related existing hooks.

## Adding as a dev dependency

If the tool being added as a hook is available as a Python package, it should also be added as an explicit dev dependency:

```shell
uv add --dev <package-name>
```

This ensures the tool is available in the development environment for direct invocation (e.g. `uv run <tool>`), not only through the hook.
