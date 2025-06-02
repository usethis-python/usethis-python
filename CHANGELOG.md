# Changelog

## 0.12.0

### 🚀 New Features

The Ruff linter and formatter can now be configured independently. When using the `usethis tool ruff` command, you can now specify whether to add or remove the linter or formatter independently using the `--linter` and `--formatter` options. This allows for more granular control over which components of Ruff are used in your project. By default, as before, both the linter and formatter will be added or removed together.
This introduces a change in the way that Bitbucket Pipeline steps will be configured for Ruff, by having the linter and formatter as separate steps.

Integrations with Ruff for pre-commit and Bitbucket pipelines will determine whether the linter or formatter is being used based on the presence of the `ruff.lint` and `ruff.format` keys the active Ruff configuration file.

### 🐞 Bug Fixes

The `usethis tool` command no longer creates a `pyproject.toml` file when using the `--remove` option.

The Coverage.py tool was previously referred to as simply "coverage" in the codebase and documentation. This has been corrected to Coverage.py, [which is the official name of the tool](https://coverage.readthedocs.io/en/latest/index.html).

The RegEx used to parse the Python versions outputted by `uv python list` has been tightened to avoid matching invalid versions containing non-alphanumeric leading characters.

### 📦 Packaging

The `click` package is no longer constrained to `!=8.2.0`, since the latest version of Typer (0.16.0) is compatible with `click` 8.2.0.

### 📚 Documentation

The README now explains that `usethis tool` commands will create a `pyproject.toml` file if it does not already exist (to be able to declare dependencies).

A security policy has been added in `SECURITY.md`.

### 🔧 Internal Changes

A `requirements.txt` file is now included in the repository (generated using the uv lockfile and automatically updated via pre-commit). This allows for Dependabot scanning. Accordingly, the version of `h11` in the lockfile was bumped to address a security issue (CVE-2025-43859).

CodeQL is now configured for security scanning.

Previously, all pre-commit hooks ran post-checkout, post-merge, and post-rewrite. Now, only `uv-sync` will run for those stages, the rest will run only on pre-commit. This is to avoid unnecessary overhead when checking out branches or merging, etc.

Some stricter linting configuration has been added for Ruff.

Permissions are now set explicitly for the GitHub Actions workflows used for development.

## 0.11.0

### 🚀 New Features

- This release adds a new `--show` option to the `usethis badge` interface. This option will display the badge as markdown output without adding it to the README file.

- The latest version of the Bitbucket Pipelines configuration file schema is now supported, specifically support for new options available regarding artifact uploads.

### 🐞 Bug Fixes

- The `--quiet` option did not properly suppress output when displaying warnings associated with failed README parsing in `usethis badge`. This has been fixed.

- Due to a breaking change in Click v8.2.0, Click is now declared as a direct dependency temporarily until the ramifications can be addressed in Typer. The lower bound is declared as `>=8.0.0` and the constraint `!=8.2.0` to avoid the breaking change. For more information, see [here](https://github.com/fastapi/typer/discussions/1215).

### 📚 Documentation

There have been various improvements to the documentation, especially the contribution guide.

### 🔧 Internal Changes

Minor improvements to the CI configuration have been made; the CI will no longer trigger for changes to markdown files only, and `--break-system-packages` is no longer used.

## 0.10.0

This is the first Alpha release of usethis. Releases up to this point do not have
a changelog recorded against them.
