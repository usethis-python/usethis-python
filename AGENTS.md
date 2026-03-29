# Copilot Instructions

## Project Overview

**usethis** is a CLI tool that automates Python project setup and development tasks. It declaratively adds, removes, and configures popular Python tools (uv, Ruff, pytest, pre-commit, MkDocs, etc.) in existing projects without breaking configuration. The tool provides detailed ✔/☐/ℹ messages about what it automated and what users need to do next. See the README.md and docs/ for more details.

## Module Structure

<!-- sync:docs/module-tree.txt -->

```text
usethis                           # usethis: Automate Python project setup and development tasks that are otherwise performed manually.
├── __main__                      # The CLI application for usethis.
├── _config                       # Global configuration state for usethis.
├── _config_file                  # Context managers for coordinated configuration file I/O.
├── _console                      # Console output helpers for styled and structured printing.
├── _deps                         # Dependency management operations for project dependency groups.
├── _fallback                     # Central module for hard-coded fallback version constants.
├── _init                         # Project initialization and build system setup.
├── _subprocess                   # Subprocess invocation utilities.
├── _test                         # Test utilities and fixtures for the usethis test suite.
├── errors                        # Custom errors for the usethis package.
├── _backend                      # Backend dispatch and tool-specific backend implementations.
│   ├── dispatch                  # Backend selection and dispatch logic.
│   ├── poetry                    # Poetry backend implementation.
│   │   └── detect                # Detection of Poetry usage in a project.
│   └── uv                        # uv backend implementation.
│       ├── available             # Check whether the uv CLI is available.
│       ├── call                  # Subprocess wrappers for invoking uv commands.
│       ├── deps                  # Dependency group operations via the uv backend.
│       ├── detect                # Detection of uv usage in a project.
│       ├── errors                # Error types for the uv backend.
│       ├── init                  # Project initialization via uv.
│       ├── link_mode             # Symlink link-mode configuration for uv.
│       ├── lockfile              # Lock file creation and management for uv.
│       ├── python                # Python version queries via uv.
│       ├── toml                  # Manager for the uv.toml configuration file.
│       └── version               # Retrieve the installed uv version.
├── _core                         # Core business logic for usethis commands.
│   ├── author                    # Author metadata management for pyproject.toml.
│   ├── badge                     # README badge generation and management.
│   ├── browse                    # Open project-related URLs in a browser.
│   ├── docstyle                  # Docstring style configuration.
│   ├── list                      # List tools and their usage status.
│   ├── readme                    # README file creation and management.
│   ├── rule                      # Linter rule selection and configuration.
│   ├── show                      # Display project information.
│   ├── status                    # Development status classifier management.
│   └── tool                      # Tool functions to add/remove tools to/from the project.
├── _detect                       # The detections module.
│   ├── pre_commit                # Detection of pre-commit usage in a project.
│   └── readme                    # Detection of README file presence.
├── _file                         # Configuration file reading, writing, and merging.
│   ├── dir                       # Project directory name utilities.
│   ├── manager                   # Base file manager classes for configuration file I/O.
│   ├── merge                     # Deep merge utilities for nested mappings.
│   ├── print_                    # Pretty-printing helpers for configuration file keys.
│   ├── types_                    # Shared type aliases for file operations.
│   ├── ini                       # INI file reading and writing.
│   │   ├── errors                # Error types for INI file operations.
│   │   └── io_                   # INI file I/O manager.
│   ├── pyproject_toml            # pyproject.toml file reading and writing.
│   │   ├── errors                # Error types for pyproject.toml operations.
│   │   ├── io_                   # pyproject.toml file I/O manager.
│   │   ├── name                  # Project name and description extraction from pyproject.toml.
│   │   ├── project               # Access the [project] section of pyproject.toml.
│   │   ├── remove                # Removal of the pyproject.toml file.
│   │   ├── requires_python       # Python version requirement queries from pyproject.toml.
│   │   └── valid                 # Validation and repair of pyproject.toml structure.
│   ├── setup_cfg                 # setup.cfg file reading and writing.
│   │   ├── errors                # Error types for setup.cfg operations.
│   │   └── io_                   # setup.cfg file I/O manager.
│   ├── toml                      # TOML file reading and writing.
│   │   ├── errors                # Error types for TOML file operations.
│   │   └── io_                   # TOML file I/O manager.
│   └── yaml                      # YAML file reading and writing.
│       ├── errors                # Error types for YAML file operations.
│       ├── io_                   # YAML file I/O manager.
│       ├── typing_               # Type aliases for YAML document values.
│       └── update                # Smart update strategies for YAML sequences and mappings.
├── _integrations                 # Third-party tool integrations.
│   ├── ci                        # CI platform integrations.
│   │   └── github                # GitHub CI integration.
│   │       ├── errors            # Error types for GitHub CI operations.
│   │       └── tags              # GitHub repository tag fetching.
│   ├── environ                   # Environment detection utilities.
│   │   └── python                # Python version environment queries.
│   ├── mkdocs                    # MkDocs documentation integration.
│   │   └── core                  # MkDocs project setup and configuration.
│   ├── pre_commit                # Pre-commit hook framework integration.
│   │   ├── cmd_                  # Pre-commit command constants.
│   │   ├── core                  # Core pre-commit setup and teardown operations.
│   │   ├── errors                # Error types for pre-commit operations.
│   │   ├── hooks                 # Pre-commit hook addition and removal.
│   │   ├── init                  # Initialization of the pre-commit configuration file.
│   │   ├── language              # Pre-commit language keyword resolution.
│   │   ├── schema                # Pydantic models for the pre-commit configuration schema.
│   │   ├── version               # Pre-commit version inference.
│   │   └── yaml                  # YAML file manager for the pre-commit configuration.
│   ├── project                   # Project structure and metadata integration.
│   │   ├── build                 # Build system detection for the project.
│   │   ├── errors                # Error types for project integration operations.
│   │   ├── imports               # Import graph analysis for the project.
│   │   ├── layout                # Project source directory layout detection.
│   │   ├── name                  # Project name resolution with fallback heuristics.
│   │   └── packages              # Importable package discovery.
│   ├── pydantic                  # Pydantic model utilities.
│   │   ├── dump                  # Pydantic model serialization helpers.
│   │   └── typing_               # Type aliases for Pydantic model representations.
│   ├── pytest                    # pytest test framework integration.
│   │   └── core                  # pytest directory and configuration setup.
│   ├── readme                    # README file integration.
│   │   └── path                  # README file path resolution.
│   └── sonarqube                 # SonarQube integration.
│       ├── config                # SonarQube project configuration management.
│       └── errors                # Error types for SonarQube operations.
├── _pipeweld                     # Pipeline welding algorithm for dependency-aware ordering.
│   ├── containers                # Container data structures for pipeline compositions.
│   ├── func                      # Pipeline welding functions.
│   ├── ops                       # Operation and instruction types for pipeline welding.
│   └── result                    # Result types for pipeline welding.
├── _python                       # Python language utilities.
│   └── version                   # Utilities for Python version information.
├── _tool                         # Tool management framework.
│   ├── all_                      # Registry of all available tools.
│   ├── base                      # Base classes for tool implementations.
│   ├── config                    # Configuration specification types for tools.
│   ├── heuristics                # Heuristic fallbacks for tool configuration.
│   ├── pre_commit                # Pre-commit hook specification types for tools.
│   ├── rule                      # Lint rule specification types for tools.
│   ├── spec                      # Abstract tool specification base classes.
│   └── impl                      # Concrete tool implementations.
│       ├── base                  # Tool base implementations with side effects.
│       │   ├── codespell         # Codespell tool implementation.
│       │   ├── coverage_py       # Coverage.py tool implementation.
│       │   ├── deptry            # deptry tool implementation.
│       │   ├── import_linter     # Import Linter tool implementation.
│       │   ├── mkdocs            # MkDocs tool implementation.
│       │   ├── pre_commit        # pre-commit tool implementation.
│       │   ├── pyproject_fmt     # pyproject-fmt tool implementation.
│       │   ├── pyproject_toml    # pyproject.toml as a managed tool.
│       │   ├── pytest            # pytest tool implementation.
│       │   ├── requirements_txt  # requirements.txt tool implementation.
│       │   ├── ruff              # Ruff tool implementation.
│       │   └── ty                # ty tool implementation.
│       └── spec                  # Tool specification implementations.
│           ├── codespell         # Codespell tool specification.
│           ├── coverage_py       # Coverage.py tool specification.
│           ├── deptry            # deptry tool specification.
│           ├── import_linter     # Import Linter tool specification.
│           ├── mkdocs            # MkDocs tool specification.
│           ├── pre_commit        # pre-commit tool specification.
│           ├── pyproject_fmt     # pyproject-fmt tool specification.
│           ├── pyproject_toml    # pyproject.toml tool specification.
│           ├── pytest            # pytest tool specification.
│           ├── requirements_txt  # requirements.txt tool specification.
│           ├── ruff              # Ruff tool specification.
│           └── ty                # ty tool specification.
├── _toolset                      # Predefined groups of related tools.
│   ├── arch                      # Architecture enforcement toolset.
│   ├── doc                       # Documentation toolset.
│   ├── format_                   # Code formatting toolset.
│   ├── hook                      # Git hook framework toolset.
│   ├── lint                      # Linting toolset.
│   ├── spellcheck                # Spell checking toolset.
│   ├── test                      # Testing toolset.
│   └── typecheck                 # Type checking toolset.
├── _types                        # Shared type definitions and enumerations.
│   ├── backend                   # Backend enumeration for package manager selection.
│   ├── build_backend             # Build backend enumeration for packaging tool selection.
│   ├── deps                      # Dependency model definitions.
│   ├── docstyle                  # Docstring style enumeration.
│   └── status                    # Development status enumeration for classifiers.
└── _ui                           # User interface layer for the CLI.
    ├── app                       # The Typer application for usethis.
    ├── options                   # Shared Typer option definitions.
    └── interface                 # Typer command interface modules.
        ├── arch                  # CLI commands for architecture enforcement tools.
        ├── author                # CLI commands for managing project authors.
        ├── badge                 # CLI commands for managing README badges.
        ├── browse                # CLI commands for browsing project resources.
        ├── doc                   # CLI commands for documentation tools.
        ├── docstyle              # CLI commands for docstring style configuration.
        ├── format_               # CLI commands for code formatting tools.
        ├── hook                  # CLI commands for git hook framework tools.
        ├── init                  # CLI commands for project initialization.
        ├── lint                  # CLI commands for linting tools.
        ├── list                  # CLI commands for showing out the full usage table.
        ├── readme                # CLI commands for README management.
        ├── rule                  # CLI commands for linter rule management.
        ├── show                  # CLI commands for showing project information.
        ├── spellcheck            # CLI commands for spell checking tools.
        ├── status                # CLI commands for development status configuration.
        ├── test                  # CLI commands for testing tools.
        ├── tool                  # CLI commands for individual tool management.
        ├── typecheck             # CLI commands for type checking tools.
        └── version               # CLI commands for displaying version information.
```

