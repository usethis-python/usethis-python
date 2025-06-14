# Changelog

## 0.13.0

### 🚀 New Features

- New high-level interfaces have been added: `usethis init` to initialize projects including recommended tools, and `usethis lint`, `usethis format`, `usethis spellcheck`, and `usethis test` to add sets of recommended tools for different purposes. For example, `usethis lint` will add both Ruff and deptry. As recommended tooling changes in the long-term, these commands will remain the same but potentially change the specific tools they include.

- Error messages are now directed to stderr instead of stdout.

- The [`INP`](https://docs.astral.sh/ruff/rules/#flake8-no-pep420-inp) code Ruff rules are now enabled when adding Import Linter, since Import Linter requires `__init__.py` files to exist in the packages it analyzes.

- The `usethis docstyle` possible arguments (`numpy`, `google`, and `pep257`) are now handled in a way that should lead to more readable error messages and `--help` explanations.

### 🦾 Robustness

- If `pre-commit install` does not run successfully (e.g. if there is not Git Repository for the project) then usethis will display a message for the user to ask them to run this command themselves, rather than the previous behaviour which was to stop with an error.

- Syntax errors in TOML and INI configuration files will be handled when trying to determine whether a given tool is being used. A warning is displayed but usethis will continue under the assumption that the invalid file does not contain relevant configuration for the tool.

### 🐞 Bug Fixes

- Previously, when calling `usethis tool ruff --how`, any passed `--linter` or `--formatter` arguments would be ignored and instructions would be displayed for both the linter and the formatter regardless. This is no longer the case - now if either the `--linter` or `--formatter` argument is passed, just the specified arguments will be considered in terms of the messages displayed.

- Previously, when adding pre-commit hook definitions, it was possible to duplicate the added definition if there was a duplicate hook ID existing in the file. This has been fixed. Similarly, when adding pre-commit hooks definitions, the intended order of hooks was violated in some circumstances. The ordering logic has been reworked to ensure consistent hook ordering (based on the hook ID).

- Previously, when adding `pre-commit`, if `pyproject-fmt` or `codespell` were present, the default configuration would be added for those tools too. This is no longer the case - adding `pre-commit` will not touch the existing configuration for other tools except for the way in which they are installed and declared as dependencies.

- Previously, the `usethis rule` command did not handle some error messages properly, and would dump the full stack trace. This has been resolved.

### 📦 Packaging

- The `typer` dependency lower bound has been bumped from version 0.6.0 to 0.12.4 to provide support for union types of Enum with `None`.

### 📚 Documentation

- More information has been added to the README in the Command Line Interface Table of Contents, giving a one-line summary of each command.

- The GitHub Issue templates have been simplified down to make them more accessible.

### 🔧 Internal Changes

- The test suite on CI now runs on the lowest supported version of uv (0.5.29), rather than just the latest version.

- The `ARG` Ruff rules are now enabled for development of usethis.

- New `alert_only` global state has been added to allow the suppression of non-warning and non-error printing to the console.

- New global state has been added to set the project directory (versus the previous default of using the current working directory in all cases).

- The `requests` package version for development was bumped from 2.23.3 to 2.23.4 to address CVE-2024-47081.

## 0.12.0

### 🚀 New Features

- The Ruff linter and formatter can now be configured independently. When using the `usethis tool ruff` command, you can now specify whether to add or remove the linter or formatter independently using the `--linter` and `--formatter` options. This allows for more granular control over which components of Ruff are used in your project. By default, as before, both the linter and formatter will be added or removed together.
This introduces a change in the way that Bitbucket Pipeline steps will be configured for Ruff, by having the linter and formatter as separate steps.

- Integrations with Ruff for pre-commit and Bitbucket pipelines will determine whether the linter or formatter is being used based on the presence of the `ruff.lint` and `ruff.format` keys the active Ruff configuration file.

### 🐞 Bug Fixes

- The `usethis tool` command no longer creates a `pyproject.toml` file when using the `--remove` option.

- The Coverage.py tool was previously referred to as simply "coverage" in the codebase and documentation. This has been corrected to Coverage.py, [which is the official name of the tool](https://coverage.readthedocs.io/en/latest/index.html).

- The RegEx used to parse the Python versions outputted by `uv python list` has been tightened to avoid matching invalid versions containing non-alphanumeric leading characters.

### 📦 Packaging

- The `click` package is no longer constrained to `!=8.2.0`, since the latest version of Typer (0.16.0) is compatible with `click` 8.2.0.

### 📚 Documentation

- The README now explains that `usethis tool` commands will create a `pyproject.toml` file if it does not already exist (to be able to declare dependencies).

- A security policy has been added in `SECURITY.md`.

### 🔧 Internal Changes

- A `requirements.txt` file is now included in the repository (generated using the uv lockfile and automatically updated via pre-commit). This allows for Dependabot scanning. Accordingly, the version of `h11` in the lockfile was bumped to address a security issue (CVE-2025-43859).

- CodeQL is now configured for security scanning.

- Previously, all pre-commit hooks ran post-checkout, post-merge, and post-rewrite. Now, only `uv-sync` will run for those stages, the rest will run only on pre-commit. This is to avoid unnecessary overhead when checking out branches or merging, etc.

- Some stricter linting configuration has been added for Ruff.

- Permissions are now set explicitly for the GitHub Actions workflows used for development.

## 0.11.0

### 🚀 New Features

- This release adds a new `--show` option to the `usethis badge` interface. This option will display the badge as markdown output without adding it to the README file.

- The latest version of the Bitbucket Pipelines configuration file schema is now supported, specifically support for new options available regarding artifact uploads.

### 🐞 Bug Fixes

- The `--quiet` option did not properly suppress output when displaying warnings associated with failed README parsing in `usethis badge`. This has been fixed.

- Due to a breaking change in Click v8.2.0, Click is now declared as a direct dependency temporarily until the ramifications can be addressed in Typer. The lower bound is declared as `>=8.0.0` and the constraint `!=8.2.0` to avoid the breaking change. For more information, see [here](https://github.com/fastapi/typer/discussions/1215).

### 📚 Documentation

- There have been various improvements to the documentation, especially the contribution guide.

### 🔧 Internal Changes

- Minor improvements to the CI configuration have been made; the CI will no longer trigger for changes to markdown files only, and `--break-system-packages` is no longer used.

## 0.10.0

This is the first Alpha release of usethis. Releases up to this point do not have
a changelog recorded against them.
