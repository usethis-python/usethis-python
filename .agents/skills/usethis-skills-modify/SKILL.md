---
name: usethis-skills-modify
description: "Enforce version bumping, scope checking, and content quality guidelines when modifying SKILL.md files"
compatibility: usethis, agent skills, markdown
license: MIT
metadata:
  version: "1.6"
---

# Modifying Agent Skills

## Procedure

When modifying any `SKILL.md` file in `.agents/skills/`:

1. **Check scope** — verify the new content belongs in this skill (see "Before modifying: check scope" below).
2. **Generalise the instruction** — if the instruction you received is highly specific (names an exact function, file, or code object), lift it to a transferable principle before writing the skill content. See "Generalising incoming instructions" below.
3. Make the necessary content changes to the skill.
4. Increment the version number in the YAML frontmatter `metadata.version` field.
5. Verify the YAML frontmatter is valid (all required fields present, version is quoted).

## Generalising incoming instructions

You will often receive instructions that are phrased in terms of a specific situation:
"add guidance about function X", "mention that file Y must be updated", or "note that
class Z behaves this way". Before writing this into a skill, lift the instruction to a
more abstract principle.

Ask: **What general rule does this specific case illustrate?** A skill should remain
useful as the codebase evolves. If the specific function, file, or class mentioned in
the instruction were renamed or removed, would the guidance still be relevant? If not,
rewrite it so it would be.

| Specific instruction received                                                 | Generalised skill content                                                                                                                                             |
| ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Add a note that `foo_helper()` must be called before `bar()`."               | "Certain setup steps must be completed before the main operation — check the API contract for ordering requirements."                                                 |
| "Note that `config.toml` must be updated when adding a new flag."             | "When adding a feature that introduces new configuration, update all files that declare or document available options."                                               |
| "Warn that `TypeAdapter.validate_python` is banned, use `validate_or_raise`." | "Some standard-library or third-party APIs may be banned by project convention — consult the linter configuration or project documentation before reaching for them." |

Avoid adding guidance that:

- Names specific functions, classes, or files unless the principle is **only** about
  that specific thing (e.g. a skill about a single tool's CLI interface).
- Reads like a changelog or incident report ("we discovered that X did Y").
- Would become incorrect or confusing if the named entity were refactored.

## Before modifying: check scope

Before adding content to an existing skill, verify that the new content truly belongs in that skill's scope. A skill's scope is defined by its name and description — content should fit naturally within that scope.

**Do not shoe-horn content into a "somewhat" related skill.** If the content doesn't fit the skill's core purpose, either:

- Find a different existing skill that is a better fit.
- Create a new skill with a more appropriate scope (see the `usethis-skills-create` skill).

### How to judge scope

Ask these questions before adding content to a skill:

- Does this content serve the same core purpose described in the skill's name and description?
- Would someone looking for this information naturally look in this skill?
- If I removed all the existing content, would the new content still belong under this skill's name?

If the answer to any of these is "no", the content belongs elsewhere.

### Example

A skill named `usethis-python-test-full-coverage` is specifically about achieving full test coverage. Adding general test suite layout or structure guidance does not fit — that is a different concern, even though both relate to testing. Instead, create a separate skill (e.g. `usethis-python-test` for general testing guidance) or find a more appropriate existing skill.

## Incrementing the version

Every time a `SKILL.md` file is modified, its `metadata.version` must be incremented. This applies to any change, including:

- Adding, removing, or rewording instructions
- Updating procedures or steps
- Fixing typos or formatting
- Changing metadata fields other than `version`

The version follows a `MAJOR.MINOR` format (e.g. `"1.0"`, `"1.1"`, `"2.0"`).

- **Minor version bump** (e.g. `"1.1"` → `"1.2"`): Use for most changes, including adding new guidance or instructions on top of existing ones, rewording, fixing typos, expanding examples, or making minor corrections. If the fundamental approach of the skill remains the same, it's a minor bump.
- **Major version bump** (e.g. `"1.2"` → `"2.0"`): Use only when the fundamental approach or strategy of the skill is being replaced, reversed, or overhauled. A major bump means the previous version's guidance was flawed or is being abandoned in favour of a substantially different approach.

When in doubt, use a minor version bump. Adding extra guidance to a skill is not a fundamental change — it's a refinement.

### Why version incrementing matters

Incrementing the version on every change helps ensure that merge conflicts are detected when two people modify the same skill concurrently. Without versioning, two independent changes to a skill could be silently merged at the git level even though the combined result may be inconsistent or contradictory. The version bump forces a conflict, prompting a human review.

## Content quality guidelines

When modifying skill content, maintain these principles:

- **Don't make descriptions prescriptive.** If you update the `description` field in the YAML frontmatter, don't use commanding language like "ALWAYS use when..." — describe what the skill covers in neutral terms. See the `usethis-skills-create` skill for detailed description-writing guidelines.
- **Describe procedures, not state.** Skills should explain how to approach situations, not describe the current state of the codebase. State descriptions become outdated; procedures remain valid. See the `usethis-skills-create` skill for detailed guidance.
- **Keep content general.** Write instructions that remain valid as the codebase evolves. Avoid embedding specific file paths, class names, or constants unless strictly necessary. See "Generalising incoming instructions" above.
- **Never reference memories.** Skill content is read with no access to agent session history or stored memories. Do not write phrases like "as noted in a previous session" or "per the stored memory about X". Everything the reader needs must be present in the skill itself.
- **Be concise.** Only include information the agent doesn't already know. If a paragraph doesn't justify its token cost, remove it.
- **Avoid time-sensitive information.** Don't include current version numbers, file counts, or lists that grow over time.
- **Use consistent terminology.** Don't introduce synonyms for concepts that already have established terms in the skill.

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