<!-- /sync:docs/module-tree.txt -->

## Function Reference

ALWAYS check whether an existing function already covers your use case before implementing new logic. The functions below are important utilities that agents commonly reinvent by mistake.

<!-- sync:docs/functions.txt -->

- `get_project_deps()` (`usethis._deps`) — Get all project dependencies.
- `get_dep_groups()` (`usethis._deps`) — Get all dependency groups from the dependency-groups section of pyproject.toml.
- `get_deps_from_group()` (`usethis._deps`) — Get the list of dependencies in a named dependency group.
- `register_default_group()` (`usethis._deps`) — Register a group in the default-groups configuration if it's not already there.
- `get_default_groups()` (`usethis._deps`) — Get the list of default dependency groups installed automatically by the package manager.
- `is_dep_satisfied_in()` (`usethis._deps`) — Check if a dependency is satisfied by any dependency in the given list.
- `remove_deps_from_group()` (`usethis._deps`) — Remove dependencies from the named group if present.
- `is_dep_in_any_group()` (`usethis._deps`) — Check if a dependency exists in any dependency group.
- `add_deps_to_group()` (`usethis._deps`) — Add dependencies to a named group using PEP 735 dependency groups.
- `tick_print()` (`usethis._console`) — Print a ✔ success/completion message (green).
- `instruct_print()` (`usethis._console`) — Print a ☐ instruction the user must perform manually (red).
- `how_print()` (`usethis._console`) — Print a ☐ guidance message explaining how to do something (red).
- `info_print()` (`usethis._console`) — Print an informational message (blue).
- `err_print()` (`usethis._console`) — Print a ✗ error message to stderr (red).
- `warn_print()` (`usethis._console`) — Print a ⚠ warning message (yellow; deduplicated).
- `get_icon_mode()` (`usethis._console`) — Detect terminal's icon support level.
- `is_pre_commit_used()` (`usethis._detect.pre_commit`) — Check if pre-commit is being used in the project.
- `is_readme_used()` (`usethis._detect.readme`) — Check if the README.md file is used.
- `has_pyproject_toml_declared_build_system()` (`usethis._integrations.project.build`) — Check if a build system is declared in the project.
- `get_project_name()` (`usethis._integrations.project.name`) — The project name, from pyproject.toml if available or fallback to heuristics.
- `get_importable_packages()` (`usethis._integrations.project.packages`) — Get the names of packages in the source directory that can be imported.
- `get_source_dir_str()` (`usethis._integrations.project.layout`) — Get the source directory as a string ('src' or '.').
- `get_requires_python()` (`usethis._file.pyproject_toml.requires_python`) — Get the requires-python constraint from pyproject.toml.
- `get_required_minor_python_versions()` (`usethis._file.pyproject_toml.requires_python`) — Get Python minor versions that match the project's requires-python constraint.
- `get_name()` (`usethis._file.pyproject_toml.name`) — Get the project name from pyproject.toml.
- `get_backend()` (`usethis._backend.dispatch`) — Get the current package manager backend.

