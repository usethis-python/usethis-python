---
name: usethis-agents
description: Maintain AGENTS.md and agent skill configuration following the one-source-of-truth principle
compatibility: usethis, agent skills, markdown
license: MIT
metadata:
  version: "1.0"
---

# Agent Configuration

## The One-Source-of-Truth Principle

When providing reference material about code objects (functions, classes, modules) to agents, always prefer automation over manual documentation. Use the source code's own docstrings as the single source of truth and extract them via prek hooks — never maintain hand-written summaries that duplicate what the code already says.

### Why

Manually maintained reference material inevitably drifts out of sync with the code it describes. Docstrings live alongside the code, are reviewed during code changes, and can be mechanically extracted — ensuring the documentation always reflects reality.

### How it works in this project

- **Module tree**: `hooks/export-module-tree.py` scans Python modules, extracts the first line of each module docstring, and writes a formatted tree to `docs/module-tree.txt`. This is synced into `AGENTS.md` via `<!-- sync:docs/module-tree.txt -->` markers.
- **Skills directory**: `hooks/export-skills-directory.py` scans `usethis-*` skill directories, extracts the `name` and `description` from each `SKILL.md` frontmatter, and writes a formatted table to `docs/skills-directory.txt`.
- **Sync enforcement**: `hooks/check-doc-sync.py` verifies that content between `<!-- sync:path -->` markers in markdown files matches the referenced source file.
- **Skills documentation check**: `hooks/check-skills-documented.py` verifies that every skill directory is listed in `AGENTS.md`.

### Applying the principle

When you need to add reference material about code to agent configuration:

1. Ensure the relevant code objects have descriptive docstrings (or YAML frontmatter descriptions for skills).
2. Create or extend a prek hook to extract the information into a generated file under `docs/`.
3. Reference the generated file from `AGENTS.md` or skill files using `<!-- sync:path -->` markers.
4. Never hand-write summaries of code that could be extracted automatically.

## Maintaining AGENTS.md

`AGENTS.md` is the top-level agent configuration file. It uses sync blocks to embed auto-generated content and is validated by prek hooks.

### Sync blocks

Content between `<!-- sync:path/to/file -->` and `<!-- /sync:path/to/file -->` markers is verified by the `check-doc-sync` hook. To update synced content:

1. Modify the source (e.g. add a docstring to a module, or update a skill's description).
2. Run the relevant export hook to regenerate the docs file.
3. Copy the updated content into the sync block, or let prek handle it during commit.

### Skills registry

The usethis-specific skills table in `AGENTS.md` must include every skill directory under `.agents/skills/` that starts with `usethis-`. The `check-skills-documented` hook enforces this. When creating a new skill, add it to the table (see the `usethis-skills-create` skill for the full procedure).

## Skills Directory

<!-- sync:docs/skills-directory.txt -->

| Skill                                 | Description                                                                                                                         |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `usethis-agents`                      | Maintain AGENTS.md and agent skill configuration following the one-source-of-truth principle                                        |
| `usethis-cli-modify`                  | Modify the usethis CLI layer (commands, options, help text) and keep documentation in sync                                          |
| `usethis-file-remove`                 | Remove files from the project                                                                                                       |
| `usethis-github-actions-update`       | Update GitHub Actions workflows                                                                                                     |
| `usethis-github-issue-create`         | Create GitHub issues via the gh CLI to record lessons, track follow-up work, or file bugs discovered during development             |
| `usethis-pre-commit`                  | Guidance on pre-commit hooks — this project uses prek, not pre-commit directly                                                      |
| `usethis-prek-add-hook`               | Add a prek hook for dev                                                                                                             |
| `usethis-prek-hook-bespoke-create`    | Write bespoke prek hooks as Python scripts for custom project-specific checks                                                       |
| `usethis-python-code`                 | Guidelines for Python code design decisions such as when to share vs. duplicate code                                                |
| `usethis-python-code-modify`          | Modify Python code (e.g. refactor, add new code, or delete code)                                                                    |
| `usethis-python-enum`                 | Style and testing conventions for working with Python enums                                                                         |
| `usethis-python-functions`            | Guidelines for Python function design, including return types and signature simplicity                                              |
| `usethis-python-module-layout-modify` | Modify the Python module layout (create, move, rename, or delete modules)                                                           |
| `usethis-python-ruff`                 | Guidelines for complying with Ruff linter rules instead of suppressing them                                                         |
| `usethis-python-test-affected-find`   | Identify tests that are potentially affected by code changes, to catch regressions before CI                                        |
| `usethis-python-test-full-coverage`   | Write tests that achieve full code coverage and verify coverage locally before pushing                                              |
| `usethis-qa-import-linter`            | Use the Import Linter software on the usethis project                                                                               |
| `usethis-qa-static-checks`            | Perform static code checks                                                                                                          |
| `usethis-skills-create`               | Create new agent skills (SKILL.md files) following best practices for content quality, structure, and discoverability               |
| `usethis-skills-external-add`         | Add an external (community) skill to the project from a third-party source, including installing it and documenting it in AGENTS.md |
| `usethis-skills-external-install`     | Reinstall already-tracked external skills from skills-lock.json (e.g. after a fresh clone)                                          |
| `usethis-skills-modify`               | Modify agent skills (SKILL.md files)                                                                                                |

<!-- /sync:docs/skills-directory.txt -->
