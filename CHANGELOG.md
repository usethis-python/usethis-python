# Changelog

## 0.16.0

### 🚀 New Features

- Most commands now accept a `--backend` option to specify the package manager backend to use. Up to this point, `uv` was the only supported backend. Now, a `--backend=none` option is available to use usethis without `uv`. This is a step toward supporting other backends such as Poetry in the future. When unspecified, heuristics will be used to determine the backend.

- The use of `pyproject.toml` in a project is no longer assumed or imposed on a project when not using the `uv` backend.

- `pre-commit` configurations are now more conventional, preferring URL-based repo configuration instead of local repos with `language: system`. The previous behaviour was designed to ensure synchronization of versions between the `uv` lockfile and the `pre-commit` configuration, but this is now provided by the `sync-with-uv` pre-commit hook, which is added automatically when using `pre-commit` with `uv`.

- When using `usethis author`, a message with the author's name is now outputted in the console.

### 🦾 Robustness

- Pydantic warnings relating to deprecated access to the `model_fields` attribute on an instance should no longer occur.

- The `tool.deptry.ignore_notebooks` configuration for deptry is set explicitly to the default value of `false` to hint that deptry is being used, and to hint on how to configure it.

### 🐞 Bug Fixes

- Previously, the `usethis ci bitbucket` command would fail to add Import Linter configuration to the CI pipeline when `import-linter` was detected. This has been fixed.

- The `usethis badge pypi` command would generate markdown with invalid syntax due to a stray `<` character. This has been fixed.

### 🧹 Maintenance

- The default version of `pyproject-fmt` when used as a pre-commit has been bumped from v2.6.0 to v2.11.0.

- The latest version of the Bitbucket Pipelines configuration file schema is now supported, specifically inline and custom pipeline step types; the `input_variables` configuration for steps, and the new name `scoped` for the artifacts upload type option `unshared`.

### 📚 Documentation

- Hyperlinks in the README and CONTRIBUTING.md files now point to the stable documentation site (rather than the latest site).

