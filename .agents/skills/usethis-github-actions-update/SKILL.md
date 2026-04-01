---
name: usethis-github-actions-update
description: Update GitHub Actions workflows
compatibility: GitHub Actions, YAML
license: MIT
metadata:
  version: "2.0"
---

# GitHub Actions Workflows

These are in `.github/workflows/`.

## Glob patterns

Avoid redundant glob patterns. For in this example:

```yaml
on:
  push:
    paths-ignore:
      - "docs/**"
      - "**/*.md"
```

We would not want to add `xyz/**/*.md` to the `paths-ignore` list, since it is already covered by the `**/*.md` pattern.
