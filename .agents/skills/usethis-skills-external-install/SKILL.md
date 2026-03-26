---
name: usethis-skills-external-install
description: Reinstall already-tracked external skills from skills-lock.json (e.g. after a fresh clone)
compatibility: usethis, agent skills, npx
license: MIT
metadata:
  version: "1.0"
---

# Installing External Skills

External skills tracked in `skills-lock.json` may not be present locally (e.g. after a fresh clone, since skill files are gitignored). This skill describes how to restore them.

## Procedure

1. Set the line-ending environment variables to ensure reproducible hashes (see below).
2. Run `npx skills experimental_install` from the repository root.
3. Verify `skills-lock.json` is unchanged (e.g. `git diff --exit-code skills-lock.json`).

## Line endings and reproducible hashes

Due to a [bug in the skills CLI](https://github.com/vercel-labs/skills/issues/781), `computedHash` values in `skills-lock.json` differ depending on git's `core.autocrlf` setting. To produce reproducible hashes, **always** set the following environment variables when running any `npx skills` command:

- `GIT_CONFIG_COUNT=1`
- `GIT_CONFIG_KEY_0=core.autocrlf`
- `GIT_CONFIG_VALUE_0=false`