- The [configurator](https://github.com/jamesbraza/configurator) project is now documented as a similar project in the README.

### 📦 Packaging

- Python 3.14 is now formally supported.

- `click` is no longer a direct dependency.

### 🔧 Internal Changes

- The CI configuration has been overhauled. `uv` is used in more conventional ways. A runner has been added for bleeding edge dependency versions. The CI now runs on a cron schedule. `zizmor` has been added for security scanning. Permissions are more tightly scoped and explained. All actions have been bumped to their latest versions.

- The pre-commit hooks have been migrated to use `prek` rather than `pre-commit` for development.

- `pytest-sugar` has been added for a more user-friendly test suite output, and `pytest-emoji` has been removed.

## 0.15.2

### 🦾 Robustness

- Previously, empty `.pre-commit-config.yaml` files would cause errors, (since they are not considered valid by pre-commit). Now usethis will treat them as if they do not exist, and so will write new config to them if applicable, rather than raising a validation error for this case.

### 🐞 Bug Fixes

- When subprocessing `uv`, the `usethis init` command will no longer use the default for `--build-backend`, and instead will always explicitly use `hatch`. This may change in the future if the default supported build backend for `usethis` becomes `uv_build`, which is the new default for `uv` v0.8.0. This change avoids creating broken config which mixes `uv_build` with `hatch` config.

- When adding Import Linter while using Ruff, the `INP` rules are selected, but ignored for the tests directory. However, no message would be displayed in cases where those rules were already selected but not already ignored. Now, a message will be displayed in this case.

### 📚 Documentation

- A documentation site is now available at <https://usethis.readthedocs.io/en/stable/>. The CLI Reference section has been moved there from the README. Other minor wording and clarity improvements have been made.

- The CLI reference now mentions that `usethis tool pre-commit` will install hooks to Git.

### 🔧 Internal Changes

- The `doc` dependency group is no longer a default group. This reduces the dependencies required on CI.

## 0.15.1

### 🐞 Bug Fixes

- Previously, when using Import Linter with Ruff, the `INP` rule would be ignored in the `tests` directory via an incorrect glob pattern of `"*/tests/**"`; this has been fixed to `"tests/**"`.

- A TOML integration problem could cause broken configuration in some cases. This could occur on deeply nested keys, such as the per-file-ignores for Ruff directories in `pyproject.toml` when using Import Linter. This has now been fixed.

### 📚 Documentation

- Some issues with mismatched bullet points in the CLI docs section of the README have been addressed.

- The opening paragraph of the README has been reworded for clarity, and various other minor changes have been made.

### 🔧 Internal Changes

- Changes to the `CI` and the test suite have been made to support `uv` v0.8.0. Newer features of `uv` are now required in the CI configuration, meaning the lowest tested version of `uv` is now v0.6.8. Going forward, it is not recommended to use older versions of `uv` with `usethis`.

## 0.15.0

### 🚀 New Features

- The `usethis tool mkdocs` command has been implemented to manage MkDocs documentation sites. Also, the higher-level `usethis doc` command has been added, which has the same effect.

- The `--doc` option for `usethis init` has been implemented to initialize MkDocs documentation sites by default. The old behaviour can be restored by passing `--no-doc`.

- Coverage.py for measuring test coverage is now included by default when using `usethis test` or `usethis init` with the default `--test` option. This provides out-of-the-box test coverage reporting.

- The `--frozen` option is now supported in the `usethis ci` and `usethis docstyle` commands. Similar to other commands, this will leave the virtual environment and lockfile unchanged.

- The `--offline` option is now supported in the `usethis docstyle` command. This will run the command without network access.

### 🦾 Robustness

- Incorrectly structured TOML files will emit better messages and in some cases will be handled gracefully, specifically in cases where a non-mapping value is encountered where a mapping is expected.

### 📦 Packaging

- Bounds are now placed on the build dependencies for usethis (i.e. `hatch-vcs>=0.5.0,<0.6.0` and `hatchling>=1.27.0,<1.28.0`), which should improve reproducibility of builds in the long run.

### 🔧 Internal Changes

- A `YAMLFileManager` has been implemented to manage YAML files, which is used for the MkDocs configuration file `mkdocs.yml`.

- A new `get_project_deps` method has been added to retrieve core project dependencies from the `pyproject.toml` file, specifically from the `project.dependencies` section. This will be used in a future release to support non-uv based backends, such as Poetry.

## 0.14.2

### 🦾 Robustness

- The heuristics to determine whether a tool is used will now check the `pre-commit` configuration to see whether there is a `pre-commit` hook for the tool.

- When removing an entry of TOML configuration, usethis makes some effort to remove empty tables and sections. This was previously only done to one level of nesting, but it should now occur at multiple levels of nesting.

### 🐞 Bug Fixes

- The Codespell configuration for `pyproject.toml` was giving invalid configuration for the `ignore-words-list` option, which was set to an empty list. Codespell requires this option to be non-empty. It is now set to `["..."]`, which is consistent with the handling for other INI-based configuration files.

- Previously, using the `--how` option for `usethis tool` commands would not properly infer the way a tool was installed. For example, it would assume that a tool is installed as a pre-commit hook, simply because `pre-commit` was used for the project, without checking whether there actually are any hooks. This has been fixed, and more sophisticated heuristics are now used to determine how a tool is installed.

- The message to suggest using `__init__.py` files when using Import Linter now checks explicitly whether you have the `INP` rules enabled in Ruff, rather than simply assuming that these rules would be enabled when Ruff is used. The message is only displayed if these `INP` rules are not enabled.

- Error messages now use more consistent punctuation and formatting.

### 🧹 Maintenance

- The default version of `pyproject-fmt` when used as a pre-commit has been bumped from v2.5.0 to v2.6.0.

- The latest version of the Bitbucket Pipelines configuration file schema is now supported, specifically support for new options available regarding concurrency groups.

### 📚 Documentation

- The FAQ is now included in the MkDocs build, and information about roundtripping is now included in the FAQ.

- Social Icon buttons for GitHub and PyPI have been added to the bottom of the MkDocs site.

### 🔧 Internal Changes

- Minor improvements to the CI configuration have been made; the CI will no longer trigger for changes to the MkDocs configuration files.

- There is now global state to turn off pre-commit detection for pre-commit integrations, which is a step toward providing an interface to forbid adding a tool as a pre-commit.

- In the previous release, the project moved to using the codspeed Walltime runner for CI benchmarks. This has been reverted back to using the GitHub-based codspeed runners, since the Walltime runner reports were not as detailed and there were usage limits.

## 0.14.1

### 🐞 Bug Fixes

- The `usethis show sonarqube` command, which is currently undocumented and should be considered experimental, did not properly print to the console. This has been fixed.

### 📚 Documentation

- The `simple-modern-uv` template is now mentioned in the README. See <https://github.com/jlevy/simple-modern-uv>.

### 🔧 Internal Changes

- The `urllib3` package version for development was bumped from 2.3.0 to 2.5.0 to address CVE-2025-50181 and CVE-2025-50182.

- `pydantic` is no longer imported for initializing the Typer application, which should provide a small performance improvement in some situations, like when using the `--help` flag.

- Pyright for development now uses the `nodejs` extra, which is recommended in the Pyright docs.

## 0.14.0

### 🚀 New Features

- A new `usethis status` command is provided to set the Development Status classifiers for the project.

- The uv link mode is now set to `symlink` by default, which can avoid issues for Windows developers relating to access permissions. [See here](https://github.com/astral-sh/uv/issues/11134#issuecomment-2940507840) for more information.

- The `usethis tool ruff` command now accepts `--no-formatter` and `--no-linter` flags to opt-out of adding the formatter or linter, respectively. Previously, this behaviour was implicit in the use of the use or non-use of the `--formatter` and `--linter` flags, but now it is explicit.

- Google-style docstrings are now the default in `usethis docstyle`. It remains opt-in to `usethis init`.

- `usethis readme`, `usethis init` and `usethis badge` now treat empty `README.md` files as suitable for populating with sensible default content, similar to as if the file did not exist.

- When using Import Linter, a message explaining that `__init__.py` files are required is now printed to the console if the user attempts to use Import Linter without Ruff. The message isn't necessary when using Ruff, since the INP rules are selected to enforce the presence of `__init__.py` files.

- Codespell configuration now includes the `ignore-words-list` option (set to empty) by default for whitelisted words. This should make it easier to get started with Codespell, since there are often a few false positives in a codebase.

### 🦾 Robustness

- File validation errors (e.g. an invalid `.pre-commit-config.yaml` file) will no longer dump the full stack trace to the console. Instead, a more concise, user-friendly error message is displayed.

### 🐞 Bug Fixes

- Previously, the INP Ruff rules were enabled when using Import Linter, but this is incorrect behaviour for the `tests` directory, since `pytest` does not require `__init__.py` files in the `tests` directory, and Import Linter does not need to analyze it. The INP rules are now ignored for the `tests` directory when being added for Import Linter.

- The `uv export` command was configured to use `--no-dev`, whereas it should exclude all dependency groups using the `--no-default-groups` option, which is the new behaviour.

- The `usethis readme` command would create a `pyproject.toml` file, if it did not already exist. This is not necessary and this behaviour has been removed.

- The `usethis tool pre-commit` command would not adapt its message explaining how to manually install pre-commit hooks based on whether the user was using uv or not. This has been fixed.

### 🔧 Internal Changes

- usethis has been moved from the `nathanjmcdougall` GitHub user to the `usethis-python` organization.

- The codspeed Walltime runner is now used for CI benchmarks.

- Configuration is now available internally to turn off the possibility of subprocessing uv. This is work towards support for non-uv based workflows, e.g. for users who use Poetry.

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

### 🐞 Bug Fixes

- The `--quiet` option did not properly suppress output when displaying warnings associated with failed README parsing in `usethis badge`. This has been fixed.

- Due to a breaking change in Click v8.2.0, Click is now declared as a direct dependency temporarily until the ramifications can be addressed in Typer. The lower bound is declared as `>=8.0.0` and the constraint `!=8.2.0` to avoid the breaking change. For more information, see [here](https://github.com/fastapi/typer/discussions/1215).

### 🧹 Maintenance

- The latest version of the Bitbucket Pipelines configuration file schema is now supported, specifically support for new options available regarding artifact uploads.

### 📚 Documentation

- There have been various improvements to the documentation, especially the contribution guide.

### 🔧 Internal Changes

- Minor improvements to the CI configuration have been made; the CI will no longer trigger for changes to markdown files only, and `--break-system-packages` is no longer used.

## 0.10.0

This is the first Alpha release of usethis. Releases up to this point do not have
a changelog recorded against them.
