---
name: usethis-skills-create
description: Create new agent skills (SKILL.md files) following best practices for content quality, structure, and discoverability
compatibility: usethis, agent skills, markdown
license: MIT
metadata:
  version: "1.7"
---

# Creating Agent Skills

## When to create a new skill vs. modify an existing one

Prefer modifying an existing skill when:

- The new content directly serves the same purpose described in the skill's name and description.
- The existing skill is the natural home for the information.
- A more general skill already exists that covers the broader topic — add to it rather than creating a narrow sub-skill.

Prefer creating a new skill when:

- You have guidance that doesn't fit the scope of any existing skill (see the `usethis-skills-modify` skill for how to judge scope).
- An existing skill is "somewhat" related but the new content serves a different core purpose.
- Adding the content to an existing skill would make its name or description misleading.

When in doubt, add to an existing general skill rather than creating a new narrow one. See "Choosing the right scope" below for how to decide.

## Procedure

When creating a new skill:

1. **Choose the right scope** — use the hierarchy brainstorming technique (see "Choosing the right scope" below) to confirm a new skill is warranted and pitched at the right level of generality.
2. Choose a descriptive name and create the directory `.agents/skills/<skill-name>/`.
3. Create a `SKILL.md` file with the required YAML frontmatter.
4. Write the skill content following the content guidelines below.
5. Add a row for the new skill to the usethis-specific skills table in `AGENTS.md` (under `### Skills registry` → `#### usethis-specific skills`).
6. Add cross-references to the new skill in related skills (see "Cross-referencing related skills" below).
7. Review the skill against the quality checklist at the end.

## Choosing the right scope

When you identify a need for new guidance that doesn't fit an existing skill, resist the temptation to jump straight to a narrowly focused skill. Instead, prefer creating a **more general** skill that the narrow topic would naturally fall under.

### The hierarchy brainstorming technique

Before creating a skill, brainstorm the ideal skill hierarchy by working from ultra-specific to fully general. For example, if you want to add guidance about where to place newly created files:

```text
usethis-file-create-placement → usethis-file-create → usethis-file → usethis
```

This hierarchy reveals **skill gaps** — intermediate levels that don't yet exist. In this example, both `usethis-file-create` and `usethis-file` are gaps. The principle is:

- **If a more general skill already exists** at any level in the hierarchy, add the guidance to it. Don't create a narrower sub-skill unless the general skill is already very large (>500 lines).
- **If no general skill exists**, create one at the most general level that makes sense — not the most specific. In the example above, creating `usethis-file-create` (or even `usethis-file`) is better than jumping straight to `usethis-file-create-placement`.

### Why general skills are preferred

- A general skill has **room to grow** — future guidance on related topics has a natural home.
- Narrow "stub skills" with limited scope often stay small and add clutter without much value.
- Agents discover skills by name and description. A general name like `usethis-file-create` is more discoverable than `usethis-file-create-placement` because agents searching for file creation guidance will find it.

### When to split into sub-skills

Only split a general skill into narrower sub-skills when the skill is getting large (>500 lines) and the content naturally separates into distinct concerns. This should be a deliberate decision, not the default — and it's usually only needed when explicitly instructed.

### Example

An agent needs to document guidance about where to place newly created files. No `usethis-file-create` or `usethis-file` skill exists.

- **Bad:** Create `usethis-file-placement` — this is too narrow, has limited room to grow, and the name suggests it only covers placement of any file operation rather than specifically file creation.
- **Good:** Create `usethis-file-create` — this is the most general level that doesn't already exist and naturally encompasses placement guidance along with other file creation concerns.
- **Also good:** Create `usethis-file` — even more general, covering file operations broadly, with a cross-reference to the existing `usethis-file-remove` skill.

## Naming the skill

Use kebab-case (lowercase with hyphens). The name should clearly communicate what the skill does at a glance.

**All skill names must start with the `usethis-` prefix.** This is enforced by the `check-skills-documented` hook.

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

Keep the description general. Ask: "What might be added to this skill in the future?" Don't focus on one specific section or aspect of the skill — instead, describe the general topic.

- **Good:** `"Maintain AGENTS.md and agent skill configuration"` — covers the broad topic
- **Bad:** `"Enforce the one-source-of-truth principle for AGENTS.md"` — focuses on a single aspect that may not represent the full scope of the skill

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

## Cross-referencing related skills

When a new skill is closely related to existing skills, add a cross-reference so agents discover the new skill at the right time. This is especially important when the new skill is a "subskill" — a more specific skill that agents should reach for from within a broader workflow.

After creating the skill, review existing skills and ask:

- **Would an agent using skill X benefit from knowing about this new skill?** If so, add a reference in skill X's procedure or content pointing to the new skill.
- **Is this new skill a specialization of a broader skill?** If a general skill covers a workflow that now has a dedicated sub-skill for one of its steps, update the general skill to mention the new one at the relevant step.

For example, if you create `usethis-cli-dogfood` (a skill for testing CLI commands against the real repo), you should update `usethis-cli-modify` to reference it — because agents modifying CLI commands should know about the dogfooding workflow.

Keep cross-references lightweight: a short mention with the skill name is enough. Don't duplicate content across skills.

## Quality checklist

Before finalizing a new skill, verify:

- [ ] Scope validated using the hierarchy brainstorming technique — no intermediate skill gap was skipped
- [ ] Skill is not too narrow — a more general skill doesn't already exist that this could be added to
- [ ] Name is descriptive and uses kebab-case
- [ ] Name follows general-to-specific hierarchical order
- [ ] YAML frontmatter has all required fields (`name`, `description`, `compatibility`, `license`, `metadata.version`)
- [ ] Version is a quoted string in `"MAJOR.MINOR"` format (e.g. `"1.0"`)
- [ ] Description includes what the skill does and when to use it
- [ ] Description is general — covers the broad topic, not just one specific aspect
- [ ] Content describes procedures, not codebase state
- [ ] Content is general enough to remain valid as the codebase evolves
- [ ] No time-sensitive information (version numbers, file counts, etc.)
- [ ] Terminology is consistent throughout
- [ ] Content is concise — no unnecessary explanations
- [ ] SKILL.md body is under 500 lines
- [ ] Cross-references added in related skills where appropriate
- [ ] Skill is added to the usethis-specific skills table in `AGENTS.md`
