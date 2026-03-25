# Copilot Instructions

## Project Overview

**usethis** is a CLI tool that automates Python project setup and development tasks. It declaratively adds, removes, and configures popular Python tools (uv, Ruff, pytest, pre-commit, MkDocs, etc.) in existing projects without breaking configuration. The tool provides detailed ✔/☐/ℹ messages about what it automated and what users need to do next. See the README.md and docs/ for more details.

## Contributing

Follow standard contributing guidelines as documented in CONTRIBUTING.md.

## Agent Skills

The `.agents/skills` directory contains agent skills.

### Important skills

- Always run static checks using the `usethis-qa-static-checks` skill before finishing a task.
- If modifying Python code, always use the `usethis-python-code`, `usethis-python-code-modify`, and `usethis-python-module-layout-modify` skills.

### Skills registry

<!-- This list is validated by the hooks/check-skills-documented.py hook. -->

| Skill                                 | Description                                                                                                           |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `github-actions-update`               | Update GitHub Actions workflows                                                                                       |
| `usethis-file-remove`                 | Remove files from the project                                                                                         |
| `usethis-pre-commit`                  | Guidance on pre-commit hooks — this project uses prek, not pre-commit directly                                        |
| `usethis-prek-add-hook`               | Add a prek hook for dev                                                                                               |
| `usethis-prek-hook-bespoke-create`    | Write bespoke prek hooks as Python scripts for custom project-specific checks                                         |
| `usethis-python-code`                 | Guidelines for Python code design decisions such as when to share vs. duplicate code                                  |
| `usethis-python-code-modify`          | Modify Python code (e.g. refactor, add new code, or delete code)                                                      |
| `usethis-python-enum`                 | Style and testing conventions for working with Python enums                                                           |
| `usethis-python-functions`            | Guidelines for Python function design, including return types and signature simplicity                                |
| `usethis-python-module-layout-modify` | Modify the Python module layout (create, move, rename, or delete modules)                                             |
| `usethis-python-ruff`                 | Guidelines for complying with Ruff linter rules instead of suppressing them                                           |
| `usethis-python-test-affected-find`   | Identify tests that are potentially affected by code changes, to catch regressions before CI                          |
| `usethis-qa-import-linter`            | Use the Import Linter software on the usethis project                                                                 |
| `usethis-qa-static-checks`            | Perform static code checks                                                                                            |
| `usethis-skills-create`               | Create new agent skills (SKILL.md files) following best practices for content quality, structure, and discoverability |
| `usethis-skills-modify`               | Modify agent skills (SKILL.md files)                                                                                  |
| `usethis-test-with-coverage`          | Write tests that achieve full code coverage and verify coverage locally before pushing                                |
