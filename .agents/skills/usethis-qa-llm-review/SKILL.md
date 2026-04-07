---
name: usethis-qa-llm-review
description: Coordinate LLM-assisted quality reviews of the codebase beyond what automated tools catch
compatibility: usethis, Python, markdown, documentation
license: MIT
metadata:
  version: "1.2"
---

# LLM-Assisted Codebase Review

Coordinate manual, LLM-assisted quality checks that go beyond what automated linters and static analysis can detect. This skill acts as a dispatcher — it defines which review checks to run and how to scope them.

## When to use this skill

- When explicitly asked to perform an LLM-based review of the codebase.
- Periodically, as a proactive quality sweep.

## Scoping rules

- **Whole codebase:** Run all checks across the entire codebase only when the user explicitly requests a full review.
- **Touched files only:** When invoked during normal development work (e.g. as part of a PR workflow), limit checks to files that have been modified. Use `git diff --name-only` against the base branch to determine which files were touched.

## Procedure

1. **Determine scope** using the scoping rules above.
2. **Run each review check** listed below, passing the determined scope.
3. **Fix issues** found by each check, or report them if fixes are non-trivial.
4. **Re-run static checks** (`usethis-qa-static-checks` skill) after making any fixes.

## Review checks

The following checks should be run in order:

1. **Grammar, spelling, and tone** — use the `usethis-qa-grammar` skill.
2. **Documentation freshness** — use the `usethis-qa-doc-freshness` skill.
3. **Config files documentation sync** — use the `usethis-qa-config-files-sync` skill.
