---
name: usethis-skills-external-add
description: Add an external (community) skill to the project from a third-party source, including installing it and documenting it in AGENTS.md
compatibility: usethis, agent skills, npx, markdown
license: MIT
metadata:
  version: "1.0"
---

# Adding External Skills

External skills are sourced from third-party repositories rather than written locally. They live in `skills-lock.json` and must be documented in the external skills registry in `AGENTS.md`.

## Procedure

1. Install the skill using `npx skills add <source>` (e.g. `npx skills add CodSpeedHQ/codspeed`).
2. Note the skill name(s) added to `skills-lock.json`.
3. Add each new skill to the external skills registry in `AGENTS.md`.
4. Verify the hook passes: `python hooks/check-skills-documented.py`.

## Installing the skill

To **add a new** external skill, run from the repository root:

```commandline
npx skills add <github-org>/<repo>
```

This adds the skill entry to `skills-lock.json`. Multiple skills may be added from a single source.

To **reinstall** already-tracked external skills that are not present locally (e.g. after a fresh clone):

```commandline
npx skills experimental_install
```

## Documenting in AGENTS.md

After installing, add a row to the external skills table in the "External skills" section of `AGENTS.md`:

```markdown
| `<skill-name>` | `<github-org>/<repo>` | Brief description of what the skill does |
```

Keep descriptions concise — one sentence covering what the skill does and when to use it.

## Verification

The `hooks/check-skills-documented.py` hook checks that every skill in `skills-lock.json` that does not start with `usethis-` is listed in `AGENTS.md`. Run it to confirm the documentation is complete before committing.
