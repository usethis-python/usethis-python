---
name: usethis-agents
description: Maintain AGENTS.md and agent skill configuration
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

### How to apply the principle

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

The skills table in `AGENTS.md` must include every skill directory under `.agents/skills/`. The `check-skills-documented` hook enforces this. When creating a new skill, add it to the table (see the `usethis-skills-create` skill for the full procedure).
