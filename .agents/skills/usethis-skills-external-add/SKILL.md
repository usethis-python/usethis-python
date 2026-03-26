---
name: usethis-skills-external-add
description: Add an external (community) skill to the project from a third-party source, including installing it and documenting it in AGENTS.md
compatibility: usethis, agent skills, npx, markdown
license: MIT
metadata:
  version: "1.1"
---

# Adding External Skills

External skills are sourced from third-party repositories rather than written locally. They live in `skills-lock.json` and must be documented in the external skills registry in `AGENTS.md`.

## Procedure

1. Set the line-ending environment variables (see "Line endings and reproducible hashes" below).
2. Install the skills using `npx skills add <source> --skill '*' --agent github-copilot --yes` (e.g. `npx skills add CodSpeedHQ/codspeed --skill '*' --agent github-copilot --yes`).
3. Note the skill name(s) added to `skills-lock.json`.
4. Add each new skill to the external skills registry in `AGENTS.md`.
5. Verify the hook passes: `python hooks/check-skills-documented.py`.

## Line endings and reproducible hashes

Due to a [bug in the skills CLI](https://github.com/vercel-labs/skills/issues/781), `computedHash` values in `skills-lock.json` differ depending on git's `core.autocrlf` setting. To produce reproducible hashes, **always** set the following environment variables when running any `npx skills` command:

- `GIT_CONFIG_COUNT=1`
- `GIT_CONFIG_KEY_0=core.autocrlf`
- `GIT_CONFIG_VALUE_0=false`

## Installing the skill

To **add a new** external skill, run from the repository root (with the line-ending environment variables set as described above):

```commandline
npx skills add <github-org>/<repo> --skill '*' --agent github-copilot --yes
```

This adds the skill entry to `skills-lock.json`. Multiple skills may be added from a single source.

## Documenting in AGENTS.md

After installing, add a row to the external skills table in the "External skills" section of `AGENTS.md`:

```markdown
| `<skill-name>` | `<github-org>/<repo>` | Brief description of what the skill does |
```

Keep descriptions concise — one sentence covering what the skill does and when to use it.

## Verification

The `hooks/check-skills-documented.py` hook checks that every skill in `skills-lock.json` that does not start with `usethis-` is listed in `AGENTS.md`. Run it to confirm the documentation is complete before committing.
