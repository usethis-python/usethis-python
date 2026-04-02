---
name: usethis-qa-grammar
description: Review code and documentation for grammar, spelling, and tone issues
compatibility: usethis, Python, markdown, documentation
license: MIT
metadata:
  version: "1.0"
---

# Grammar, Spelling, and Tone Review

A manual, LLM-assisted review of text quality across the codebase. This complements automated spellcheckers (like codespell) by catching issues they miss: awkward phrasing, inconsistent tone, grammatical errors, and unclear wording.

## When to use this skill

- When explicitly asked to review grammar, spelling, or tone across the codebase or specific files.
- As a step in the `usethis-qa-llm-review` skill.

## Procedure

1. **Determine scope.** If invoked for specific files (e.g. files touched in a PR), review only those. If invoked for the whole codebase, review all files listed in "What to review" below.
2. **Read each file** and identify grammar, spelling, tone, and clarity issues.
3. **Fix issues directly** when you have edit access and the fix is unambiguous. For subjective or large-scale changes, report them instead.
4. **Skip** anything listed under "What to ignore" below.
5. **Re-run static checks** (`usethis-qa-static-checks` skill) after making fixes, since text changes can affect generated files and formatting hooks.

## What to review

Focus on human-readable text. In rough priority order:

- **Documentation files** — README, docs/, CONTRIBUTING.md, CHANGELOG.md, and similar Markdown files.
- **Agent skill files** — SKILL.md files under `.agents/skills/`.
- **CLI help text and user-facing messages** — strings passed to `tick_print`, `instruct_print`, `info_print`, `warn_print`, `err_print`, `how_print`, and Typer command/parameter help strings.
- **Docstrings** — module, class, and function docstrings.
- **Code comments** — inline comments and block comments.
- **Error messages** — exception messages and error strings.

## What to look for

- **Spelling mistakes** — typos, misspellings, and commonly confused words that automated tools may miss (e.g. "their" vs "there", "it's" vs "its").
- **Grammar errors** — subject-verb agreement, incorrect tense, missing articles, dangling modifiers.
- **Unclear or awkward phrasing** — sentences that are hard to parse or could be simplified.
- **Inconsistent tone** — the project uses a professional but approachable tone. Flag text that is overly formal, too casual, or inconsistent with surrounding text.
- **Inconsistent terminology** — the same concept described with different words in different places (e.g. mixing "hook" and "check" for the same thing).

## What to ignore

- **Identifier names** — variable names, function names, class names, and other code identifiers. These follow naming conventions, not grammar rules.
- **Third-party content** — text in vendored files, generated files, or lock files.
- **Technical jargon used correctly** — domain-specific terms (e.g. "pyproject.toml", "pre-commit", "lockfile") are not spelling errors.
- **Intentional abbreviations** — standard abbreviations like "config", "deps", "args" are fine.
