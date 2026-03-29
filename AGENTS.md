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

- `get_backend()` (`_backend.dispatch`) — Get the current package manager backend.
- `is_poetry_used()` (`_backend.poetry.detect`) — Check if Poetry is being used in the project.
- `is_uv_available()` (`_backend.uv.available`) — Check if the `uv` command is available in the current environment.
- `call_uv_subprocess()` (`_backend.uv.call`) — Run a subprocess using the uv command-line tool.
- `add_default_groups_via_uv()` (`_backend.uv.call`) — Add default groups using the uv command-line tool.
- `add_dep_to_group_via_uv()` (`_backend.uv.deps`) — Add a dependency to the named group using uv.
- `remove_dep_from_group_via_uv()` (`_backend.uv.deps`) — Remove a dependency from the named group using uv.
- `get_default_groups_via_uv()` (`_backend.uv.deps`) — Get the default dependency groups from the uv configuration.
- `is_uv_used()` (`_backend.uv.detect`) — Check if uv is being used in the project.
- `opinionated_uv_init()` (`_backend.uv.init`) — Subprocess `uv init` with opinionated arguments.
- `ensure_pyproject_toml_via_uv()` (`_backend.uv.init`) — Create a pyproject.toml file using `uv init --bare`.
- `ensure_symlink_mode()` (`_backend.uv.link_mode`) — Ensure that the symlink link mode is enabled.
- `ensure_uv_lock()` (`_backend.uv.lockfile`) — Ensure a uv.lock file exists, creating it if necessary.
- `get_available_uv_python_versions()` (`_backend.uv.python`) — Get the set of Python versions available via uv.
- `get_supported_uv_minor_python_versions()` (`_backend.uv.python`) — Get the minor Python versions supported by the project and available via uv.
- `uv_python_pin()` (`_backend.uv.python`) — Pin the Python version for the project using uv.
- `get_uv_version()` (`_backend.uv.version`) — Get the version string of the installed uv tool.
- `next_breaking_uv_version()` (`_backend.uv.version`) — Get the next breaking version for a uv version string, following semver.
- `files_manager()` (`_config_file`) — Context manager that opens all configuration file managers for coordinated I/O.
- `plain_print()` (`_console`) — Print a plain message to the console, respecting quiet and alert-only settings.
- `table_print()` (`_console`) — Print a Rich table to the console, respecting quiet and alert-only settings.
- `tick_print()` (`_console`) — Print a ✔ success/completion message (green).
- `instruct_print()` (`_console`) — Print a ☐ instruction the user must perform manually (red).
- `how_print()` (`_console`) — Print a ☐ guidance message explaining how to do something (red).
- `info_print()` (`_console`) — Print an informational message (blue).
- `err_print()` (`_console`) — Print a ✗ error message to stderr (red).
- `warn_print()` (`_console`) — Print a ⚠ warning message (yellow; deduplicated).
- `get_icon_mode()` (`_console`) — Detect terminal's icon support level.
- `add_author()` (`_core.author`) — Add an author entry to the project metadata in pyproject.toml.
- `get_pre_commit_badge()` (`_core.badge`) — Return the pre-commit badge.
- `get_pypi_badge()` (`_core.badge`) — Return the PyPI version badge for the project.
- `get_ruff_badge()` (`_core.badge`) — Return the Ruff badge.
- `get_socket_badge()` (`_core.badge`) — Return the Socket supply chain security badge for the project.
- `get_ty_badge()` (`_core.badge`) — Return the ty type checker badge.
- `get_uv_badge()` (`_core.badge`) — Return the uv package manager badge.
- `get_bitbucket_badge()` (`_core.badge`) — Return the Bitbucket badge.
- `get_usethis_badge()` (`_core.badge`) — Return the usethis badge.
- `get_badge_order()` (`_core.badge`) — Return the canonical ordered list of all supported badges.
- `add_badge()` (`_core.badge`) — Add a badge to the README.md file in the correct position.
- `is_blank()` (`_core.badge`) — Return True if the line is empty or contains only whitespace.
- `is_header()` (`_core.badge`) — Return True if the line is a Markdown header.
- `is_badge()` (`_core.badge`) — Return True if the line looks like a Markdown badge.
- `remove_badge()` (`_core.badge`) — Remove a badge from the README.md file.
- `browse_pypi()` (`_core.browse`) — Open or display the PyPI project page URL for a package.
- `use_docstyle()` (`_core.docstyle`) — Configure the docstring style convention for the project using Ruff.
- `show_usage_table()` (`_core.list`) — Show the usage table.
- `get_usage_table()` (`_core.list`) — Get the usage table.
- `add_readme()` (`_core.readme`) — Add a README.md file to the project.
- `select_rules()` (`_core.rule`) — Select the given linter rules, enabling the appropriate tools as needed.
- `deselect_rules()` (`_core.rule`) — Deselect the given linter rules from the relevant tools.
- `ignore_rules()` (`_core.rule`) — Add the given linter rules to the ignore list of the relevant tools.
- `unignore_rules()` (`_core.rule`) — Remove the given linter rules from the ignore list of the relevant tools.
- `get_rules_mapping()` (`_core.rule`) — Partition a list of rule codes into deptry and Ruff rule groups.
- `show_backend()` (`_core.show`) — Display the inferred package manager backend for the current project.
- `show_name()` (`_core.show`) — Display the name of the current project.
- `show_sonarqube_config()` (`_core.show`) — Display the sonar-project.properties configuration for the current project.
- `use_development_status()` (`_core.status`) — Set the development status classifier in pyproject.toml.
- `use_codespell()` (`_core.tool`) — Add and configure the codespell spellchecker tool.
- `use_coverage_py()` (`_core.tool`) — Add and configure the Coverage.py code coverage tool.
- `use_deptry()` (`_core.tool`) — Add and configure the deptry dependency linter tool.
- `use_import_linter()` (`_core.tool`) — Add and configure the Import Linter architecture enforcement tool.
- `use_mkdocs()` (`_core.tool`) — Add and configure the MkDocs documentation site generator tool.
- `use_pre_commit()` (`_core.tool`) — Add and configure the pre-commit hook framework.
- `use_pyproject_fmt()` (`_core.tool`) — Add and configure the pyproject-fmt pyproject.toml formatter tool.
- `use_pyproject_toml()` (`_core.tool`) — Add and configure the pyproject.toml file as a project configuration tool.
- `use_pytest()` (`_core.tool`) — Add and configure the pytest testing framework.
- `use_requirements_txt()` (`_core.tool`) — Add and configure a requirements.txt file exported from the uv lockfile.
- `use_ruff()` (`_core.tool`) — Add Ruff to the project.
- `use_ty()` (`_core.tool`) — Add and configure the ty type checker tool.
- `use_tool()` (`_core.tool`) — General dispatch function to add or remove a tool to/from the project.
- `get_project_deps()` (`_deps`) — Get all project dependencies.
- `get_dep_groups()` (`_deps`) — Get all dependency groups from the dependency-groups section of pyproject.toml.
- `get_deps_from_group()` (`_deps`) — Get the list of dependencies in a named dependency group.
- `register_default_group()` (`_deps`) — Register a group in the default-groups configuration if it's not already there.
- `add_default_groups()` (`_deps`) — Register the given dependency groups as default groups in the package manager configuration.
- `get_default_groups()` (`_deps`) — Get the list of default dependency groups installed automatically by the package manager.
- `ensure_dev_group_is_defined()` (`_deps`) — Ensure the 'dev' dependency group exists in pyproject.toml.
- `is_dep_satisfied_in()` (`_deps`) — Check if a dependency is satisfied by any dependency in the given list.
- `remove_deps_from_group()` (`_deps`) — Remove dependencies from the named group if present.
- `is_dep_in_any_group()` (`_deps`) — Check if a dependency exists in any dependency group.
- `add_deps_to_group()` (`_deps`) — Add dependencies to a named group using PEP 735 dependency groups.
- `is_pre_commit_used()` (`_detect.pre_commit`) — Check if pre-commit is being used in the project.
- `is_readme_used()` (`_detect.readme`) — Check if the README.md file is used.
- `next_breaking_version()` (`_fallback`) — Get the next breaking version for a version string, following semver.
- `get_project_name_from_dir()` (`_file.dir`) — Derive a valid project name from the current directory name.
- `deep_merge()` (`_file.merge`) — Recursively merge source into target in place, returning target.
- `print_keys()` (`_file.print_`) — Convert a list of keys to a string.
- `get_name()` (`_file.pyproject_toml.name`) — Get the project name from pyproject.toml.
- `get_description()` (`_file.pyproject_toml.name`) — Get the project description from pyproject.toml.
- `get_project_dict()` (`_file.pyproject_toml.project`) — Get the contents of the [project] section from pyproject.toml.
- `remove_pyproject_toml()` (`_file.pyproject_toml.remove`) — Remove the pyproject.toml file from the project.
- `get_requires_python()` (`_file.pyproject_toml.requires_python`) — Get the requires-python constraint from pyproject.toml.
- `get_required_minor_python_versions()` (`_file.pyproject_toml.requires_python`) — Get Python minor versions that match the project's requires-python constraint.
- `ensure_pyproject_validity()` (`_file.pyproject_toml.valid`) — Ensure pyproject.toml has a valid structure, adding missing required fields.
- `edit_yaml()` (`_file.yaml.io_`) — A context manager to modify a YAML file in-place, with managed read and write.
- `read_yaml()` (`_file.yaml.io_`) — A context manager to read a YAML file.
- `update_ruamel_yaml_map()` (`_file.yaml.update`) — Update the values of a ruamel.yaml map in-place using a diff-like algorithm.
- `lcs_list_update()` (`_file.yaml.update`) — Update in-place using a longest common subsequence solver.
- `project_init()` (`_init`) — Initialize the project by creating the pyproject.toml and project structure.
- `write_simple_requirements_txt()` (`_init`) — Write a simple requirements.txt file with -e . and any project dependencies.
- `ensure_dep_declaration_file()` (`_init`) — Ensure that the file where dependencies are declared exists, if necessary.
- `ensure_pyproject_toml()` (`_init`) — Ensure that a pyproject.toml file exists, creating it if necessary.
- `get_github_latest_tag()` (`_integrations.ci.github.tags`) — Get the name of the most recent tag on the default branch of a GitHub repository.
- `get_supported_minor_python_versions()` (`_integrations.environ.python`) — Get supported Python versions for the current backend.
- `add_docs_dir()` (`_integrations.mkdocs.core`) — Create the `docs` directory and an `docs/index.md` file if they do not exist.
- `remove_pre_commit_config()` (`_integrations.pre_commit.core`) — Remove the .pre-commit-config.yaml file from the project.
- `install_pre_commit_hooks()` (`_integrations.pre_commit.core`) — Install pre-commit hooks.
- `uninstall_pre_commit_hooks()` (`_integrations.pre_commit.core`) — Uninstall pre-commit hooks.
- `add_repo()` (`_integrations.pre_commit.hooks`) — Add a pre-commit repo configuration to the pre-commit configuration file.
- `insert_repo()` (`_integrations.pre_commit.hooks`) — Insert a repo into the list of repos after the named predecessor hook.
- `add_placeholder_hook()` (`_integrations.pre_commit.hooks`) — Add a placeholder hook to the pre-commit configuration with instructions for the user.
- `remove_hook()` (`_integrations.pre_commit.hooks`) — Remove pre-commit hook configuration.
- `get_hook_ids()` (`_integrations.pre_commit.hooks`) — Get the list of hook IDs currently configured in the pre-commit configuration file.
- `extract_hook_ids()` (`_integrations.pre_commit.hooks`) — Extract all hook IDs from a pre-commit configuration model.
- `hooks_are_equivalent()` (`_integrations.pre_commit.hooks`) — Check if two hooks are equivalent.
- `hook_ids_are_equivalent()` (`_integrations.pre_commit.hooks`) — Check if two hook IDs are equivalent.
- `ensure_pre_commit_config_exists()` (`_integrations.pre_commit.init`) — Ensure '.pre-commit-config.yaml' exists with minimal valid content.
- `get_system_language()` (`_integrations.pre_commit.language`) — Get the appropriate 'system' language keyword based on pre-commit version.
- `get_pre_commit_version()` (`_integrations.pre_commit.version`) — Get an inferred pre-commit version for usethis to target.
- `get_minimum_pre_commit_version()` (`_integrations.pre_commit.version`) — Get the declared minimum supported pre-commit version from the configuration.
- `has_pyproject_toml_declared_build_system()` (`_integrations.project.build`) — Check if a build system is declared in the project.
- `get_layered_architectures()` (`_integrations.project.imports`) — Get the suggested layers for a package.
- `augment_pythonpath()` (`_integrations.project.imports`) — Temporarily add a directory to the Python path.
- `get_source_dir_str()` (`_integrations.project.layout`) — Get the source directory as a string ('src' or '.').
- `get_project_name()` (`_integrations.project.name`) — The project name, from pyproject.toml if available or fallback to heuristics.
- `get_importable_packages()` (`_integrations.project.packages`) — Get the names of packages in the source directory that can be imported.
- `fancy_model_dump()` (`_integrations.pydantic.dump`) — Like `pydantic.model_dump` but with bespoke formatting options.
- `add_pytest_dir()` (`_integrations.pytest.core`) — Create the tests directory and conftest.py if they do not already exist.
- `remove_pytest_dir()` (`_integrations.pytest.core`) — Remove the tests directory if it contains only the managed conftest.py.
- `get_readme_path()` (`_integrations.readme.path`) — Return the path to the README file, searching for common README filenames.
- `get_markdown_readme_path()` (`_integrations.readme.path`) — Return the path to the Markdown README file, raising an error if it is not Markdown.
- `get_sonar_project_properties()` (`_integrations.sonarqube.config`) — Get contents for (or from) the sonar-project.properties file.
- `parallel()` (`_pipeweld.containers`) — Create a Parallel pipeline composition from the given components.
- `series()` (`_pipeweld.containers`) — Create a Series pipeline composition from the given components.
- `depgroup()` (`_pipeweld.containers`) — Create a DepGroup pipeline composition tied to a named configuration group.
- `get_endpoint()` (`_pipeweld.func`) — Get the last step name (endpoint) from a pipeline component.
- `call_subprocess()` (`_subprocess`) — Run a subprocess and return its stdout, raising SubprocessFailedError on failure.
- `change_cwd()` (`_test`) — Change the working directory temporarily.
- `is_offline()` (`_test`) — Return True if the current environment has no internet connectivity.
- `ensure_managed_file_exists()` (`_tool.config`) — Ensure a file manager's managed file exists.
- `is_likely_used()` (`_tool.heuristics`) — Determine whether a tool is likely used in the current project.
- `is_rule_covered_by()` (`_tool.rule`) — Check if a rule is covered (subsumed) by a more general rule.
- `reconcile_rules()` (`_tool.rule`) — Determine which rules to add and which existing rules to remove.
- `use_arch_tools()` (`_toolset.arch`) — Add and configure architecture enforcement tools for the project.
- `use_doc_frameworks()` (`_toolset.doc`) — Add and configure documentation framework tools for the project.
- `use_formatters()` (`_toolset.format_`) — Add and configure code formatting tools for the project.
- `use_hook_framework()` (`_toolset.hook`) — Add and configure git hook framework tools for the project.
- `use_linters()` (`_toolset.lint`) — Add and configure linting tools for the project.
- `use_spellcheckers()` (`_toolset.spellcheck`) — Add and configure spellchecking tools for the project.
- `use_test_frameworks()` (`_toolset.test`) — Add and configure testing framework tools for the project.
- `use_typecheckers()` (`_toolset.typecheck`) — Add and configure type checking tools for the project.
- `arch()` (`_ui.interface.arch`) — Add recommended architecture analysis tools to the project.
- `author()` (`_ui.interface.author`) — Add an author to the project metadata in pyproject.toml.
- `pypi()` (`_ui.interface.badge`) — Add a badge with the version of your package on PyPI.
- `ruff()` (`_ui.interface.badge`) — Add a badge for the Ruff linter.
- `ty()` (`_ui.interface.badge`) — Add a badge for the ty type checker.
- `pre_commit()` (`_ui.interface.badge`) — Add a badge for the pre-commit framework.
- `socket()` (`_ui.interface.badge`) — Add a badge with your PyPI package's supply chain security rating from Socket.
- `usethis()` (`_ui.interface.badge`) — Add a badge for usethis.
- `bitbucket()` (`_ui.interface.badge`) — Add a badge for Bitbucket.
- `uv()` (`_ui.interface.badge`) — Add a badge for the uv package manager.
- `pypi()` (`_ui.interface.browse`) — Visit the PyPI project page for a package.
- `doc()` (`_ui.interface.doc`) — Add a recommended documentation framework to the project.
- `docstyle()` (`_ui.interface.docstyle`) — Configure the docstring style for the project.
- `format_()` (`_ui.interface.format_`) — Add recommended formatters to the project.
- `hook()` (`_ui.interface.hook`) — Add a recommended git hook framework to the project.
- `init()` (`_ui.interface.init`) — Initialize a new project with recommended tooling.
- `lint()` (`_ui.interface.lint`) — Add recommended linters to the project.
- `list()` (`_ui.interface.list`) — Show the usage table of all available tools and their current status.
- `readme()` (`_ui.interface.readme`) — Create or update the README.md file, optionally adding badges.
- `rule()` (`_ui.interface.rule`) — Select, deselect, ignore, or unignore linter rules.
- `backend()` (`_ui.interface.show`) — Show the inferred project manager backend, e.g. 'uv' or 'none'.
- `name()` (`_ui.interface.show`) — Show the name of the project.
- `sonarqube()` (`_ui.interface.show`) — Show the sonar-project.properties file for SonarQube.
- `spellcheck()` (`_ui.interface.spellcheck`) — Add a recommended spellchecker to the project.
- `status()` (`_ui.interface.status`) — Set the development status classifier for the project.
- `test()` (`_ui.interface.test`) — Add a recommended testing framework to the project.
- `codespell()` (`_ui.interface.tool`) — Use the codespell spellchecker: detect common spelling mistakes.
- `coverage_py()` (`_ui.interface.tool`) — Use Coverage.py: a code coverage measurement tool.
- `deptry()` (`_ui.interface.tool`) — Use the deptry linter: avoid missing or superfluous dependency declarations.
- `import_linter()` (`_ui.interface.tool`) — Use Import Linter: enforce a self-imposed architecture on imports.
- `mkdocs()` (`_ui.interface.tool`) — Use MkDocs: Generate project documentation sites with Markdown.
- `pre_commit()` (`_ui.interface.tool`) — Use the pre-commit framework to manage and maintain pre-commit hooks.
- `pyproject_fmt()` (`_ui.interface.tool`) — Use the pyproject-fmt linter: opinionated formatting of 'pyproject.toml' files.
- `pyproject_toml()` (`_ui.interface.tool`) — Use a pyproject.toml file to configure the project.
- `pytest()` (`_ui.interface.tool`) — Use the pytest testing framework.
- `requirements_txt()` (`_ui.interface.tool`) — Use a requirements.txt file exported from the uv lockfile.
- `ruff()` (`_ui.interface.tool`) — Use Ruff: an extremely fast Python linter and code formatter.
- `ty()` (`_ui.interface.tool`) — Use the ty type checker: an extremely fast Python type checker.
- `typecheck()` (`_ui.interface.typecheck`) — Add a recommended type checker to the project.
- `version()` (`_ui.interface.version`) — Print the installed version of usethis.
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
