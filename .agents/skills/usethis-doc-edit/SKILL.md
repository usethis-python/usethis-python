---
name: usethis-doc-edit
description: Guidelines for editing documentation — including scope matching, section placement, and content organisation
compatibility: usethis, markdown, documentation
license: MIT
metadata:
  version: "1.0"
---

# Editing Documentation

General principles for editing and adding content to the project's documentation files.

## Scope matching

**Place every piece of content in the section whose scope matches the generality of the information.**

Before writing or inserting content, ask: _How broadly does this information apply?_

- If the information applies to a **single specific command or feature**, place it in the section for that command or feature.
- If the information applies to **multiple commands, features, or use cases**, place it in a more general introduction or overview section — not embedded within any one specific command or feature description.
- If the information applies to **all tooling commands or to the project as a whole**, place it at the top level of the relevant document, before the first command description.

### Common mistake to avoid

Placing broadly applicable information inside the description of one specific command because that was the section being edited at the time. Always pause to consider whether the content's scope is narrower, equal to, or wider than the section being edited.

### Example

Configuration file discovery logic that applies to all `usethis` tooling commands belongs in a general introduction at the top of the CLI reference — not nested inside the `usethis tool` section just because that was the section being worked on.

## Relation to other skills

- Use `usethis-qa-doc-freshness` to check whether existing documentation content has become factually outdated.
- Use `usethis-qa-doc-integrity` to audit whether every CLI option is present in the reference documentation.
- Use `usethis-qa-grammar` to review grammar, spelling, and tone.
