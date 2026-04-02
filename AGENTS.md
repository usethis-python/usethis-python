# Copilot Instructions

## Project Overview

**usethis** is a CLI tool that automates Python project setup and development tasks. It declaratively adds, removes, and configures popular Python tools (uv, Ruff, pytest, pre-commit, MkDocs, etc.) in existing projects without breaking configuration. The tool provides detailed ✔/☐/ℹ messages about what it automated and what users need to do next. See the README.md and docs/ for more details.

## Module Structure

<!-- sync:docs/module-tree.txt -->

```text
usethis                           # usethis: Automatically manage Python tooling and configuration: linters, formatters, and more.
├── __main__                      # The CLI application for usethis.
├── _config                       # Global configuration state for usethis.
├── _config_file                  # Context managers for coordinated configuration file I/O.
├── _console                      # Console output helpers for styled and structured printing.
├── _deps                         # Dependency management operations for project dependency groups.
├── _fallback                     # Central module for hard-coded fallback version constants.
├── _init                         # Project initialization and build system setup.
├── _subprocess                   # Subprocess invocation utilities.
├── _test                         # Test utilities and fixtures for the usethis test suite.
├── _validate                     # Safer abstractions for Pydantic TypeAdapter validation.
├── errors                        # Custom errors for the usethis package.
├── _backend                      # Backend dispatch and tool-specific backend implementations.
│   ├── dispatch                  # Backend selection and dispatch logic.
│   ├── poetry                    # Poetry backend implementation.
│   │   ├── available             # Check whether the Poetry CLI is available.
│   │   ├── call                  # Subprocess wrappers for invoking Poetry commands.
│   │   ├── deps                  # Dependency group operations via the Poetry backend.
│   │   ├── detect                # Detection of Poetry usage in a project.
│   │   ├── errors                # Error types for the Poetry backend.
│   │   └── init                  # Project initialization via Poetry.
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
│   │   ├── deps                  # Dependency extraction from pyproject.toml.
│   │   ├── errors                # Error types for pyproject.toml operations.
│   │   ├── io_                   # pyproject.toml file I/O manager.
│   │   ├── name                  # Project name and description extraction from pyproject.toml.
│   │   ├── project               # Access the [project] section of pyproject.toml.
│   │   ├── remove                # Removal of the pyproject.toml file.
│   │   ├── requires_python       # Python version requirement queries from pyproject.toml.
│   │   ├── valid                 # Validation and repair of pyproject.toml structure.
│   │   └── write                 # Preparation helpers for writing pyproject.toml via subprocesses.
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
│   │   ├── license               # License detection for the project.
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
│       │   ├── tach              # Tach tool implementation.
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
│           ├── tach              # Tach tool specification.
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

- `get_backend()` (`usethis._backend.dispatch`) — Get the current package manager backend.
- `call_backend_subprocess()` (`usethis._backend.dispatch`) — Dispatch a subprocess call to the appropriate backend.
- `is_poetry_available()` (`usethis._backend.poetry.available`) — Check if the `poetry` command is available in the current environment.
- `call_poetry_subprocess()` (`usethis._backend.poetry.call`) — Run a subprocess using the Poetry command-line tool.
- `add_dep_to_group_via_poetry()` (`usethis._backend.poetry.deps`) — Add a dependency to the named group using Poetry.
- `remove_dep_from_group_via_poetry()` (`usethis._backend.poetry.deps`) — Remove a dependency from the named group using Poetry.
- `is_poetry_used()` (`usethis._backend.poetry.detect`) — Check if Poetry is being used in the project.
- `ensure_pyproject_toml_via_poetry()` (`usethis._backend.poetry.init`) — Create a pyproject.toml file using `poetry init`.
- `opinionated_poetry_init()` (`usethis._backend.poetry.init`) — Subprocess `poetry init` with opinionated arguments.
- `is_uv_available()` (`usethis._backend.uv.available`) — Check if the `uv` command is available in the current environment.
- `call_uv_subprocess()` (`usethis._backend.uv.call`) — Run a subprocess using the uv command-line tool.
- `add_default_groups_via_uv()` (`usethis._backend.uv.call`) — Add default groups using the uv command-line tool.
- `add_dep_to_group_via_uv()` (`usethis._backend.uv.deps`) — Add a dependency to the named group using uv.
- `remove_dep_from_group_via_uv()` (`usethis._backend.uv.deps`) — Remove a dependency from the named group using uv.
- `get_default_groups_via_uv()` (`usethis._backend.uv.deps`) — Get the default dependency groups from the uv configuration.
- `is_uv_used()` (`usethis._backend.uv.detect`) — Check if uv is being used in the project.
- `opinionated_uv_init()` (`usethis._backend.uv.init`) — Subprocess `uv init` with opinionated arguments.
- `ensure_pyproject_toml_via_uv()` (`usethis._backend.uv.init`) — Create a pyproject.toml file using `uv init --bare`.
- `ensure_symlink_mode()` (`usethis._backend.uv.link_mode`) — Ensure that the symlink link mode is enabled.
- `ensure_uv_lock()` (`usethis._backend.uv.lockfile`) — Ensure a uv.lock file exists, creating it if necessary.
- `get_available_uv_python_versions()` (`usethis._backend.uv.python`) — Get the set of Python versions available via uv.
- `get_supported_uv_minor_python_versions()` (`usethis._backend.uv.python`) — Get the minor Python versions supported by the project and available via uv.
- `uv_python_pin()` (`usethis._backend.uv.python`) — Pin the Python version for the project using uv.
- `get_uv_version()` (`usethis._backend.uv.version`) — Get the version string of the installed uv tool.
- `next_breaking_uv_version()` (`usethis._backend.uv.version`) — Get the next breaking version for a uv version string, following semver.
- `files_manager()` (`usethis._config_file`) — Context manager that opens all configuration file managers for coordinated I/O.
- `plain_print()` (`usethis._console`) — Print a plain message to the console, respecting quiet and alert-only settings.
- `table_print()` (`usethis._console`) — Print a Rich table to the console, respecting quiet and alert-only settings.
- `tick_print()` (`usethis._console`) — Print a ✔ success/completion message (green).
- `instruct_print()` (`usethis._console`) — Print a ☐ instruction the user must perform manually (red).
- `how_print()` (`usethis._console`) — Print a ☐ guidance message explaining how to do something (red).
- `info_print()` (`usethis._console`) — Print an informational message (blue).
- `err_print()` (`usethis._console`) — Print a ✗ error message to stderr (red).
- `warn_print()` (`usethis._console`) — Print a ⚠ warning message (yellow; deduplicated).
- `get_icon_mode()` (`usethis._console`) — Detect terminal's icon support level.
- `add_author()` (`usethis._core.author`) — Add an author entry to the project metadata in pyproject.toml.
- `get_pre_commit_badge()` (`usethis._core.badge`) — Return the pre-commit badge.
- `get_pypi_badge()` (`usethis._core.badge`) — Return the PyPI version badge for the project.
- `get_ruff_badge()` (`usethis._core.badge`) — Return the Ruff badge.
- `get_socket_badge()` (`usethis._core.badge`) — Return the Socket supply chain security badge for the project.
- `get_ty_badge()` (`usethis._core.badge`) — Return the ty type checker badge.
- `get_uv_badge()` (`usethis._core.badge`) — Return the uv package manager badge.
- `get_bitbucket_badge()` (`usethis._core.badge`) — Return the Bitbucket badge.
- `get_usethis_badge()` (`usethis._core.badge`) — Return the usethis badge.
- `get_badge_order()` (`usethis._core.badge`) — Return the canonical ordered list of all supported badges.
- `add_badge()` (`usethis._core.badge`) — Add a badge to the README.md file in the correct position.
- `is_blank()` (`usethis._core.badge`) — Return True if the line is empty or contains only whitespace.
- `is_header()` (`usethis._core.badge`) — Return True if the line is a Markdown header.
- `is_badge()` (`usethis._core.badge`) — Return True if the line looks like a Markdown badge.
- `remove_badge()` (`usethis._core.badge`) — Remove a badge from the README.md file.
- `browse_pypi()` (`usethis._core.browse`) — Open or display the PyPI project page URL for a package.
- `use_docstyle()` (`usethis._core.docstyle`) — Configure the docstring style convention for the project using Ruff.
- `show_usage_table()` (`usethis._core.list`) — Show the usage table.
- `get_usage_table()` (`usethis._core.list`) — Get the usage table.
- `add_readme()` (`usethis._core.readme`) — Add a README.md file to the project.
- `select_rules()` (`usethis._core.rule`) — Select the given linter rules, enabling the appropriate tools as needed.
- `deselect_rules()` (`usethis._core.rule`) — Deselect the given linter rules from the relevant tools.
- `ignore_rules()` (`usethis._core.rule`) — Add the given linter rules to the ignore list of the relevant tools.
- `unignore_rules()` (`usethis._core.rule`) — Remove the given linter rules from the ignore list of the relevant tools.
- `get_rules_mapping()` (`usethis._core.rule`) — Partition a list of rule codes into deptry and Ruff rule groups.
- `show_backend()` (`usethis._core.show`) — Display the inferred package manager backend for the current project.
- `show_license()` (`usethis._core.show`) — Display the detected license of the current project in SPDX format.
- `show_name()` (`usethis._core.show`) — Display the name of the current project.
- `show_sonarqube_config()` (`usethis._core.show`) — Display the sonar-project.properties configuration for the current project.
- `use_development_status()` (`usethis._core.status`) — Set the development status classifier in pyproject.toml.
- `use_codespell()` (`usethis._core.tool`) — Add and configure the codespell spellchecker tool.
- `use_coverage_py()` (`usethis._core.tool`) — Add and configure the Coverage.py code coverage tool.
- `use_deptry()` (`usethis._core.tool`) — Add and configure the deptry dependency linter tool.
- `use_import_linter()` (`usethis._core.tool`) — Add and configure the Import Linter architecture enforcement tool.
- `use_mkdocs()` (`usethis._core.tool`) — Add and configure the MkDocs documentation site generator tool.
- `use_pre_commit()` (`usethis._core.tool`) — Add and configure the pre-commit hook framework.
- `use_pyproject_fmt()` (`usethis._core.tool`) — Add and configure the pyproject-fmt pyproject.toml formatter tool.
- `use_pyproject_toml()` (`usethis._core.tool`) — Add and configure the pyproject.toml file as a project configuration tool.
- `use_pytest()` (`usethis._core.tool`) — Add and configure the pytest testing framework.
- `use_requirements_txt()` (`usethis._core.tool`) — Add and configure a requirements.txt file exported from the uv lockfile.
- `use_ruff()` (`usethis._core.tool`) — Add Ruff to the project.
- `use_tach()` (`usethis._core.tool`) — Add and configure the Tach architecture enforcement tool.
- `use_ty()` (`usethis._core.tool`) — Add and configure the ty type checker tool.
- `use_tool()` (`usethis._core.tool`) — General dispatch function to add or remove a tool to/from the project.
- `get_project_deps()` (`usethis._deps`) — Get all project dependencies.
- `get_dep_groups()` (`usethis._deps`) — Get all dependency groups from pyproject.toml.
- `get_deps_from_group()` (`usethis._deps`) — Get the list of dependencies in a named dependency group.
- `register_default_group()` (`usethis._deps`) — Register a group in the default-groups configuration if it's not already there.
- `add_default_groups()` (`usethis._deps`) — Register the given dependency groups as default groups in the package manager configuration.
- `get_default_groups()` (`usethis._deps`) — Get the list of default dependency groups installed automatically by the package manager.
- `ensure_dev_group_is_defined()` (`usethis._deps`) — Ensure the 'dev' dependency group exists in pyproject.toml.
- `is_dep_satisfied_in()` (`usethis._deps`) — Check if a dependency is satisfied by any dependency in the given list.
- `remove_deps_from_group()` (`usethis._deps`) — Remove dependencies from the named group if present.
- `is_dep_in_any_group()` (`usethis._deps`) — Check if a dependency exists in any dependency group.
- `add_deps_to_group()` (`usethis._deps`) — Add dependencies to a named group using PEP 735 dependency groups.
- `is_pre_commit_used()` (`usethis._detect.pre_commit`) — Check if pre-commit is being used in the project.
- `is_readme_used()` (`usethis._detect.readme`) — Check if the README.md file is used.
- `next_breaking_version()` (`usethis._fallback`) — Get the next breaking version for a version string, following semver.
- `get_project_name_from_dir()` (`usethis._file.dir`) — Derive a valid project name from the current directory name.
- `deep_merge()` (`usethis._file.merge`) — Recursively merge source into target in place, returning target.
- `print_keys()` (`usethis._file.print_`) — Convert a list of keys to a string.
- `get_project_deps()` (`usethis._file.pyproject_toml.deps`) — Get all project dependencies from [project.dependencies].
- `get_dep_groups()` (`usethis._file.pyproject_toml.deps`) — Get all dependency groups from [dependency-groups].
- `get_poetry_project_deps()` (`usethis._file.pyproject_toml.deps`) — Get project dependencies from [tool.poetry.dependencies].
- `get_poetry_dep_groups()` (`usethis._file.pyproject_toml.deps`) — Get dependency groups from [tool.poetry.group.*.dependencies].
- `get_name()` (`usethis._file.pyproject_toml.name`) — Get the project name from pyproject.toml.
- `get_description()` (`usethis._file.pyproject_toml.name`) — Get the project description from pyproject.toml.
- `get_project_dict()` (`usethis._file.pyproject_toml.project`) — Get the contents of the [project] section from pyproject.toml.
- `remove_pyproject_toml()` (`usethis._file.pyproject_toml.remove`) — Remove the pyproject.toml file from the project.
- `get_requires_python()` (`usethis._file.pyproject_toml.requires_python`) — Get the requires-python constraint from pyproject.toml.
- `get_required_minor_python_versions()` (`usethis._file.pyproject_toml.requires_python`) — Get Python minor versions that match the project's requires-python constraint.
- `ensure_pyproject_validity()` (`usethis._file.pyproject_toml.valid`) — Ensure pyproject.toml has a valid structure, adding missing required fields.
- `prepare_pyproject_write()` (`usethis._file.pyproject_toml.write`) — Prepare the pyproject.toml file for a subprocess that will modify it.
- `edit_yaml()` (`usethis._file.yaml.io_`) — A context manager to modify a YAML file in-place, with managed read and write.
- `read_yaml()` (`usethis._file.yaml.io_`) — A context manager to read a YAML file.
- `update_ruamel_yaml_map()` (`usethis._file.yaml.update`) — Update the values of a ruamel.yaml map in-place using a diff-like algorithm.
- `lcs_list_update()` (`usethis._file.yaml.update`) — Update in-place using a longest common subsequence solver.
- `project_init()` (`usethis._init`) — Initialize the project by creating the pyproject.toml and project structure.
- `write_simple_requirements_txt()` (`usethis._init`) — Write a simple requirements.txt file with -e . and any project dependencies.
- `ensure_dep_declaration_file()` (`usethis._init`) — Ensure that the file where dependencies are declared exists, if necessary.
- `ensure_pyproject_toml()` (`usethis._init`) — Ensure that a pyproject.toml file exists, creating it if necessary.
- `get_github_latest_tag()` (`usethis._integrations.ci.github.tags`) — Get the name of the most recent tag on the default branch of a GitHub repository.
- `get_supported_minor_python_versions()` (`usethis._integrations.environ.python`) — Get supported Python versions for the current backend.
- `add_docs_dir()` (`usethis._integrations.mkdocs.core`) — Create the `docs` directory and an `docs/index.md` file if they do not exist.
- `remove_pre_commit_config()` (`usethis._integrations.pre_commit.core`) — Remove the .pre-commit-config.yaml file from the project.
- `install_pre_commit_hooks()` (`usethis._integrations.pre_commit.core`) — Install pre-commit hooks.
- `uninstall_pre_commit_hooks()` (`usethis._integrations.pre_commit.core`) — Uninstall pre-commit hooks.
- `add_repo()` (`usethis._integrations.pre_commit.hooks`) — Add a pre-commit repo configuration to the pre-commit configuration file.
- `insert_repo()` (`usethis._integrations.pre_commit.hooks`) — Insert a repo into the list of repos after the named predecessor hook.
- `add_placeholder_hook()` (`usethis._integrations.pre_commit.hooks`) — Add a placeholder hook to the pre-commit configuration with instructions for the user.
- `remove_hook()` (`usethis._integrations.pre_commit.hooks`) — Remove pre-commit hook configuration.
- `get_hook_ids()` (`usethis._integrations.pre_commit.hooks`) — Get the list of hook IDs currently configured in the pre-commit configuration file.
- `extract_hook_ids()` (`usethis._integrations.pre_commit.hooks`) — Extract all hook IDs from a pre-commit configuration model.
- `hooks_are_equivalent()` (`usethis._integrations.pre_commit.hooks`) — Check if two hooks are equivalent.
- `hook_ids_are_equivalent()` (`usethis._integrations.pre_commit.hooks`) — Check if two hook IDs are equivalent.
- `ensure_pre_commit_config_exists()` (`usethis._integrations.pre_commit.init`) — Ensure '.pre-commit-config.yaml' exists with minimal valid content.
- `get_system_language()` (`usethis._integrations.pre_commit.language`) — Get the appropriate 'system' language keyword based on pre-commit version.
- `get_pre_commit_version()` (`usethis._integrations.pre_commit.version`) — Get an inferred pre-commit version for usethis to target.
- `get_minimum_pre_commit_version()` (`usethis._integrations.pre_commit.version`) — Get the declared minimum supported pre-commit version from the configuration.
- `has_pyproject_toml_declared_build_system()` (`usethis._integrations.project.build`) — Check if a build system is declared in the project.
- `get_layered_architectures()` (`usethis._integrations.project.imports`) — Get the suggested layers for a package.
- `augment_pythonpath()` (`usethis._integrations.project.imports`) — Temporarily add a directory to the Python path.
- `get_source_dir_str()` (`usethis._integrations.project.layout`) — Get the source directory as a string ('src' or '.').
- `get_license_id()` (`usethis._integrations.project.license`) — Get the SPDX license identifier for the current project.
- `get_project_name()` (`usethis._integrations.project.name`) — The project name, from pyproject.toml if available or fallback to heuristics.
- `get_importable_packages()` (`usethis._integrations.project.packages`) — Get the names of packages in the source directory that can be imported.
- `fancy_model_dump()` (`usethis._integrations.pydantic.dump`) — Like `pydantic.model_dump` but with bespoke formatting options.
- `add_pytest_dir()` (`usethis._integrations.pytest.core`) — Create the tests directory and conftest.py if they do not already exist.
- `add_example_test()` (`usethis._integrations.pytest.core`) — Create an example test file in the tests directory if it does not already exist.
- `remove_pytest_dir()` (`usethis._integrations.pytest.core`) — Remove the tests directory if it contains only managed files.
- `get_readme_path()` (`usethis._integrations.readme.path`) — Return the path to the README file, searching for common README filenames.
- `get_markdown_readme_path()` (`usethis._integrations.readme.path`) — Return the path to the Markdown README file, raising an error if it is not Markdown.
- `get_sonar_project_properties()` (`usethis._integrations.sonarqube.config`) — Get contents for (or from) the sonar-project.properties file.
- `parallel()` (`usethis._pipeweld.containers`) — Create a Parallel pipeline composition from the given components.
- `series()` (`usethis._pipeweld.containers`) — Create a Series pipeline composition from the given components.
- `depgroup()` (`usethis._pipeweld.containers`) — Create a DepGroup pipeline composition tied to a named configuration group.
- `get_endpoint()` (`usethis._pipeweld.func`) — Get the last step name (endpoint) from a pipeline component.
- `get_predecessor()` (`usethis._pipeweld.func`) — Find the step that immediately precedes `step` in a pipeline component.
- `call_subprocess()` (`usethis._subprocess`) — Run a subprocess and return its stdout, raising SubprocessFailedError on failure.
- `change_cwd()` (`usethis._test`) — Change the working directory temporarily.
- `is_offline()` (`usethis._test`) — Return True if the current environment has no internet connectivity.
- `ensure_managed_file_exists()` (`usethis._tool.config`) — Ensure a file manager's managed file exists.
- `is_likely_used()` (`usethis._tool.heuristics`) — Determine whether a tool is likely used in the current project.
- `is_rule_covered_by()` (`usethis._tool.rule`) — Check if a rule is covered (subsumed) by a more general rule.
- `reconcile_rules()` (`usethis._tool.rule`) — Determine which rules to add and which existing rules to remove.
- `use_arch_tools()` (`usethis._toolset.arch`) — Add and configure architecture enforcement tools for the project.
- `use_doc_frameworks()` (`usethis._toolset.doc`) — Add and configure documentation framework tools for the project.
- `use_formatters()` (`usethis._toolset.format_`) — Add and configure code formatting tools for the project.
- `use_hook_framework()` (`usethis._toolset.hook`) — Add and configure git hook framework tools for the project.
- `use_linters()` (`usethis._toolset.lint`) — Add and configure linting tools for the project.
- `use_spellcheckers()` (`usethis._toolset.spellcheck`) — Add and configure spellchecking tools for the project.
- `use_test_frameworks()` (`usethis._toolset.test`) — Add and configure testing framework tools for the project.
- `use_typecheckers()` (`usethis._toolset.typecheck`) — Add and configure type checking tools for the project.
- `arch()` (`usethis._ui.interface.arch`) — Add recommended architecture analysis tools to the project.
- `author()` (`usethis._ui.interface.author`) — Add an author to the project metadata in pyproject.toml.
- `pypi()` (`usethis._ui.interface.badge`) — Add a badge with the version of your package on PyPI.
- `ruff()` (`usethis._ui.interface.badge`) — Add a badge for the Ruff linter.
- `ty()` (`usethis._ui.interface.badge`) — Add a badge for the ty type checker.
- `pre_commit()` (`usethis._ui.interface.badge`) — Add a badge for the pre-commit framework.
- `socket()` (`usethis._ui.interface.badge`) — Add a badge with your PyPI package's supply chain security rating from Socket.
- `usethis()` (`usethis._ui.interface.badge`) — Add a badge for usethis.
- `bitbucket()` (`usethis._ui.interface.badge`) — Add a badge for Bitbucket.
- `uv()` (`usethis._ui.interface.badge`) — Add a badge for the uv package manager.
- `pypi()` (`usethis._ui.interface.browse`) — Visit the PyPI project page for a package.
- `doc()` (`usethis._ui.interface.doc`) — Add a recommended documentation framework to the project.
- `docstyle()` (`usethis._ui.interface.docstyle`) — Configure the docstring style for the project.
- `format_()` (`usethis._ui.interface.format_`) — Add recommended formatters to the project.
- `hook()` (`usethis._ui.interface.hook`) — Add a recommended git hook framework to the project.
- `init()` (`usethis._ui.interface.init`) — Initialize a new project with recommended tooling.
- `lint()` (`usethis._ui.interface.lint`) — Add recommended linters to the project.
- `list()` (`usethis._ui.interface.list`) — Show the usage table of all available tools and their current status.
- `readme()` (`usethis._ui.interface.readme`) — Create or update the README.md file, optionally adding badges.
- `rule()` (`usethis._ui.interface.rule`) — Select, deselect, ignore, or unignore linter rules.
- `backend()` (`usethis._ui.interface.show`) — Show the inferred project manager backend, e.g. 'uv' or 'none'.
- `license()` (`usethis._ui.interface.show`) — Show the project license in SPDX format.
- `name()` (`usethis._ui.interface.show`) — Show the name of the project.
- `sonarqube()` (`usethis._ui.interface.show`) — Show the sonar-project.properties file for SonarQube.
- `spellcheck()` (`usethis._ui.interface.spellcheck`) — Add a recommended spellchecker to the project.
- `status()` (`usethis._ui.interface.status`) — Set the development status classifier for the project.
- `test()` (`usethis._ui.interface.test`) — Add a recommended testing framework to the project.
- `codespell()` (`usethis._ui.interface.tool`) — Use the codespell spellchecker: detect common spelling mistakes.
- `coverage_py()` (`usethis._ui.interface.tool`) — Use Coverage.py: a code coverage measurement tool.
- `deptry()` (`usethis._ui.interface.tool`) — Use the deptry linter: avoid missing or superfluous dependency declarations.
- `import_linter()` (`usethis._ui.interface.tool`) — Use Import Linter: enforce a self-imposed architecture on imports.
- `mkdocs()` (`usethis._ui.interface.tool`) — Use MkDocs: Generate project documentation sites with Markdown.
- `pre_commit()` (`usethis._ui.interface.tool`) — Use the pre-commit framework to manage and maintain pre-commit hooks.
- `pyproject_fmt()` (`usethis._ui.interface.tool`) — Use the pyproject-fmt linter: opinionated formatting of 'pyproject.toml' files.
- `pyproject_toml()` (`usethis._ui.interface.tool`) — Use a pyproject.toml file to configure the project.
- `pytest()` (`usethis._ui.interface.tool`) — Use the pytest testing framework.
- `requirements_txt()` (`usethis._ui.interface.tool`) — Use a requirements.txt file exported from the uv lockfile.
- `ruff()` (`usethis._ui.interface.tool`) — Use Ruff: an extremely fast Python linter and code formatter.
- `tach()` (`usethis._ui.interface.tool`) — Use Tach: enforce self-imposed dependency and interface rules.
- `ty()` (`usethis._ui.interface.tool`) — Use the ty type checker: an extremely fast Python type checker.
- `typecheck()` (`usethis._ui.interface.typecheck`) — Add a recommended type checker to the project.
- `version()` (`usethis._ui.interface.version`) — Print the installed version of usethis.
- `validate_or_raise()` (`usethis._validate`) — Validate `obj` against `type_`, raising a custom error on failure.
- `validate_or_default()` (`usethis._validate`) — Validate `obj` against `type_`, returning `default` on failure.

<!-- /sync:docs/functions.txt -->

## Agent Skills

The `.agents/skills` directory contains agent skills.

### Skills registry

#### usethis-specific skills

<!-- sync:docs/skills-directory.txt -->

- `usethis-agents`: Maintain AGENTS.md and agent skill configuration
- `usethis-cli-dogfood`: Dogfood new or modified CLI commands by running them against the usethis repo itself to catch edge cases
- `usethis-cli-modify`: Modify the usethis CLI layer (commands, options, help text) and keep documentation in sync
- `usethis-cli-user-test`: Simulate user testing for CLI commands by running them in a fresh temporary project to verify the happy path
- `usethis-file-create`: Guidance on where to place new files in the repository
- `usethis-file-remove`: Remove files from the project
- `usethis-github-actions-update`: Update GitHub Actions workflows
- `usethis-github-issue-create`: Create GitHub issues via the gh CLI to record lessons, track follow-up work, or file bugs discovered during development
- `usethis-pre-commit`: Guidance on pre-commit hooks — this project uses prek, not pre-commit directly
- `usethis-prek-add-hook`: Add a prek hook for dev
- `usethis-prek-hook-bespoke-create`: Write bespoke prek hooks as reusable Python scripts for custom checks
- `usethis-python-code`: Guidelines for Python code design decisions such as when to share vs. duplicate code
- `usethis-python-code-modify`: Modify Python code (e.g. refactor, add new code, or delete code)
- `usethis-python-enum`: Style and testing conventions for working with Python enums
- `usethis-python-functions`: Guidelines for Python function design, including return types and signature simplicity
- `usethis-python-module-layout-modify`: Modify the Python module layout (create, move, rename, or delete modules)
- `usethis-python-ruff`: Guidelines for complying with Ruff linter rules instead of suppressing them
- `usethis-python-test`: General guidelines for writing tests in the usethis project, including test class organization
- `usethis-python-test-affected-find`: Identify tests that are potentially affected by code changes, to catch regressions before CI
- `usethis-python-test-full-coverage`: Write tests that achieve full code coverage and verify coverage locally before pushing
- `usethis-qa-import-linter`: Use the Import Linter software on the usethis project
- `usethis-qa-static-checks`: Perform static code checks
- `usethis-skills-create`: Create new agent skills (SKILL.md files) following best practices for content quality, structure, and discoverability
- `usethis-skills-external-add`: Add an external (community) skill to the project from a third-party source, including installing it and documenting it in AGENTS.md
- `usethis-skills-external-install`: Reinstall already-tracked external skills from skills-lock.json (e.g. after a fresh clone)
- `usethis-skills-modify`: Enforce version bumping, scope checking, and content quality guidelines when modifying SKILL.md files

<!-- /sync:docs/skills-directory.txt -->

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
- ALWAYS use the `usethis-skills-modify` skill when modifying any agent skill (`SKILL.md` file). Do not edit skill files without it — it enforces version bumping, scope checking, and content quality guidelines. Similarly, ALWAYS use `usethis-skills-create` when creating a new skill.
- ALWAYS use `find-skills` to research new skill capabilities if there are difficult tasks, tasks in an unfamiliar domain, if you believe there is a lack of clarity or direction around precisely how to proceed, or if you get stuck or find something surprisingly challenging. When using this skill, please be sure to use the `usethis-skills-external-install` skill when deciding to install a new external skill.
- ALWAYS consider the `usethis-python-test-full-coverage` to be relevant: if your task involves
  writing or modifying code, always use this skill to write tests and verify full coverage
  before finishing. Aim for 100% coverage on new or changed code.
- ALWAYS consider the `usethis-qa-static-checks` to be relevant: if you think your task is complete, always run this skill to check for any issues before finishing. You must fix **all** static check failures, including pre-existing ones unrelated to your changes. This applies to ALL changes, including documentation-only changes and skill file edits — static checks catch sync issues, formatting problems, and other regressions that affect every file type. CI enforces checks on the entire codebase, so unfixed failures will block your PR. **After fixing any failure or making any further change, re-run ALL static checks again from scratch — even if you ran them moments ago.** It is expected and normal to run this skill repeatedly in a loop until every check passes cleanly.
- ALWAYS mention which skills you've used after completing any task, in PR descriptions, and comments.
- ALWAYS reference the relevant issue ID in PR descriptions using a closing keyword, e.g. `Resolves #123`. This ensures traceability between PRs and the issues they address.

## Lessons

When you are working on a problem, you are almost always going to encounter a difficulty. This is great - it's an opportunity for learning. ALWAYS make a note explicitly of what lessons you are drawing as you complete a task or when receiving user feedback. Try and keep this structured: consider the root cause of the difficulty, and how you overcame it. After finishing work on a task, report back all your lessons. Finally, ALWAYS use the `usethis-github-issue-create` skill to record each lesson as a GitHub issue so it can be triaged and tracked.
