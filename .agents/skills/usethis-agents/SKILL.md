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

### What belongs in AGENTS.md vs. agent skills

`AGENTS.md` is reserved for general-purpose reference material and high-level instructions about how to use agent skills. It is **not** the place for technical guidance on specific topics. If you want to add guidance about a particular practice, convention, or technique (e.g. how to create files, how to structure code, how to write tests), create or update an agent skill instead.

Appropriate content for `AGENTS.md`:

- Auto-generated reference material (module tree, function reference, skills registry) via sync blocks.
- High-level instructions about when and how to use agent skills (the "Generally Important Instructions" section).

Content that should go in an agent skill instead:

- Technical guidance or conventions about specific topics (e.g. file placement, code style, testing patterns).
- How-to instructions for specific tasks or workflows.
- Domain-specific best practices or project-specific rules.

### Sync blocks

Content between `<!-- sync:path/to/file -->` and `<!-- /sync:path/to/file -->` markers is auto-fixed by the `fix-doc-sync` hook. To update synced content:

1. Modify the source (e.g. add a docstring to a module, or update a skill's description).
2. Run the relevant export hook to regenerate the docs file.
3. Let prek handle the sync block update during commit (the `fix-doc-sync` hook runs automatically).

### Skills registry

The skills table in `AGENTS.md` must include every skill directory under `.agents/skills/`. The `check-skills-documented` hook enforces this. When creating a new skill, add it to the table (see the `usethis-skills-create` skill for the full procedure).

## Run static checks after modifying agent configuration

After finishing your modifications, run the static checks (e.g. `usethis-qa-static-checks`) to check for any issues before merging. This is especially important for agent configuration changes because several QA static checks involve markdown linting and formatting, which directly apply to `AGENTS.md` and skill files.
