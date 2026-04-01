---
name: usethis-file-create
description: Guidance on where to place new files in the repository
compatibility: usethis, git
license: MIT
metadata:
  version: "1.0"
---

# Creating New Files

## Repository root

The repository root is publicly facing and should be kept clean. Only standard community files belong there (e.g. `README.md`, `LICENSE`, `pyproject.toml`, `CONTRIBUTING.md`).

Before creating a new file at the root level, consider a more appropriate subdirectory:

- Documentation templates → `docs/`
- Hook scripts → `hooks/`
- Agent skills → `.agents/skills/`