<!-- /sync:docs/functions.txt -->

## Agent Skills

The `.agents/skills` directory contains agent skills.

### Skills registry

#### usethis-specific skills

| Skill                                 | Description                                                                                                             |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `usethis-cli-modify`                  | Modify the usethis CLI layer (commands, options, help text) and keep documentation in sync                              |
| `usethis-file-remove`                 | Remove files from the project (e.g. obsolete configs or generated artifacts) in a safe, consistent way                  |
| `usethis-github-actions-update`       | Update GitHub Actions workflows                                                                                         |
| `usethis-github-issue-create`         | Create GitHub issues via the gh CLI to record lessons, track follow-up work, or file bugs discovered during development |
| `usethis-pre-commit`                  | Guidance on pre-commit hooks — this project uses prek, not pre-commit directly                                          |
| `usethis-prek-add-hook`               | Add a prek hook for dev                                                                                                 |
| `usethis-prek-hook-bespoke-create`    | Write bespoke prek hooks as Python scripts for custom project-specific checks                                           |
| `usethis-python-code`                 | Guidelines for Python code design decisions such as when to share vs. duplicate code                                    |
| `usethis-python-code-modify`          | Modify Python code (e.g. refactor, add new code, or delete code)                                                        |
| `usethis-python-enum`                 | Style and testing conventions for working with Python enums                                                             |
| `usethis-python-functions`            | Guidelines for Python function design, including return types and signature simplicity                                  |
| `usethis-python-module-layout-modify` | Modify the Python module layout (create, move, rename, or delete modules)                                               |
| `usethis-python-ruff`                 | Guidelines for complying with Ruff linter rules instead of suppressing them                                             |
| `usethis-python-test-affected-find`   | Identify tests that are potentially affected by code changes, to catch regressions before CI                            |
| `usethis-qa-import-linter`            | Use the Import Linter software on the usethis project                                                                   |
| `usethis-qa-static-checks`            | Perform static code checks                                                                                              |
| `usethis-skills-create`               | Create new agent skills (SKILL.md files) following best practices for content quality, structure, and discoverability   |
| `usethis-skills-external-add`         | Add an external (community) skill and document it in AGENTS.md                                                          |
| `usethis-skills-external-install`     | Install/reinstall already-tracked external skills from skills-lock.json (e.g. after a fresh clone)                      |
| `usethis-skills-modify`               | Modify agent skills (SKILL.md files)                                                                                    |
| `usethis-python-test-full-coverage`   | Write tests that achieve full code coverage and verify coverage locally before pushing                                  |

