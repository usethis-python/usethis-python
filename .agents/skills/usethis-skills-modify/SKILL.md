---
name: usethis-skills-modify
description: Modify agent skills (SKILL.md files)
compatibility: usethis, agent skills, markdown
license: MIT
metadata:
  version: "1.0"
---

# Modifying Agent Skills

## Procedure

When modifying any `SKILL.md` file in `.agents/skills/`:

1. Make the necessary content changes to the skill.
2. Increment the version number in the YAML frontmatter `metadata.version` field.
3. Verify the YAML frontmatter is valid (all required fields present, version is quoted).

## Incrementing the version

Every time a `SKILL.md` file is modified, its `metadata.version` must be incremented. This applies to any change, including:

- Adding, removing, or rewording instructions
- Updating procedures or steps
- Fixing typos or formatting
- Changing metadata fields other than `version`

The version follows a `MAJOR.MINOR` format (e.g. `"1.0"`, `"1.1"`, `"2.0"`). Increment the minor version for adding new aspects, minor fixes, etc. (e.g. `"1.1"` → `"1.2"`). Increment the major version when intending to change the behaviour of the skill in a more fundamental way.

### Why version incrementing matters

Incrementing the version on every change helps ensure that merge conflicts are detected when two people modify the same skill concurrently. Without versioning, two independent changes to a skill could be silently merged at the git level even though the combined result may be inconsistent or contradictory. The version bump forces a conflict, prompting a human review.

## YAML frontmatter format

All `SKILL.md` files must include the following YAML frontmatter fields:

```yaml
---
name: <skill-name>
description: <brief description>
compatibility: <comma-separated technologies>
license: MIT
metadata:
  version: "<MAJOR.MINOR>"
---
```
