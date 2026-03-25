# Copilot Instructions

## Project Overview

**usethis** is a CLI tool that automates Python project setup and development tasks. It declaratively adds, removes, and configures popular Python tools (uv, Ruff, pytest, pre-commit, MkDocs, etc.) in existing projects without breaking configuration. The tool provides detailed ✔/☐/ℹ messages about what it automated and what users need to do next. See the README.md and docs/ for more details.

## Contributing

Follow standard contributing guidelines as documented in CONTRIBUTING.md.

## Agent Skills

The .agent/skills directory contains agent skills.

### Important skills

- Always run static checks using the `usethis-qa-static-checks` skill before finishing a task.
- If modifying Python code, always use the `usethis-python-code`, `usethis-python-code-modify`, and `usethis-python-module-layout-modify` skills.