#### External skills

External skills can be installed if they are not present — see the `usethis-skills-external-install` skill.

| Skill                    | Source                | Description                                                                           |
| ------------------------ | --------------------- | ------------------------------------------------------------------------------------- |
| `codspeed-optimize`      | `CodSpeedHQ/codspeed` | Optimize code for performance using CodSpeed benchmarks and flamegraphs               |
| `codspeed-setup-harness` | `CodSpeedHQ/codspeed` | Set up performance benchmarks and the CodSpeed harness for a project                  |
| `find-skills`            | `vercel-labs/skills`  | Discover and install agent skills from the open skills ecosystem for new capabilities |

## Generally Important Instructions

- ALWAYS check the [Function Reference](#function-reference) section above before implementing any utility logic — mature, tested functions already exist for common operations such as reading dependencies, detecting tools, and printing console output.
- ALWAYS use possibly relevant agent skills when they are available. Eagerly use skills, if in doubt, assume a skill is relevant.
- ALWAYS use `find-skills` to research new skill capabilities if there are difficult tasks, tasks in an unfamiliar domain, if you believe there is a lack of clarity or direction around precisely how to proceed, or if you get stuck or find something surprisingly challenging. When using this skill, please be sure to use the `usethis-skills-external-install` skill when deciding to install a new external skill.
- ALWAYS consider the `usethis-python-test-full-coverage` to be relevant: if your task involves
  writing or modifying code, always use this skill to write tests and verify full coverage
  before finishing. Aim for 100% coverage on new or changed code.
- ALWAYS consider the `usethis-qa-static-checks` to be relevant: if you think your task
  is complete, always run this skill to check for any issues before finishing.
- ALWAYS mention which skills you've used after completing any task, in PR descriptions, and comments.
- ALWAYS reference the relevant issue ID in PR descriptions using a closing keyword, e.g. `Resolves #123`. This ensures traceability between PRs and the issues they address.

## Lessons

When you are working on a problem, you are almost always going to encounter a difficulty. This is great - it's an opportunity for learning. ALWAYS make a note explicitly of what lessons you are drawing as you complete a task or when receiving user feedback. Try and keep this structured: consider the root cause of the difficulty, and how you overcame it. After finishing work on a task, report back all your lessons. Finally, ALWAYS use the `usethis-github-issue-create` skill to record each lesson as a GitHub issue so it can be triaged and tracked.
