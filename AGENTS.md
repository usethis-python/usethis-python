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

- `get_backend()` (`usethis._backend.dispatch`) — Get the current package manager backend.
- `is_poetry_used()` (`usethis._backend.poetry.detect`)
- `is_uv_available()` (`usethis._backend.uv.available`) — Check if the `uv` command is available in the current environment.
- `call_uv_subprocess()` (`usethis._backend.uv.call`) — Run a subprocess using the uv command-line tool.
- `_prepare_pyproject_write()` (`usethis._backend.uv.call`)
- `add_default_groups_via_uv()` (`usethis._backend.uv.call`) — Add default groups using the uv command-line tool.
- `add_dep_to_group_via_uv()` (`usethis._backend.uv.deps`)
- `remove_dep_from_group_via_uv()` (`usethis._backend.uv.deps`)
- `get_default_groups_via_uv()` (`usethis._backend.uv.deps`) — Get the default dependency groups from the uv configuration.
- `is_uv_used()` (`usethis._backend.uv.detect`)
- `opinionated_uv_init()` (`usethis._backend.uv.init`) — Subprocess `uv init` with opinionated arguments.
- `ensure_pyproject_toml_via_uv()` (`usethis._backend.uv.init`) — Create a pyproject.toml file using `uv init --bare`.
- `ensure_symlink_mode()` (`usethis._backend.uv.link_mode`) — Ensure that the symlink link mode is enabled.
- `ensure_uv_lock()` (`usethis._backend.uv.lockfile`)
- `get_available_uv_python_versions()` (`usethis._backend.uv.python`)
- `get_supported_uv_minor_python_versions()` (`usethis._backend.uv.python`)
- `_parse_python_version_from_uv_output()` (`usethis._backend.uv.python`)
- `uv_python_pin()` (`usethis._backend.uv.python`)
- `relative_path()` (`usethis._backend.uv.toml`)
- `get_uv_version()` (`usethis._backend.uv.version`)
- `next_breaking_uv_version()` (`usethis._backend.uv.version`) — Get the next breaking version for a uv version string, following semver.
- `set()` (`usethis._config`) — Temporarily change command options.
- `cpd()` (`usethis._config`) — Return the current project directory.
- `files_manager()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `relative_path()` (`usethis._config_file`)
- `plain_print()` (`usethis._console`)
- `table_print()` (`usethis._console`)
- `tick_print()` (`usethis._console`) — Print a ✔ success/completion message (green).
- `instruct_print()` (`usethis._console`) — Print a ☐ instruction the user must perform manually (red).
- `how_print()` (`usethis._console`) — Print a ☐ guidance message explaining how to do something (red).
- `info_print()` (`usethis._console`) — Print an informational message (blue).
- `err_print()` (`usethis._console`) — Print a ✗ error message to stderr (red).
- `warn_print()` (`usethis._console`) — Print a ⚠ warning message (yellow; deduplicated).
- `_cached_warn_print()` (`usethis._console`)
- `get_icon_mode()` (`usethis._console`) — Detect terminal's icon support level.
- `_get_icon()` (`usethis._console`) — Get the appropriate icon based on terminal capabilities.
- `_get_stdout_encoding()` (`usethis._console`)
- `add_author()` (`usethis._core.author`)
- `get_pre_commit_badge()` (`usethis._core.badge`)
- `get_pypi_badge()` (`usethis._core.badge`)
- `get_ruff_badge()` (`usethis._core.badge`)
- `get_socket_badge()` (`usethis._core.badge`)
- `get_ty_badge()` (`usethis._core.badge`)
- `get_uv_badge()` (`usethis._core.badge`)
- `get_bitbucket_badge()` (`usethis._core.badge`)
- `get_usethis_badge()` (`usethis._core.badge`)
- `get_badge_order()` (`usethis._core.badge`)
- `add_badge()` (`usethis._core.badge`)
- `_get_prerequisites()` (`usethis._core.badge`) — Get the prerequisites for a badge.
- `_ensure_final_newline()` (`usethis._core.badge`)
- `is_blank()` (`usethis._core.badge`)
- `is_header()` (`usethis._core.badge`)
- `is_badge()` (`usethis._core.badge`)
- `remove_badge()` (`usethis._core.badge`)
- `name()` (`usethis._core.badge`)
- `equivalent_to()` (`usethis._core.badge`)
- `update_from_line()` (`usethis._core.badge`)
- `_count_h1_open_tags()` (`usethis._core.badge`)
- `_count_h1_close_tags()` (`usethis._core.badge`)
- `browse_pypi()` (`usethis._core.browse`)
- `use_docstyle()` (`usethis._core.docstyle`)
- `_rich_status()` (`usethis._core.list`) — Get richly formatted status.
- `_rich_category()` (`usethis._core.list`) — Get richly formatted category.
- `show_usage_table()` (`usethis._core.list`) — Show the usage table.
- `get_usage_table()` (`usethis._core.list`) — Get the usage table.
- `rich_style()` (`usethis._core.list`) — Get the Rich style for the row.
- `to_rich()` (`usethis._core.list`) — Convert the table to a rich Table.
- `add_readme()` (`usethis._core.readme`) — Add a README.md file to the project.
- `select_rules()` (`usethis._core.rule`)
- `deselect_rules()` (`usethis._core.rule`)
- `ignore_rules()` (`usethis._core.rule`)
- `unignore_rules()` (`usethis._core.rule`)
- `get_rules_mapping()` (`usethis._core.rule`)
- `show_backend()` (`usethis._core.show`)
- `show_name()` (`usethis._core.show`)
- `show_sonarqube_config()` (`usethis._core.show`)
- `_output()` (`usethis._core.show`)
- `use_development_status()` (`usethis._core.status`)
- `use_codespell()` (`usethis._core.tool`)
- `use_coverage_py()` (`usethis._core.tool`)
- `use_deptry()` (`usethis._core.tool`)
- `use_import_linter()` (`usethis._core.tool`)
- `use_mkdocs()` (`usethis._core.tool`)
- `use_pre_commit()` (`usethis._core.tool`)
- `_add_all_tools_pre_commit_configs()` (`usethis._core.tool`)
- `use_pyproject_fmt()` (`usethis._core.tool`)
- `use_pyproject_toml()` (`usethis._core.tool`)
- `use_pytest()` (`usethis._core.tool`)
- `use_requirements_txt()` (`usethis._core.tool`)
- `use_ruff()` (`usethis._core.tool`) — Add Ruff to the project.
- `_get_basic_rule_config()` (`usethis._core.tool`) — Get the basic rule config for Ruff.
- `use_ty()` (`usethis._core.tool`)
- `use_tool()` (`usethis._core.tool`) — General dispatch function to add or remove a tool to/from the project.
- `__call__()` (`usethis._core.tool`) — A function that adds/removes a tool to/from the project.
- `get_project_deps()` (`usethis._deps`) — Get all project dependencies.
- `get_dep_groups()` (`usethis._deps`) — Get all dependency groups from the dependency-groups section of pyproject.toml.
- `get_deps_from_group()` (`usethis._deps`) — Get the list of dependencies in a named dependency group.
- `register_default_group()` (`usethis._deps`) — Register a group in the default-groups configuration if it's not already there.
- `add_default_groups()` (`usethis._deps`)
- `get_default_groups()` (`usethis._deps`) — Get the list of default dependency groups installed automatically by the package manager.
- `ensure_dev_group_is_defined()` (`usethis._deps`)
- `is_dep_satisfied_in()` (`usethis._deps`) — Check if a dependency is satisfied by any dependency in the given list.
- `_is_dep_satisfied_by()` (`usethis._deps`)
- `remove_deps_from_group()` (`usethis._deps`) — Remove dependencies from the named group if present.
- `is_dep_in_any_group()` (`usethis._deps`) — Check if a dependency exists in any dependency group.
- `add_deps_to_group()` (`usethis._deps`) — Add dependencies to a named group using PEP 735 dependency groups.
- `_register_default_group()` (`usethis._deps`)
- `is_pre_commit_used()` (`usethis._detect.pre_commit`) — Check if pre-commit is being used in the project.
- `is_readme_used()` (`usethis._detect.readme`) — Check if the README.md file is used.
- `next_breaking_version()` (`usethis._fallback`) — Get the next breaking version for a version string, following semver.
- `get_project_name_from_dir()` (`usethis._file.dir`)
- `_as_dict()` (`usethis._file.ini.io_`)
- `_remove_option()` (`usethis._file.ini.io_`)
- `_remove_section()` (`usethis._file.ini.io_`)
- `_itermatches()` (`usethis._file.ini.io_`) — Iterate through an iterable and find all matches for a key.
- `_ensure_newline()` (`usethis._file.ini.io_`) — Add a newline to the INI file.
- `__enter__()` (`usethis._file.ini.io_`)
- `read_file()` (`usethis._file.ini.io_`)
- `_dump_content()` (`usethis._file.ini.io_`)
- `_parse_content()` (`usethis._file.ini.io_`)
- `get()` (`usethis._file.ini.io_`)
- `commit()` (`usethis._file.ini.io_`)
- `_content()` (`usethis._file.ini.io_`)
- `_content()` (`usethis._file.ini.io_`)
- `_validate_lock()` (`usethis._file.ini.io_`)
- `__contains__()` (`usethis._file.ini.io_`) — Check if the INI file contains a value at the given key.
- `__getitem__()` (`usethis._file.ini.io_`)
- `set_value()` (`usethis._file.ini.io_`) — Set a value in the INI file.
- `_set_value_in_root()` (`usethis._file.ini.io_`)
- `_set_value_in_section()` (`usethis._file.ini.io_`)
- `_set_value_in_option()` (`usethis._file.ini.io_`)
- `_validated_set()` (`usethis._file.ini.io_`)
- `_validated_append()` (`usethis._file.ini.io_`)
- `__delitem__()` (`usethis._file.ini.io_`) — Delete a value in the INI file.
- `_delete_strkeys()` (`usethis._file.ini.io_`) — Delete a specific value in the INI file.
- `extend_list()` (`usethis._file.ini.io_`) — Extend a list in the INI file.
- `_extend_list_in_option()` (`usethis._file.ini.io_`)
- `_remove_from_list_in_option()` (`usethis._file.ini.io_`)
- `remove_from_list()` (`usethis._file.ini.io_`) — Remove values from a list in the INI file.
- `relative_path()` (`usethis._file.manager`) — Return the relative path to the file.
- `__init__()` (`usethis._file.manager`)
- `__eq__()` (`usethis._file.manager`)
- `__hash__()` (`usethis._file.manager`)
- `name()` (`usethis._file.manager`)
- `__repr__()` (`usethis._file.manager`)
- `__enter__()` (`usethis._file.manager`)
- `__exit__()` (`usethis._file.manager`)
- `get()` (`usethis._file.manager`) — Retrieve the document, reading from disk if necessary.
- `commit()` (`usethis._file.manager`) — Store the given document in memory for deferred writing.
- `revert()` (`usethis._file.manager`) — Clear the stored document without writing to disk.
- `write_file()` (`usethis._file.manager`) — Write the stored document to disk if there are changes.
- `read_file()` (`usethis._file.manager`) — Read the document from disk and store it in memory.
- `_dump_content()` (`usethis._file.manager`) — Return the content of the document as a string.
- `_parse_content()` (`usethis._file.manager`) — Parse the content of the document.
- `_content()` (`usethis._file.manager`)
- `_content()` (`usethis._file.manager`)
- `_validate_lock()` (`usethis._file.manager`)
- `is_locked()` (`usethis._file.manager`)
- `lock()` (`usethis._file.manager`)
- `unlock()` (`usethis._file.manager`)
- `__contains__()` (`usethis._file.manager`) — Check if a key exists in the configuration file.
- `__getitem__()` (`usethis._file.manager`)
- `__setitem__()` (`usethis._file.manager`) — Set a value in the configuration file.
- `__delitem__()` (`usethis._file.manager`) — Remove a value from the configuration file.
- `set_value()` (`usethis._file.manager`) — Set a value in the configuration file.
- `extend_list()` (`usethis._file.manager`) — Extend a list in the configuration file.
- `remove_from_list()` (`usethis._file.manager`) — Remove values from a list in the configuration file.
- `deep_merge()` (`usethis._file.merge`) — Recursively merge source into target in place, returning target.
- `print_keys()` (`usethis._file.print_`) — Convert a list of keys to a string.
- `name()` (`usethis._file.pyproject_toml.errors`) — The name of the file that could not be decoded.
- `name()` (`usethis._file.pyproject_toml.errors`) — The name of the file that has a configuration error.
- `relative_path()` (`usethis._file.pyproject_toml.io_`)
- `__enter__()` (`usethis._file.pyproject_toml.io_`)
- `read_file()` (`usethis._file.pyproject_toml.io_`)
- `_validate_lock()` (`usethis._file.pyproject_toml.io_`)
- `set_value()` (`usethis._file.pyproject_toml.io_`) — Set a value in the pyproject.toml configuration file.
- `__delitem__()` (`usethis._file.pyproject_toml.io_`) — Remove a value from the pyproject.toml configuration file.
- `get_name()` (`usethis._file.pyproject_toml.name`) — Get the project name from pyproject.toml.
- `get_description()` (`usethis._file.pyproject_toml.name`)
- `get_project_dict()` (`usethis._file.pyproject_toml.project`)
- `remove_pyproject_toml()` (`usethis._file.pyproject_toml.remove`)
- `get_requires_python()` (`usethis._file.pyproject_toml.requires_python`) — Get the requires-python constraint from pyproject.toml.
- `get_required_minor_python_versions()` (`usethis._file.pyproject_toml.requires_python`) — Get Python minor versions that match the project's requires-python constraint.
- `_get_minimum_minor_python_version_tuple()` (`usethis._file.pyproject_toml.requires_python`) — Get the minimum (major, minor) Python version from requires-python specifier.
- `_get_maximum_minor_python_version_tuple()` (`usethis._file.pyproject_toml.requires_python`) — Get the maximum (major, minor) Python version from requires-python specifier.
- `_get_maximum_python_minor_version()` (`usethis._file.pyproject_toml.requires_python`) — Get the hard-coded maximum minor version for a given Python major version.
- `ensure_pyproject_validity()` (`usethis._file.pyproject_toml.valid`)
- `_ensure_project_section()` (`usethis._file.pyproject_toml.valid`)
- `_ensure_project_version()` (`usethis._file.pyproject_toml.valid`)
- `_ensure_project_name()` (`usethis._file.pyproject_toml.valid`)
- `name()` (`usethis._file.setup_cfg.errors`) — The name of the file that could not be decoded.
- `relative_path()` (`usethis._file.setup_cfg.io_`)
- `__enter__()` (`usethis._file.setup_cfg.io_`)
- `read_file()` (`usethis._file.setup_cfg.io_`)
- `_validate_lock()` (`usethis._file.setup_cfg.io_`)
- `set_value()` (`usethis._file.setup_cfg.io_`) — Set a value in the pyproject.toml configuration file.
- `__delitem__()` (`usethis._file.setup_cfg.io_`) — Remove a value from the pyproject.toml configuration file.
- `_set_value_in_existing()` (`usethis._file.toml.io_`) — Set a new value in an existing container.
- `_validate_keys()` (`usethis._file.toml.io_`) — Validate the keys.
- `_raise_already_set()` (`usethis._file.toml.io_`) — Raise an error if the configuration is already set.
- `_get_unified_key()` (`usethis._file.toml.io_`)
- `__enter__()` (`usethis._file.toml.io_`)
- `read_file()` (`usethis._file.toml.io_`)
- `_dump_content()` (`usethis._file.toml.io_`)
- `_parse_content()` (`usethis._file.toml.io_`)
- `get()` (`usethis._file.toml.io_`)
- `commit()` (`usethis._file.toml.io_`)
- `_content()` (`usethis._file.toml.io_`)
- `_content()` (`usethis._file.toml.io_`)
- `_validate_lock()` (`usethis._file.toml.io_`)
- `__contains__()` (`usethis._file.toml.io_`) — Check if the TOML file contains a value.
- `__getitem__()` (`usethis._file.toml.io_`)
- `set_value()` (`usethis._file.toml.io_`) — Set a value in the TOML file.
- `__delitem__()` (`usethis._file.toml.io_`) — Delete a value in the TOML file.
- `extend_list()` (`usethis._file.toml.io_`)
- `remove_from_list()` (`usethis._file.toml.io_`) — Remove values from a list in the TOML file.
- `_set_value_in_existing()` (`usethis._file.yaml.io_`)
- `_validate_keys()` (`usethis._file.yaml.io_`) — Validate the keys.
- `edit_yaml()` (`usethis._file.yaml.io_`) — A context manager to modify a YAML file in-place, with managed read and write.
- `read_yaml()` (`usethis._file.yaml.io_`) — A context manager to read a YAML file.
- `_get_yaml_document()` (`usethis._file.yaml.io_`)
- `__enter__()` (`usethis._file.yaml.io_`)
- `read_file()` (`usethis._file.yaml.io_`)
- `_dump_content()` (`usethis._file.yaml.io_`) — Return the content of the document as a string.
- `get()` (`usethis._file.yaml.io_`)
- `commit()` (`usethis._file.yaml.io_`)
- `_parse_content()` (`usethis._file.yaml.io_`) — Parse the content of the document.
- `_content()` (`usethis._file.yaml.io_`)
- `_content()` (`usethis._file.yaml.io_`)
- `_validate_lock()` (`usethis._file.yaml.io_`)
- `__contains__()` (`usethis._file.yaml.io_`) — Check if the YAML file contains a value.
- `__getitem__()` (`usethis._file.yaml.io_`)
- `set_value()` (`usethis._file.yaml.io_`) — Set a value in the YAML file.
- `__delitem__()` (`usethis._file.yaml.io_`) — Delete a value in the TOML file.
- `extend_list()` (`usethis._file.yaml.io_`) — Extend a list in the configuration file.
- `remove_from_list()` (`usethis._file.yaml.io_`) — Remove values from a list in the configuration file.
- `update_ruamel_yaml_map()` (`usethis._file.yaml.update`) — Update the values of a ruamel.yaml map in-place using a diff-like algorithm.
- `lcs_list_update()` (`usethis._file.yaml.update`) — Update in-place using a longest common subsequence solver.
- `_shared_id_sequences()` (`usethis._file.yaml.update`) — Map list elements to integers which are equal iff the objects are equal by value.
- `project_init()` (`usethis._init`)
- `_regularize_package_name()` (`usethis._init`) — Regularize the package name to be suitable for Python packaging.
- `write_simple_requirements_txt()` (`usethis._init`) — Write a simple requirements.txt file with -e . and any project dependencies.
- `ensure_dep_declaration_file()` (`usethis._init`) — Ensure that the file where dependencies are declared exists, if necessary.
- `ensure_pyproject_toml()` (`usethis._init`)
- `get_github_latest_tag()` (`usethis._integrations.ci.github.tags`) — Get the name of the most recent tag on the default branch of a GitHub repository.
- `get_supported_minor_python_versions()` (`usethis._integrations.environ.python`) — Get supported Python versions for the current backend.
- `add_docs_dir()` (`usethis._integrations.mkdocs.core`) — Create the `docs` directory and an `docs/index.md` file if they do not exist.
- `remove_pre_commit_config()` (`usethis._integrations.pre_commit.core`)
- `install_pre_commit_hooks()` (`usethis._integrations.pre_commit.core`) — Install pre-commit hooks.
- `uninstall_pre_commit_hooks()` (`usethis._integrations.pre_commit.core`) — Uninstall pre-commit hooks.
- `name()` (`usethis._integrations.pre_commit.errors`) — The name of the file that has a configuration error.
- `add_repo()` (`usethis._integrations.pre_commit.hooks`) — Add a pre-commit repo configuration to the pre-commit configuration file.
- `insert_repo()` (`usethis._integrations.pre_commit.hooks`)
- `_report_adding_repo()` (`usethis._integrations.pre_commit.hooks`) — Append a repo to the end of the existing repos with message.
- `add_placeholder_hook()` (`usethis._integrations.pre_commit.hooks`)
- `_get_placeholder_repo_config()` (`usethis._integrations.pre_commit.hooks`)
- `remove_hook()` (`usethis._integrations.pre_commit.hooks`) — Remove pre-commit hook configuration.
- `get_hook_ids()` (`usethis._integrations.pre_commit.hooks`)
- `extract_hook_ids()` (`usethis._integrations.pre_commit.hooks`)
- `hooks_are_equivalent()` (`usethis._integrations.pre_commit.hooks`) — Check if two hooks are equivalent.
- `hook_ids_are_equivalent()` (`usethis._integrations.pre_commit.hooks`) — Check if two hook IDs are equivalent.
- `ensure_pre_commit_config_exists()` (`usethis._integrations.pre_commit.init`) — Ensure '.pre-commit-config.yaml' exists with minimal valid content.
- `get_system_language()` (`usethis._integrations.pre_commit.language`) — Get the appropriate 'system' language keyword based on pre-commit version.
- `get_pre_commit_version()` (`usethis._integrations.pre_commit.version`) — Get an inferred pre-commit version for usethis to target.
- `get_minimum_pre_commit_version()` (`usethis._integrations.pre_commit.version`) — Get the declared minimum supported pre-commit version from the configuration.
- `_pre_commit_fancy_dump()` (`usethis._integrations.pre_commit.yaml`)
- `relative_path()` (`usethis._integrations.pre_commit.yaml`)
- `model_validate()` (`usethis._integrations.pre_commit.yaml`) — Validate the current document content against the JSON schema.
- `commit_model()` (`usethis._integrations.pre_commit.yaml`)
- `has_pyproject_toml_declared_build_system()` (`usethis._integrations.project.build`) — Check if a build system is declared in the project.
- `get_layered_architectures()` (`usethis._integrations.project.imports`) — Get the suggested layers for a package.
- `_get_module_layered_architecture()` (`usethis._integrations.project.imports`)
- `_get_child_dependencies()` (`usethis._integrations.project.imports`) — For each child submodule, give a set of the sibling submodules it depends on.
- `_filter_to_submodule()` (`usethis._integrations.project.imports`)
- `_narrow_to_submodule()` (`usethis._integrations.project.imports`)
- `_get_graph()` (`usethis._integrations.project.imports`)
- `augment_pythonpath()` (`usethis._integrations.project.imports`) — Temporarily add a directory to the Python path.
- `module_count()` (`usethis._integrations.project.imports`) — Count the number of modules in the architecture.
- `get_source_dir_str()` (`usethis._integrations.project.layout`) — Get the source directory as a string ('src' or '.').
- `get_project_name()` (`usethis._integrations.project.name`) — The project name, from pyproject.toml if available or fallback to heuristics.
- `get_importable_packages()` (`usethis._integrations.project.packages`) — Get the names of packages in the source directory that can be imported.
- `_get_packages_in_dir()` (`usethis._integrations.project.packages`) — Get the names of packages in the given directory.
- `_is_excluded()` (`usethis._integrations.project.packages`) — Check if the given name is excluded from importable packages.
- `fancy_model_dump()` (`usethis._integrations.pydantic.dump`) — Like `pydantic.model_dump` but with bespoke formatting options.
- `_fancy_model_dump_list()` (`usethis._integrations.pydantic.dump`)
- `_fancy_model_dump_dict()` (`usethis._integrations.pydantic.dump`)
- `_fancy_model_dump_base_model()` (`usethis._integrations.pydantic.dump`)
- `_get_value_ref()` (`usethis._integrations.pydantic.dump`)
- `add_pytest_dir()` (`usethis._integrations.pytest.core`)
- `remove_pytest_dir()` (`usethis._integrations.pytest.core`)
- `get_readme_path()` (`usethis._integrations.readme.path`)
- `get_markdown_readme_path()` (`usethis._integrations.readme.path`)
- `get_sonar_project_properties()` (`usethis._integrations.sonarqube.config`) — Get contents for (or from) the sonar-project.properties file.
- `_get_sonarqube_project_key()` (`usethis._integrations.sonarqube.config`)
- `_is_sonarqube_verbose()` (`usethis._integrations.sonarqube.config`)
- `_get_sonarqube_exclusions()` (`usethis._integrations.sonarqube.config`)
- `_validate_project_key()` (`usethis._integrations.sonarqube.config`) — Validate the SonarQube project key.
- `parallel()` (`usethis._pipeweld.containers`)
- `series()` (`usethis._pipeweld.containers`)
- `depgroup()` (`usethis._pipeweld.containers`)
- `__hash__()` (`usethis._pipeweld.containers`)
- `__getitem__()` (`usethis._pipeweld.containers`)
- `__setitem__()` (`usethis._pipeweld.containers`)
- `__eq__()` (`usethis._pipeweld.containers`)
- `__len__()` (`usethis._pipeweld.containers`)
- `__hash__()` (`usethis._pipeweld.containers`)
- `__or__()` (`usethis._pipeweld.containers`)
- `__eq__()` (`usethis._pipeweld.containers`)
- `__len__()` (`usethis._pipeweld.containers`)
- `__hash__()` (`usethis._pipeweld.containers`)
- `_has_any_steps()` (`usethis._pipeweld.func`)
- `_flatten_partition()` (`usethis._pipeweld.func`)
- `_op_series_merge_partitions()` (`usethis._pipeweld.func`)
- `_parallel_merge_partitions()` (`usethis._pipeweld.func`)
- `_collapsed_union()` (`usethis._pipeweld.func`)
- `_get_instructions_for_insertion()` (`usethis._pipeweld.func`) — Get the instructions to insert a component after the given step.
- `_concat()` (`usethis._pipeweld.func`)
- `_union()` (`usethis._pipeweld.func`)
- `get_endpoint()` (`usethis._pipeweld.func`)
- `add()` (`usethis._pipeweld.func`)
- `partition_component()` (`usethis._pipeweld.func`)
- `_partition_series_component()` (`usethis._pipeweld.func`)
- `_partition_parallel_component()` (`usethis._pipeweld.func`)
- `_partition_depgroup_component()` (`usethis._pipeweld.func`)
- `_insert_step()` (`usethis._pipeweld.func`)
- `_insert_before_postrequisites()` (`usethis._pipeweld.func`)
- `from_string()` (`usethis._python.version`) — Parse version string like '3.10.5' or '3.13' or '3.14.0a3'.
- `to_short_string()` (`usethis._python.version`) — Return X.Y format (e.g., '3.10').
- `to_short_tuple()` (`usethis._python.version`) — Return (major, minor) as integers.
- `__str__()` (`usethis._python.version`) — Return full version string.
- `from_interpreter()` (`usethis._python.version`) — Get the Python version from the current interpreter.
- `call_subprocess()` (`usethis._subprocess`)
- `change_cwd()` (`usethis._test`) — Change the working directory temporarily.
- `is_offline()` (`usethis._test`)
- `invoke_safe()` (`usethis._test`)
- `invoke()` (`usethis._test`)
- `print_how_to_use()` (`usethis._tool.base`) — Print instructions for using the tool.
- `how_to_use_cmd()` (`usethis._tool.base`) — The command used when explaining to run the tool.
- `how_to_use_pre_commit_hook_id()` (`usethis._tool.base`) — The pre-commit hook ID to use when explaining how to run via pre-commit.
- `is_used()` (`usethis._tool.base`) — Whether the tool is being used in the current project.
- `add_dev_deps()` (`usethis._tool.base`)
- `remove_dev_deps()` (`usethis._tool.base`)
- `add_test_deps()` (`usethis._tool.base`)
- `remove_test_deps()` (`usethis._tool.base`)
- `add_doc_deps()` (`usethis._tool.base`)
- `remove_doc_deps()` (`usethis._tool.base`)
- `add_pre_commit_config()` (`usethis._tool.base`) — Add the tool's pre-commit configuration.
- `remove_pre_commit_repo_configs()` (`usethis._tool.base`) — Remove the tool's pre-commit configuration.
- `migrate_config_to_pre_commit()` (`usethis._tool.base`) — Migrate the tool's configuration to pre-commit.
- `migrate_config_from_pre_commit()` (`usethis._tool.base`) — Migrate the tool's configuration from pre-commit.
- `is_config_present()` (`usethis._tool.base`) — Whether any of the tool's managed config sections are present.
- `add_configs()` (`usethis._tool.base`) — Add the tool's configuration sections.
- `_add_config_item()` (`usethis._tool.base`) — Add a specific configuration item using specified file managers.
- `remove_configs()` (`usethis._tool.base`) — Remove the tool's configuration sections.
- `remove_managed_files()` (`usethis._tool.base`) — Remove all files managed by this tool.
- `get_install_method()` (`usethis._tool.base`) — Infer the method used to install the tool, return None if uninstalled.
- `_get_select_keys()` (`usethis._tool.base`) — Get the configuration keys for selected rules.
- `select_rules()` (`usethis._tool.base`) — Select the rules managed by the tool.
- `_get_ignore_keys()` (`usethis._tool.base`) — Get the configuration keys for ignored rules.
- `ignore_rules()` (`usethis._tool.base`) — Ignore rules managed by the tool.
- `unignore_rules()` (`usethis._tool.base`) — Stop ignoring rules managed by the tool.
- `deselect_rules()` (`usethis._tool.base`) — Deselect the rules managed by the tool.
- `_get_no_config_value()` (`usethis._tool.config`)
- `ensure_managed_file_exists()` (`usethis._tool.config`) — Ensure a file manager's managed file exists.
- `from_flat()` (`usethis._tool.config`)
- `empty()` (`usethis._tool.config`)
- `is_present()` (`usethis._tool.config`) — Check whether any managed configuration in this spec is present on disk.
- `paths()` (`usethis._tool.config`) — Get the absolute paths to the config files associated with this item.
- `is_likely_used()` (`usethis._tool.heuristics`) — Determine whether a tool is likely used in the current project.
- `print_how_to_use()` (`usethis._tool.impl.base.codespell`)
- `test_deps()` (`usethis._tool.impl.base.coverage_py`)
- `print_how_to_use()` (`usethis._tool.impl.base.coverage_py`)
- `select_rules()` (`usethis._tool.impl.base.deptry`) — Does nothing for deptry - all rules are automatically enabled by default.
- `selected_rules()` (`usethis._tool.impl.base.deptry`) — No notion of selection for deptry.
- `deselect_rules()` (`usethis._tool.impl.base.deptry`) — Does nothing for deptry - all rules are automatically enabled by default.
- `ignored_rules()` (`usethis._tool.impl.base.deptry`)
- `_get_ignore_keys()` (`usethis._tool.impl.base.deptry`) — Get the keys for the ignored rules in the given file manager.
- `_is_inp_rule_selected()` (`usethis._tool.impl.base.import_linter`)
- `_is_inp_rule()` (`usethis._tool.impl.base.import_linter`)
- `is_used()` (`usethis._tool.impl.base.import_linter`) — Check if the Import Linter tool is used in the project.
- `print_how_to_use()` (`usethis._tool.impl.base.import_linter`)
- `print_how_to_use()` (`usethis._tool.impl.base.mkdocs`)
- `is_used()` (`usethis._tool.impl.base.pre_commit`)
- `print_how_to_use()` (`usethis._tool.impl.base.pre_commit`)
- `migrate_config_to_pre_commit()` (`usethis._tool.impl.base.pre_commit`)
- `migrate_config_from_pre_commit()` (`usethis._tool.impl.base.pre_commit`)
- `print_how_to_use()` (`usethis._tool.impl.base.pyproject_toml`)
- `remove_managed_files()` (`usethis._tool.impl.base.pyproject_toml`)
- `test_deps()` (`usethis._tool.impl.base.pytest`)
- `print_how_to_use()` (`usethis._tool.impl.base.pytest`)
- `get_active_config_file_managers()` (`usethis._tool.impl.base.pytest`)
- `print_how_to_use()` (`usethis._tool.impl.base.requirements_txt`)
- `print_how_to_use()` (`usethis._tool.impl.base.ruff`) — Print how to use the Ruff tool.
- `print_how_to_use_linter()` (`usethis._tool.impl.base.ruff`)
- `print_how_to_use_formatter()` (`usethis._tool.impl.base.ruff`)
- `pre_commit_config()` (`usethis._tool.impl.base.ruff`)
- `selected_rules()` (`usethis._tool.impl.base.ruff`) — Get the Ruff rules selected in the project.
- `ignored_rules()` (`usethis._tool.impl.base.ruff`) — Get the Ruff rules ignored in the project.
- `ignore_rules_in_glob()` (`usethis._tool.impl.base.ruff`) — Ignore Ruff rules in the project for a specific glob pattern.
- `unignore_rules_in_glob()` (`usethis._tool.impl.base.ruff`) — Stop ignoring Ruff rules in the project for a specific glob pattern.
- `get_ignored_rules_in_glob()` (`usethis._tool.impl.base.ruff`) — Get the Ruff rules ignored in the project for a specific glob pattern.
- `apply_rule_config()` (`usethis._tool.impl.base.ruff`) — Apply the Ruff rules associated with a rule config to the project.
- `remove_rule_config()` (`usethis._tool.impl.base.ruff`) — Remove the Ruff rules associated with a rule config from the project.
- `set_docstyle()` (`usethis._tool.impl.base.ruff`)
- `get_docstyle()` (`usethis._tool.impl.base.ruff`) — Get the docstring style set in the project.
- `are_pydocstyle_rules_selected()` (`usethis._tool.impl.base.ruff`) — Check if pydocstyle rules are selected in the configuration.
- `is_pydocstyle_rule()` (`usethis._tool.impl.base.ruff`)
- `_get_select_keys()` (`usethis._tool.impl.base.ruff`) — Get the keys for the selected rules in the given file manager.
- `_get_ignore_keys()` (`usethis._tool.impl.base.ruff`) — Get the keys for the ignored rules in the given file manager.
- `_get_per_file_ignore_keys()` (`usethis._tool.impl.base.ruff`) — Get the keys for the per-file ignored rules in the given file manager.
- `_get_docstyle_keys()` (`usethis._tool.impl.base.ruff`) — Get the keys for the docstyle rules in the given file manager.
- `is_linter_used()` (`usethis._tool.impl.base.ruff`) — Check if the linter is used in the project.
- `is_linter_config_present()` (`usethis._tool.impl.base.ruff`)
- `is_formatter_used()` (`usethis._tool.impl.base.ruff`) — Check if the formatter is used in the project.
- `is_formatter_config_present()` (`usethis._tool.impl.base.ruff`)
- `is_no_subtool_config_present()` (`usethis._tool.impl.base.ruff`) — Check if no subtool config is present.
- `print_how_to_use()` (`usethis._tool.impl.base.ty`)
- `meta()` (`usethis._tool.impl.spec.codespell`)
- `preferred_file_manager()` (`usethis._tool.impl.spec.codespell`)
- `raw_cmd()` (`usethis._tool.impl.spec.codespell`)
- `dev_deps()` (`usethis._tool.impl.spec.codespell`)
- `pre_commit_config()` (`usethis._tool.impl.spec.codespell`)
- `config_spec()` (`usethis._tool.impl.spec.codespell`)
- `meta()` (`usethis._tool.impl.spec.coverage_py`)
- `preferred_file_manager()` (`usethis._tool.impl.spec.coverage_py`)
- `config_spec()` (`usethis._tool.impl.spec.coverage_py`)
- `_get_source()` (`usethis._tool.impl.spec.coverage_py`)
- `meta()` (`usethis._tool.impl.spec.deptry`)
- `raw_cmd()` (`usethis._tool.impl.spec.deptry`)
- `dev_deps()` (`usethis._tool.impl.spec.deptry`)
- `pre_commit_config()` (`usethis._tool.impl.spec.deptry`)
- `config_spec()` (`usethis._tool.impl.spec.deptry`)
- `_importlinter_warn_no_packages_found()` (`usethis._tool.impl.spec.import_linter`)
- `meta()` (`usethis._tool.impl.spec.import_linter`)
- `raw_cmd()` (`usethis._tool.impl.spec.import_linter`)
- `dev_deps()` (`usethis._tool.impl.spec.import_linter`)
- `preferred_file_manager()` (`usethis._tool.impl.spec.import_linter`)
- `config_spec()` (`usethis._tool.impl.spec.import_linter`)
- `_are_active_ini_contracts()` (`usethis._tool.impl.spec.import_linter`)
- `_is_root_package_singular()` (`usethis._tool.impl.spec.import_linter`)
- `_get_layered_architecture_by_module_by_root_package()` (`usethis._tool.impl.spec.import_linter`)
- `_get_resolution()` (`usethis._tool.impl.spec.import_linter`)
- `_get_file_manager_by_relative_path()` (`usethis._tool.impl.spec.import_linter`)
- `pre_commit_config()` (`usethis._tool.impl.spec.import_linter`)
- `get_root_packages()` (`usethis._tool.impl.spec.import_linter`)
- `meta()` (`usethis._tool.impl.spec.mkdocs`)
- `doc_deps()` (`usethis._tool.impl.spec.mkdocs`)
- `preferred_file_manager()` (`usethis._tool.impl.spec.mkdocs`) — If there is no currently active config file, this is the preferred one.
- `config_spec()` (`usethis._tool.impl.spec.mkdocs`) — Get the configuration specification for this tool.
- `meta()` (`usethis._tool.impl.spec.pre_commit`)
- `raw_cmd()` (`usethis._tool.impl.spec.pre_commit`)
- `dev_deps()` (`usethis._tool.impl.spec.pre_commit`)
- `pre_commit_config()` (`usethis._tool.impl.spec.pre_commit`) — Get the pre-commit configurations for the tool.
- `meta()` (`usethis._tool.impl.spec.pyproject_fmt`)
- `raw_cmd()` (`usethis._tool.impl.spec.pyproject_fmt`)
- `dev_deps()` (`usethis._tool.impl.spec.pyproject_fmt`)
- `pre_commit_config()` (`usethis._tool.impl.spec.pyproject_fmt`)
- `config_spec()` (`usethis._tool.impl.spec.pyproject_fmt`)
- `meta()` (`usethis._tool.impl.spec.pyproject_toml`)
- `meta()` (`usethis._tool.impl.spec.pytest`)
- `raw_cmd()` (`usethis._tool.impl.spec.pytest`)
- `preferred_file_manager()` (`usethis._tool.impl.spec.pytest`)
- `config_spec()` (`usethis._tool.impl.spec.pytest`)
- `meta()` (`usethis._tool.impl.spec.requirements_txt`)
- `pre_commit_config()` (`usethis._tool.impl.spec.requirements_txt`)
- `config_spec()` (`usethis._tool.impl.spec.requirements_txt`)
- `__init__()` (`usethis._tool.impl.spec.ruff`) — Initialize the Ruff management class.
- `meta()` (`usethis._tool.impl.spec.ruff`)
- `dev_deps()` (`usethis._tool.impl.spec.ruff`)
- `preferred_file_manager()` (`usethis._tool.impl.spec.ruff`)
- `config_spec()` (`usethis._tool.impl.spec.ruff`)
- `meta()` (`usethis._tool.impl.spec.ty`)
- `preferred_file_manager()` (`usethis._tool.impl.spec.ty`)
- `raw_cmd()` (`usethis._tool.impl.spec.ty`)
- `dev_deps()` (`usethis._tool.impl.spec.ty`)
- `pre_commit_config()` (`usethis._tool.impl.spec.ty`)
- `config_spec()` (`usethis._tool.impl.spec.ty`)
- `_get_src_include()` (`usethis._tool.impl.spec.ty`)
- `from_single_repo()` (`usethis._tool.pre_commit`)
- `from_system_hook()` (`usethis._tool.pre_commit`) — Create a PreCommitConfig for a local system hook.
- `any_require_venv()` (`usethis._tool.pre_commit`)
- `is_rule_covered_by()` (`usethis._tool.rule`) — Check if a rule is covered (subsumed) by a more general rule.
- `reconcile_rules()` (`usethis._tool.rule`) — Determine which rules to add and which existing rules to remove.
- `is_noop()` (`usethis._tool.rule`) — Whether the reconciliation results in no changes.
- `get_all_selected()` (`usethis._tool.rule`) — Get all (project-scope) selected rules.
- `get_all_ignored()` (`usethis._tool.rule`) — Get all (project-scope) ignored rules.
- `subset_related_to_tests()` (`usethis._tool.rule`) — Get a RuleConfig with only rules relating to tests configuration.
- `empty()` (`usethis._tool.rule`) — Check if the rule config is empty.
- `is_related_to_tests()` (`usethis._tool.rule`) — Check if the rule config has any tests-related rules.
- `__repr__()` (`usethis._tool.rule`) — Representation which omits empty-list fields.
- `__or__()` (`usethis._tool.rule`) — Merge multiple rule configs together.
- `meta()` (`usethis._tool.spec`)
- `name()` (`usethis._tool.spec`) — The name of the tool, for display purposes.
- `managed_files()` (`usethis._tool.spec`) — Get (relative) paths to files managed by (solely) this tool.
- `rule_config()` (`usethis._tool.spec`) — Get the linter rule configuration associated with this tool.
- `preferred_file_manager()` (`usethis._tool.spec`) — If there is no currently active config file, this is the preferred one.
- `config_spec()` (`usethis._tool.spec`) — Get the configuration specification for this tool.
- `get_active_config_file_managers()` (`usethis._tool.spec`) — Get file managers for all active configuration files.
- `_get_active_config_file_managers_from_resolution()` (`usethis._tool.spec`)
- `raw_cmd()` (`usethis._tool.spec`) — The default command to run the tool.
- `dev_deps()` (`usethis._tool.spec`) — The tool's development dependencies.
- `test_deps()` (`usethis._tool.spec`) — The tool's test dependencies.
- `doc_deps()` (`usethis._tool.spec`) — The tool's documentation dependencies.
- `pre_commit_config()` (`usethis._tool.spec`) — Get the pre-commit configurations for the tool.
- `selected_rules()` (`usethis._tool.spec`) — Get the rules managed by the tool that are currently selected.
- `ignored_rules()` (`usethis._tool.spec`) — Get the ignored rules managed by the tool.
- `is_declared_as_dep()` (`usethis._tool.spec`) — Whether the tool is declared as a dependency in the project.
- `get_pre_commit_repos()` (`usethis._tool.spec`) — Get the pre-commit repository definitions for the tool.
- `is_pre_commit_config_present()` (`usethis._tool.spec`) — Whether the tool's pre-commit configuration is present.
- `use_arch_tools()` (`usethis._toolset.arch`)
- `use_doc_frameworks()` (`usethis._toolset.doc`)
- `use_formatters()` (`usethis._toolset.format_`)
- `use_hook_framework()` (`usethis._toolset.hook`)
- `use_linters()` (`usethis._toolset.lint`)
- `use_spellcheckers()` (`usethis._toolset.spellcheck`)
- `use_test_frameworks()` (`usethis._toolset.test`)
- `use_typecheckers()` (`usethis._toolset.typecheck`)
- `__str__()` (`usethis._types.deps`)
- `__hash__()` (`usethis._types.deps`)
- `to_requirement_string()` (`usethis._types.deps`) — Convert the dependency to a requirements string.
- `arch()` (`usethis._ui.interface.arch`) — Add recommended architecture analysis tools to the project.
- `author()` (`usethis._ui.interface.author`)
- `pypi()` (`usethis._ui.interface.badge`)
- `ruff()` (`usethis._ui.interface.badge`)
- `ty()` (`usethis._ui.interface.badge`)
- `pre_commit()` (`usethis._ui.interface.badge`)
- `socket()` (`usethis._ui.interface.badge`)
- `usethis()` (`usethis._ui.interface.badge`)
- `bitbucket()` (`usethis._ui.interface.badge`)
- `uv()` (`usethis._ui.interface.badge`)
- `_badge_effect()` (`usethis._ui.interface.badge`)
- `pypi()` (`usethis._ui.interface.browse`)
- `doc()` (`usethis._ui.interface.doc`) — Add a recommended documentation framework to the project.
- `docstyle()` (`usethis._ui.interface.docstyle`)
- `format_()` (`usethis._ui.interface.format_`) — Add recommended formatters to the project.
- `hook()` (`usethis._ui.interface.hook`) — Add a recommended git hook framework to the project.
- `init()` (`usethis._ui.interface.init`) — Initialize a new project with recommended tooling.
- `_init()` (`usethis._ui.interface.init`)
- `lint()` (`usethis._ui.interface.lint`) — Add recommended linters to the project.
- `list()` (`usethis._ui.interface.list`)
- `readme()` (`usethis._ui.interface.readme`)
- `rule()` (`usethis._ui.interface.rule`)
- `backend()` (`usethis._ui.interface.show`)
- `name()` (`usethis._ui.interface.show`)
- `sonarqube()` (`usethis._ui.interface.show`)
- `spellcheck()` (`usethis._ui.interface.spellcheck`) — Add a recommended spellchecker to the project.
- `status()` (`usethis._ui.interface.status`)
- `test()` (`usethis._ui.interface.test`) — Add a recommended testing framework to the project.
- `codespell()` (`usethis._ui.interface.tool`)
- `coverage_py()` (`usethis._ui.interface.tool`)
- `deptry()` (`usethis._ui.interface.tool`)
- `import_linter()` (`usethis._ui.interface.tool`)
- `mkdocs()` (`usethis._ui.interface.tool`)
- `pre_commit()` (`usethis._ui.interface.tool`)
- `pyproject_fmt()` (`usethis._ui.interface.tool`)
- `pyproject_toml()` (`usethis._ui.interface.tool`)
- `pytest()` (`usethis._ui.interface.tool`)
- `requirements_txt()` (`usethis._ui.interface.tool`)
- `ruff()` (`usethis._ui.interface.tool`)
- `ty()` (`usethis._ui.interface.tool`)
- `_run_tool()` (`usethis._ui.interface.tool`)
- `typecheck()` (`usethis._ui.interface.typecheck`) — Add a recommended type checker to the project.
- `version()` (`usethis._ui.interface.version`)
- `name()` (`usethis.errors`) — The name of the file that has a configuration error.
- `name()` (`usethis.errors`) — The name of the file that could not be decoded.

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
