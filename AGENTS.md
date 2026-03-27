# Copilot Instructions

## Project Overview

**usethis** is a CLI tool that automates Python project setup and development tasks. It declaratively adds, removes, and configures popular Python tools (uv, Ruff, pytest, pre-commit, MkDocs, etc.) in existing projects without breaking configuration. The tool provides detailed ✔/☐/ℹ messages about what it automated and what users need to do next. See the README.md and docs/ for more details.

## Contributing

Follow standard contributing guidelines as documented in CONTRIBUTING.md.

## Agent Skills

The `.agents/skills` directory contains agent skills.

### Skills registry

#### usethis-specific skills

| Skill                                 | Description                                                                                                           |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `usethis-cli-modify`                  | Update GitHub Actions workflows                                                                                       |
| `usethis-file-remove`                 | Modify the usethis CLI layer (commands, options, help text) and keep documentation in sync                            |
| `usethis-github-actions-update`       | Update GitHub Actions workflows                                                                                       |
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
| `usethis-skills-external-add`         | Add an external (community) skill and document it in AGENTS.md                                                        |
| `usethis-skills-external-install`     | Install/reinstall already-tracked external skills from skills-lock.json (e.g. after a fresh clone)                    |
| `usethis-skills-modify`               | Modify agent skills (SKILL.md files)                                                                                  |
| `usethis-test-with-coverage`          | Write tests that achieve full code coverage and verify coverage locally before pushing                                |

#### External skills

External skills can be installed if they are not present — see the `usethis-skills-external-install` skill.

| Skill                    | Source                | Description                                                                           |
| ------------------------ | --------------------- | ------------------------------------------------------------------------------------- |
| `codspeed-optimize`      | `CodSpeedHQ/codspeed` | Optimize code for performance using CodSpeed benchmarks and flamegraphs               |
| `codspeed-setup-harness` | `CodSpeedHQ/codspeed` | Set up performance benchmarks and the CodSpeed harness for a project                  |
| `find-skills`            | `vercel-labs/skills`  | Discover and install agent skills from the open skills ecosystem for new capabilities |

### Important Instructions about Skills usage

- ALWAYS use possibly relevant agent skills when they are available. Eagerly use skills, if in doubt, assume a skill is relevant.
- ALWAYS use `find-skills` to research new skill capabilities if there are difficult tasks, tasks in an unfamiliar domain, if you believe there is a lack of clarity or direction around precisely how to proceed, or if you get stuck or find something surprisingly challenging. When using this skill, please be sure to use the `usethis-skills-external-install` skill when deciding to install a new external skill.
- ALWAYS consider the `usethis-qa-static-checks` to be relevant: if you think your task
  is complete, always run this skill to check for any issues before finishing.
- ALWAYS mention which skills you've used after completing any task, in PR descriptions, and comments.
