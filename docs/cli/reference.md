# 🖥️ Command Reference

## `usethis init`

Initialize a new Python project with recommended defaults, including:

- a `pyproject.toml` file and relevant configuration,
- recommended linters, formatters, spellcheckers, and test frameworks (all opt-out),
- docstring style enforcement (opt-in),
- the pre-commit framework (opt-in),
- CI services (opt-in),
- declared & installed dependencies via `uv add`, and
- any other relevant directories or tool-bespoke configuration files.

Supported options:

- `--doc` to add recommended documentation tools (default; or `--no-doc` to opt-out)
- `--format` to add recommended formatters (default; or `--no-format` to opt-out)
- `--lint` to add recommended linters (default; or `--no-lint` to opt-out)
- `--spellcheck` to add a recommended spellchecker (default; or `--no-spellcheck` to opt-out)
- `--test` to add a recommended testing framework (default; or `--no-test` to opt-out)
- `--pre-commit` to add the pre-commit framework for git hooks (but the default is `--no-pre-commit`)
- `--ci` to add a CI service configuration
  Possible values:
  - `bitbucket` for [Bitbucket Pipelines](https://bitbucket.org/product/features/pipelines)
- `--docstyle` to set a docstring style convention for the project
  Possible values:
  - `numpy` for [NumPy docstring style](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard)
  - `google` for [Google docstring style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
  - `pep257` for [PEP 257 docstring style](https://www.python.org/dev/peps/pep-0257/)
- `--status` to set the development status of the project. Defaults to `planning`.
  Possible values:
  - `planning` or `1` for "Development Status :: 1 - Planning"
  - `pre-alpha` or `2` for "Development Status :: 2 - Pre-Alpha"
  - `alpha` or `3` for "Development Status :: 3 - Alpha"
  - `beta` or `4` for "Development Status :: 4 - Beta"
  - `production` or `5` for "Development Status :: 5 - Production/Stable"
  - `mature` or `6` for "Development Status :: 6 - Mature"
  - `inactive` or `7` for "Development Status :: 7 - Inactive"
- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output
- `--frozen` to leave the virtual environment and lockfile unchanged (i.e. do not install dependencies, nor update lockfiles)
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

## `usethis doc`

Add recommended documentation tools to the project (namely, [MkDocs](https://www.mkdocs.org/)), including:

- declared & installed dependencies via `uv add`,
- relevant `pyproject.toml` configuration, and
- any other relevant directories or tool-bespoke configuration files.

Note if `pyproject.toml` is not present, it will be created, since this is required for declaring dependencies via `uv add`.

Supported options:

- `--remove` to remove the tool instead of adding it
- `--how` to only print how to use the tool, with no other side effects
- `--offline` to disable network access and rely on caches
- `--frozen` to leave the virtual environment and lockfile unchanged
- `--quiet` to suppress output

See [`usethis tool`](#usethis-tool) for more information.

## `usethis format`

Add recommended formatters to the project (namely, [Ruff](https://docs.astral.sh/ruff/formatter/) and [pyproject-fmt](https://pyproject-fmt.readthedocs.io/en/latest/)), including:

- declared & installed dependencies via `uv add`,
- relevant `pyproject.toml` configuration, and
- any other relevant directories or tool-bespoke configuration files.

Note if `pyproject.toml` is not present, it will be created, since this is required for declaring dependencies via `uv add`.

Supported options:

- `--remove` to remove the tool instead of adding it
- `--how` to only print how to use the tool, with no other side effects
- `--offline` to disable network access and rely on caches
- `--frozen` to leave the virtual environment and lockfile unchanged
- `--quiet` to suppress output
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

See [`usethis tool`](#usethis-tool) for more information.

## `usethis lint`

Add recommended linters to the project (namely, [Ruff](https://docs.astral.sh/ruff/linter) and [deptry](https://github.com/fpgmaas/deptry)), including:

- declared & installed dependencies with `uv add`,
- relevant `pyproject.toml` configuration, and
- any other relevant directories or tool-bespoke configuration files.

Note if `pyproject.toml` is not present, it will be created, since this is required for declaring dependencies with `uv add`.

Supported options:

- `--remove` to remove the tool instead of adding it
- `--how` to only print how to use the tool, with no other side effects
- `--offline` to disable network access and rely on caches
- `--frozen` to leave the virtual environment and lockfile unchanged
- `--quiet` to suppress output
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

See [`usethis tool`](#usethis-tool) for more information.

## `usethis spellcheck`

Add a recommended spellchecker to the project (namely, [codespell](https://github.com/codespell-project/codespell)), including:

- declared & installed dependencies with `uv add`,
- relevant `pyproject.toml` configuration, and
- any other relevant directories or tool-bespoke configuration files.

Note if `pyproject.toml` is not present, it will be created, since this is required for declaring dependencies with `uv add`.

Supported options:

- `--remove` to remove the tool instead of adding it
- `--how` to only print how to use the tool, with no other side effects
- `--offline` to disable network access and rely on caches
- `--frozen` to leave the virtual environment and lockfile unchanged
- `--quiet` to suppress output
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

See [`usethis tool`](#usethis-tool) for more information.

## `usethis test`

Add a recommended testing framework to the project (namely pytest), including:

- declared & installed dependencies with `uv add`,
- relevant `pyproject.toml` configuration, and
- any other relevant directories or tool-bespoke configuration files.

Note if `pyproject.toml` is not present, it will be created, since this is required for declaring dependencies with `uv add`.

Supported options:

- `--remove` to remove the tool instead of adding it
- `--how` to only print how to use the tool, with no other side effects
- `--offline` to disable network access and rely on caches
- `--frozen` to leave the virtual environment and lockfile unchanged
- `--quiet` to suppress output
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

See [`usethis tool`](#usethis-tool) for more information.

## `usethis tool`

Add a new tool to a Python project, including:

- declared & installed dependencies with `uv add`,
- relevant `pyproject.toml` configuration,
- any other relevant directories or tool-bespoke configuration files, and
- `.pre-commit-config.yaml` configuration if using `pre-commit`.

Note if `pyproject.toml` is not present, it will be created, since this is required for
declaring dependencies with `uv add`.

### Code Quality Tools

- `usethis tool codespell` - Use the [codespell spellchecker](https://github.com/codespell-project/codespell): detect common spelling mistakes.
- `usethis tool deptry` - Use the [deptry linter](https://github.com/fpgmaas/deptry): avoid missing or superfluous dependency declarations.
- `usethis tool import-linter` - Use [Import Linter](https://import-linter.readthedocs.io/en/stable/): enforce a self-imposed architecture on imports.
- `usethis tool pre-commit` - Use the [pre-commit](https://github.com/pre-commit/pre-commit) framework to manage and maintain Git hooks. Note that this will also install all the hooks to Git.
- `usethis tool pyproject-fmt` - Use the [pyproject-fmt linter](https://github.com/tox-dev/pyproject-fmt): opinionated formatting of 'pyproject.toml' files.
- `usethis tool ruff` - Use [Ruff](https://github.com/astral-sh/ruff): an extremely fast Python linter and code formatter.

### Testing

- `usethis tool coverage.py` - Use [Coverage.py](https://github.com/nedbat/coveragepy): a code coverage measurement tool.
- `usethis tool pytest` - Use the [pytest](https://github.com/pytest-dev/pytest) testing framework.

### Documentation

- `usethis tool mkdocs` - Use [MkDocs](https://www.mkdocs.org/): Generate project documentation sites with Markdown.

### Configuration Files

- `usethis tool pyproject.toml` - Use a [pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-your-pyproject-toml) file to configure the project.
- `usethis tool requirements.txt` - Use a [requirements.txt](https://pip.pypa.io/en/stable/reference/requirements-file-format/) file exported from the uv lockfile.

Supported options:

- `--remove` to remove the tool instead of adding it
- `--how` to only print how to use the tool, with no other side effects
- `--offline` to disable network access and rely on caches
- `--frozen` to leave the virtual environment and lockfile unchanged
- `--quiet` to suppress output
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

For `usethis tool ruff`, in addition to the above options, you can also specify:

- `--linter` to add or remove specifically the linter component of Ruff (default; or `--no-linter` to opt-out)
- `--formatter` to add or remove specifically the formatter component of Ruff (default; or `--no-formatter` to opt-out)

## `usethis ci`

Add Continuous Integration pipelines to the project.

Currently supported platforms:

- `usethis ci bitbcuket` - Use [Bitbucket Pipelines](https://bitbucket.org/product/features/pipelines): a CI/CD service for Bitbucket.

Supported options:

- `--remove` to remove the CI configuration instead of adding it
- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output
- `--frozen` to leave the virtual environment and lockfile unchanged (i.e. do not install dependencies, nor update lockfiles)
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

## `usethis badge`

Add badges to the README file.

Currently supported badges:

- `usethis badge pre-commit` - [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
- `usethis badge pypi` - [![PyPI Version](https://img.shields.io/pypi/v/usethis.svg)](https://pypi.python.org/pypi/usethis)
- `usethis badge ruff` - [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
- `usethis badge usethis` - [![usethis](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/usethis-python/usethis-python/main/assets/badge/v1.json)](https://github.com/usethis-python/usethis-python)
- `usethis badge uv` - [![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Supported options:

- `--show` to show the badge URL instead of adding (or removing) it
- `--remove` to remove the badge instead of adding it
- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output

## `usethis readme`

Add a README.md file to the project.

Supported options:

- `--badges` to also add badges to the README.md file
- `--quiet` to suppress output
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

## `usethis author`

Set new author information for the project.

Required options:

- `--name` for the new author's name

Other supported options:

- `--email` to set the author email address
- `--overwrite` to overwrite all existing author information
- `--quiet` to suppress output
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

## `usethis docstyle <style>`

Set a docstring style convention for the project, and [enforce it with Ruff](https://docs.astral.sh/ruff/rules/#pydocstyle-d).

Defaults to the Google docstring style.

Possible style options:

- `numpy` for [NumPy docstring style](https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard)
- `google` for [Google docstring style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- `pep257` for [PEP 257 docstring style](https://www.python.org/dev/peps/pep-0257/)

Example:

`usethis docstyle google`

Supported options:

- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output
- `--frozen` to leave the virtual environment and lockfile unchanged (i.e. do not install dependencies, nor update lockfiles)
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

## `usethis rule <rulecode>`

Add (or manage configuration) of Ruff and Deptry rules in `pyproject.toml`.

See [the Ruff documentation](https://docs.astral.sh/ruff/rules/) for a list of available
rules, and [the Deptry documentation](https://deptry.com/rules-violations/) for a list
of available rules.

Example:

`usethis rule RUF001`

Supported options:

- `--remove` to remove the rule selection or ignore status.
- `--ignore` to add the rule to the ignore list (or remove it if --remove is specified).
- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output
- `--backend` to specify a package manager backend to use. The default is to auto-detect.
Possible values:
  - `auto` to auto-detect the backend (default)
  - `uv` to use the [uv](https://docs.astral.sh/uv) package manager
  - `none` to not use a package manager backend and display messages for some operations.

## `usethis status <status>`

Set the development status of the project via trove classifiers.

Possible values (required):

- `usethis status planning` or `usethis status 1` for "Development Status :: 1 - Planning"
- `usethis status pre-alpha` or `usethis status 2` for "Development Status :: 2 - Pre-Alpha"
- `usethis status alpha` or `usethis status 3` for "Development Status :: 3 - Alpha"
- `usethis status beta` or `usethis status 4` for "Development Status :: 4 - Beta"
- `usethis status production` or `usethis status 5` for "Development Status :: 5 - Production/Stable"
- `usethis status mature` or `usethis status 6` for "Development Status :: 6 - Mature"
- `usethis status inactive` or `usethis status 7` for "Development Status :: 7 - Inactive"

Supported options:

- `--badges` to add an associated badge to the README file
- `--quiet` to suppress output

## `usethis list`

Display a table of all available tools and their current usage status.

## `usethis version`

Display the current version of usethis.

## `usethis show`

Show a piece of information about the project.

Currently supported subcommands:

- `usethis show name` to show the name of the project.
- `usethis show sonarqube` to show appropriate contents of a `sonar-projects.properties` file for SonarQube analysis.

## `usethis browse pypi <package>`

Display or open the PyPI landing page associated with another project.

Example:

`usethis browse pypi numpy`

Supported options:

- `--browser` to open the link in the browser automatically.
