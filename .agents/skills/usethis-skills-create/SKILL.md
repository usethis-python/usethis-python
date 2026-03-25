---
name: usethis-skills-create
description: Create new agent skills (SKILL.md files) following best practices for content quality, structure, and discoverability
compatibility: usethis, agent skills, markdown
license: MIT
metadata:
  version: "1.1"
---

# Creating Agent Skills

## Procedure

When creating a new skill:

1. Choose a descriptive name and create the directory `.agents/skills/<skill-name>/`.
2. Create a `SKILL.md` file with the required YAML frontmatter.
3. Write the skill content following the content guidelines below.
4. Review the skill against the quality checklist at the end.

## Naming the skill

Use kebab-case (lowercase with hyphens). The name should clearly communicate what the skill does at a glance.

Prefer specific, descriptive names over vague ones:

- **Good:** `usethis-qa-static-checks`, `usethis-prek-hook-bespoke-create`
- **Bad:** `helper`, `utils`, `tools`

### Hierarchical naming

Organize names from general to specific, using a hierarchical structure: `<project>-<domain>-<topic>-<subtopic>-<action>`. This keeps related skills grouped together and makes names predictable.

- Start with the project prefix (e.g. `usethis-`).
- Follow with the domain or category (e.g. `python-`, `qa-`, `prek-`).
- Then the topic (e.g. `code`, `hook`, `skills`).
- Optionally narrow with a subtopic (e.g. `bespoke`).
- End with a specific action if the skill is narrow in scope (e.g. `create`, `modify`).

For example, skills about bespoke prek hooks would be named:

- `usethis-prek-hook-bespoke` — general guidance on bespoke hooks (topic-level skill)
- `usethis-prek-hook-bespoke-create` — creating a new bespoke hook
- `usethis-prek-hook-bespoke-modify` — modifying an existing bespoke hook

**Bad:** `usethis-prek-bespoke-hook` — this breaks the general-to-specific order by placing the subtopic (`bespoke`) before the topic (`hook`).

When in doubt, think about how the name would sort alphabetically alongside related skills. Related skills should cluster together.

## YAML frontmatter format

All `SKILL.md` files must include the following YAML frontmatter:

```yaml
---
name: <skill-name>
description: <brief description>
compatibility: <comma-separated technologies>
license: MIT
metadata:
  version: "1.0"
---
```

### Writing the description

The `description` field is critical for skill discovery. Include both **what** the skill does and **when** to use it. Write in **third person**.

- **Good:** `"Modify agent skills (SKILL.md files)"`
- **Bad:** `"I help you modify skills"` or `"Use this to modify skills"`

## Content guidelines

### Describe procedures, not state

Skills should describe **how to approach situations**, not describe the current state of the codebase. State descriptions become outdated as code evolves, leading to incorrect guidance. Procedures remain valid because they describe approaches, not specifics.

- **Good:** "Run the test suite for the module you changed to check for regressions."
- **Bad:** "The test suite is located in `tests/` and has 247 test files covering all modules."

- **Good:** "Check the project's configuration file for the list of supported backends and add your new backend there."
- **Bad:** "The project supports hatch, uv, flit, and setuptools backends, configured in `_types/build_backend.py`."

### Keep content general

Write skills as general-purpose procedures that work regardless of how the codebase evolves. Rather than documenting specific files, classes, or constants, describe the principles for finding and working with them.

- **Good:** "Find the relevant configuration enum and add the new member."
- **Bad:** "Add the new backend to `BuildBackendEnum` in `src/usethis/_types/build_backend.py`."

When repo-specific details are necessary (e.g. exact commands to run), keep them to a minimum and separate them from the general principles.

### Be concise

Only include information the agent doesn't already know. Challenge each piece of content:

- "Does the agent really need this explanation?"
- "Can this be assumed as general knowledge?"
- "Does this paragraph justify its token cost?"

### Avoid time-sensitive information

Don't include information that will become outdated, such as current version numbers, counts of files, or lists of existing items that grow over time.

- **Good:** "Check the changelog for the latest version constraints."
- **Bad:** "The current version is 2.3.1 and supports Python 3.9+."

### Use consistent terminology

Choose one term for each concept and use it throughout:

- **Good:** Always "hook", always "contract", always "module"
- **Bad:** Mixing "hook"/"check"/"validator" for the same concept

## Structuring the content

### Use a clear hierarchy

Start with a single `#` heading describing the skill's purpose, then use `##` for major sections and `###` for subsections.

### Lead with a Procedure section

Include a numbered "Procedure" section near the top that gives an overview of the steps. Then expand on each step in subsequent sections. This provides a quick reference while allowing the agent to read details only when needed.

### Set appropriate degrees of freedom

Match the level of specificity to how fragile the task is:

- **High freedom** (text-based guidance) — when multiple valid approaches exist and context determines the best one.
- **Medium freedom** (pseudocode or parameterized steps) — when a preferred pattern exists but some variation is acceptable.
- **Low freedom** (exact commands or scripts) — when operations are fragile, error-prone, or must follow a specific sequence.

### Keep SKILL.md under 500 lines

If content grows beyond this, split details into separate reference files in the same skill directory and reference them from `SKILL.md`. Keep references one level deep — all reference files should link directly from `SKILL.md`, not from other reference files.

## Quality checklist

Before finalizing a new skill, verify:

- [ ] Name is descriptive and uses kebab-case
- [ ] Name follows general-to-specific hierarchical order
- [ ] YAML frontmatter has all required fields (`name`, `description`, `compatibility`, `license`, `metadata.version`)
- [ ] Version is a quoted string in `"MAJOR.MINOR"` format (e.g. `"1.0"`)
- [ ] Description includes what the skill does and when to use it
- [ ] Content describes procedures, not codebase state
- [ ] Content is general enough to remain valid as the codebase evolves
- [ ] No time-sensitive information (version numbers, file counts, etc.)
- [ ] Terminology is consistent throughout
- [ ] Content is concise — no unnecessary explanations
- [ ] SKILL.md body is under 500 lines
