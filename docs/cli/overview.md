# 🖥️ Command Line Interface

## Start a New Project

- [`usethis init`](reference.md#usethis-init) — Initialize a new project with recommended defaults.

## Manage Tooling

- [`usethis doc`](reference.md#usethis-doc) — Add/Configure recommended documentation tools (namely, [MkDocs](https://www.mkdocs.org/)).
- [`usethis format`](reference.md#usethis-format) — Add/Configure recommended formatters (namely, [Ruff](https://docs.astral.sh/ruff/formatter/) and [pyproject-fmt](https://pyproject-fmt.readthedocs.io/en/latest/)).
- [`usethis lint`](reference.md#usethis-lint) — Add/Configure recommended linters (namely, [Ruff](https://docs.astral.sh/ruff/linter) and [deptry](https://github.com/fpgmaas/deptry)).
- [`usethis spellcheck`](reference.md#usethis-spellcheck) — Add/Configure recommended spellcheckers (namely, [codespell](https://github.com/codespell-project/codespell)).
- [`usethis test`](reference.md#usethis-test) — Add/Configure a recommended testing framework (namely, [pytest](https://github.com/pytest-dev/pytest) with [Coverage.py](https://github.com/nedbat/coveragepy)).
- [`usethis tool`](reference.md#usethis-tool) — Add/Configure specific tools individually.
  - [`usethis tool codespell`](reference.md#code-quality-tools) - Use the [codespell spellchecker](https://github.com/codespell-project/codespell): detect common spelling mistakes.
  - [`usethis tool deptry`](reference.md#code-quality-tools) - Use the [deptry linter](https://github.com/fpgmaas/deptry): avoid missing or superfluous dependency declarations.
  - [`usethis tool import-linter`](reference.md#code-quality-tools) - Use [Import Linter](https://import-linter.readthedocs.io/en/stable/): enforce a self-imposed architecture on imports.
  - [`usethis tool pre-commit`](reference.md#code-quality-tools) - Use the [pre-commit](https://github.com/pre-commit/pre-commit) framework to manage and maintain Git hooks. Note that this will also install all the hooks to Git.
  - [`usethis tool pyproject-fmt`](reference.md#code-quality-tools) - Use the [pyproject-fmt formatter](https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt): opinionated formatting of 'pyproject.toml' files.
  - [`usethis tool ruff`](reference.md#code-quality-tools) - Use [Ruff](https://github.com/astral-sh/ruff): an extremely fast Python linter and code formatter.
  - [`usethis tool coverage.py`](reference.md#testing) - Use [Coverage.py](https://github.com/nedbat/coveragepy): a code coverage measurement tool.
  - [`usethis tool pytest`](reference.md#testing) - Use the [pytest](https://github.com/pytest-dev/pytest) testing framework.
  - [`usethis tool mkdocs`](reference.md#documentation) - Use [MkDocs](https://www.mkdocs.org/): Generate project documentation sites with Markdown.
  - [`usethis tool pyproject.toml`](reference.md#testing) - Use a [pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-your-pyproject-toml) file to configure the project.
  - [`usethis tool requirements.txt`](reference.md#testing) - Use a [requirements.txt](https://pip.pypa.io/en/stable/reference/requirements-file-format/) file exported from the uv lockfile.

## Manage Configuration

- [`usethis author`](reference.md#usethis-author) — Set new author information for the project.
- [`usethis docstyle`](reference.md#usethis-docstyle-style) — Set a docstring style convention for the project, and [enforce it with Ruff](https://docs.astral.sh/ruff/rules/#pydocstyle-d).
- [`usethis rule`](reference.md#usethis-rule-rulecode) — Set linter rule configuration for specific rules across the project.
- [`usethis status`](reference.md#usethis-status-status) — Set the development status of the project (via trove classifiers).

## Manage the README

- [`usethis badge`](reference.md#usethis-badge) — Add badges to the README file.
- [`usethis readme`](reference.md#usethis-readme) — Add a new README file.

## Information

- [`usethis list`](reference.md#usethis-list) — Display a table of all available tools and their current usage status.
- [`usethis version`](reference.md#usethis-version) — Display the current version of usethis.
- [`usethis browse pypi`](reference.md#usethis-browse-pypi-package) — Display or open the PyPI landing page associated with another project.
- [`usethis show`](reference.md#usethis-show) — Show a specific piece of information about the project.
