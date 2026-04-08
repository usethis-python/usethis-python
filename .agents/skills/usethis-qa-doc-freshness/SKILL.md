---
name: usethis-qa-doc-freshness
description: Review documentation for outdated or inaccurate content by cross-referencing the current source code and project capabilities
compatibility: usethis, Python, markdown, documentation
license: MIT
metadata:
  version: "1.0"
---

# Documentation Freshness Review

A manual, LLM-assisted review of documentation accuracy. This complements structural checks (like `usethis-qa-doc-integrity`) by catching content that has become factually outdated — for example, an FAQ describing a feature as "planned" when it has already been implemented, or a guide recommending a workaround that is no longer necessary.

## When to use this skill

- When explicitly asked to check documentation for outdated content.
- As a step in the `usethis-qa-llm-review` skill.
- After a significant feature addition or behaviour change, to verify that existing docs still reflect reality.

## Procedure

1. **Determine scope.** If invoked for specific files (e.g. files touched in a PR), review only those. If invoked for the whole documentation set, review all files listed in "What to review" below.
2. **Read each documentation file** and identify claims about the project's capabilities, limitations, or behaviour.
3. **Cross-reference each claim** against the current source code, CLI help text, and other authoritative sources within the repository to verify accuracy.
4. **Fix issues directly** when you have edit access and the correction is clear. For ambiguous cases, report the issue instead.
5. **Re-run static checks** (`usethis-qa-static-checks` skill) after making fixes, since text changes can affect generated files and formatting hooks.

## What to review

Focus on documentation that makes factual claims about the project. In rough priority order:

- **FAQ pages** — these frequently describe workarounds, limitations, and planned features that become outdated as the project evolves.
- **Getting started and tutorial pages** — instructions that reference specific commands, options, or behaviours.
- **Feature and concept pages** — pages describing backends, configuration, or tool integrations.
- **README** — high-level project description and feature claims.

## What to look for

### "Planned" or "future" claims

Statements that a feature is planned, coming soon, or not yet supported. Cross-reference the source code to check whether the feature has since been implemented.

### Workaround advice that is no longer necessary

Instructions telling users to work around a limitation that has since been removed. Check whether the described limitation still exists.

### Incorrect capability descriptions

Claims about what the project can or cannot do that no longer match the current implementation. For example, a page saying the tool only supports one backend when it now supports multiple.

### Stale cross-references

Links or references to other documentation pages, sections, or external resources that have moved, been renamed, or been removed.

### Outdated command examples

CLI examples that use options, subcommands, or syntax that has changed.

## What to ignore

- **Intentionally aspirational language** — roadmap documents or clearly labelled future plans that are not presented as current facts.
- **Third-party documentation** — claims about external tools' behaviour that are outside this project's control.
- **Version-pinned content** — content that is explicitly scoped to a specific version (e.g. "as of v1.2").

## Relation to other skills

- Use `usethis-qa-doc-integrity` for structural completeness checks (e.g. ensuring every CLI option is documented).
- Use `usethis-qa-grammar` for text quality (grammar, spelling, tone).
- Use `usethis-qa-config-files-sync` for verifying config file documentation matches the Python API.
- This skill focuses specifically on **factual accuracy** — whether what the docs say is still true.
