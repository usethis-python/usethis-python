---
name: usethis-prek-add-hook
description: Add a prek hook for dev
compatibility: usethis, prek, pre-commit, YAML
license: MIT
metadata:
  version: "1.0"
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
        priority: 1
```

## Setting the `priority` field

Every hook **must** have an explicit `priority` field. prek uses `priority` to enable concurrent execution of hooks — hooks at the same priority level run in parallel, while different priority levels run sequentially (lower numbers first). See the [prek priority documentation](https://prek.j178.dev/configuration/#priority) for more details.

Use the following guidelines:

- **`priority: 0`** — Fast, file-level checks (linters, formatters, validators). These are the majority of hooks.
- **`priority: 1`** — Slower, project-wide checks (type checkers, import linters, dependency checkers). These run after the fast checks complete.

## Adding as a dev dependency

If the tool being added as a hook is available as a Python package, it should also be added as an explicit dev dependency:

```shell
uv add --dev <package-name>
```

This ensures the tool is available in the development environment for direct invocation (e.g. `uv run <tool>`), not only through the hook.
