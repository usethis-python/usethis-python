<h1 align="center">
  <img src="https://raw.githubusercontent.com/usethis-python/usethis-python/refs/heads/main/docs/logo.svg" alt="usethis logo" ><br>
</h1>

# usethis

[![usethis](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/usethis-python/usethis-python/main/assets/badge/v1.json)](https://github.com/usethis-python/usethis-python)
[![PyPI Version](https://img.shields.io/pypi/v/usethis.svg)](https://pypi.python.org/pypi/usethis)
[![PyPI License](https://img.shields.io/pypi/l/usethis.svg)](https://github.com/usethis-python/usethis-python?tab=MIT-1-ov-file)
[![PyPI Supported Versions](https://img.shields.io/pypi/pyversions/usethis.svg)](https://pypi.python.org/pypi/usethis)
[![Docs](https://app.readthedocs.org/projects/usethis/badge/?version=stable)](https://usethis.readthedocs.io/en/stable/)

Automatically manage Python tooling and configuration: linters, formatters, and more. A CLI for declaratively configuring your Python projects following best practices.

usethis is a command-line interface to automate the configuration of popular Python tools, workflows, and frameworks. You can use it to declaratively add, remove, and configure tools in an existing project, as well as set up a new project from scratch. It won't break your existing configuration, and ensures all tools work together smoothly.

usethis gives detailed messages about what it is doing (and what you need to do next).

- Output beginning with `✔` represents a task which usethis has automated.
- Output beginning with `☐` represents a task which you need to perform manually.
- Output beginning with `ℹ` gives hints and tips.

Inspired by an [**R** package of the same name](https://usethis.r-lib.org/index.html), this package brings a similar experience to the Python ecosystem as a CLI tool.

## Highlights

- 🧰 First-class support for state-of-the-practice tooling: uv, Ruff, pytest, pre-commit, and many more.
- 🤖 Automatically add and remove tools: declare, install, and configure in one step.
- 🧠 Powerful knowledge of how different tools interact and sensible defaults.
- 🔄 Update existing configuration files automatically.
- 📢 Fully declarative project configuration.
- ⚡ Get started on a new Python project or a new workflow in seconds.

## 🧭 Installation

First, it is strongly recommended you [install the uv package manager](https://docs.astral.sh/uv/getting-started/installation/): this is a simple, documented process. If you're already using uv, make sure you're using at least
version v0.9.9 (run `uv --version` to check, and `uv self update` to upgrade).

You can install usethis directly into the project environment:

```console
# With uv
$ uv add --dev usethis

# With pip
$ pip install usethis
```

Alternatively, you can also run usethis commands in isolation, using `uvx` or `pipx`. For example, to add Ruff to the project:

```console
# With uv
$ uvx usethis tool ruff

# With pipx
$ pipx run usethis tool ruff
```

## 📜 Documentation

The usethis documentation is available at [usethis.readthedocs.io](https://usethis.readthedocs.io/en/stable/).

Additionally, the command line reference documentation can be viewed with `usethis --help`.

## 🖥️ Command Line Interface

### Start a New Project

- [`usethis init`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-init) — Initialize a new project with recommended defaults.

### Manage Tooling

- [`usethis arch`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-arch) — Add/Configure recommended architecture analysis tools (namely, [Import Linter](https://import-linter.readthedocs.io/en/stable/)).
- [`usethis doc`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-doc) — Add/Configure recommended documentation tools (namely, [MkDocs](https://www.mkdocs.org/)).
- [`usethis format`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-format) — Add/Configure recommended formatters (namely, [Ruff](https://docs.astral.sh/ruff/formatter/) and [pyproject-fmt](https://pyproject-fmt.readthedocs.io/en/latest/)).
- [`usethis hook`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-hook) — Add/Configure a recommended git hook framework (namely, [pre-commit](https://github.com/pre-commit/pre-commit)).
- [`usethis lint`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-lint) — Add/Configure recommended linters (namely, [Ruff](https://docs.astral.sh/ruff/linter) and [deptry](https://github.com/fpgmaas/deptry)).
- [`usethis spellcheck`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-spellcheck) — Add/Configure recommended spellcheckers (namely, [codespell](https://github.com/codespell-project/codespell)).
- [`usethis test`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-test) — Add/Configure a recommended testing framework (namely, [pytest](https://github.com/pytest-dev/pytest) with [Coverage.py](https://github.com/nedbat/coveragepy)).
- [`usethis typecheck`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-typecheck) — Add/Configure a recommended type checker (namely, [ty](https://docs.astral.sh/ty/)).
- [`usethis tool`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-tool) — Add/Configure specific tools individually.
  - [`usethis tool codespell`](https://usethis.readthedocs.io/en/stable/cli/reference#code-quality-tools) - Use the [codespell spellchecker](https://github.com/codespell-project/codespell): detect common spelling mistakes.
  - [`usethis tool deptry`](https://usethis.readthedocs.io/en/stable/cli/reference#code-quality-tools) - Use the [deptry linter](https://github.com/fpgmaas/deptry): avoid missing or superfluous dependency declarations.
  - [`usethis tool import-linter`](https://usethis.readthedocs.io/en/stable/cli/reference#code-quality-tools) - Use [Import Linter](https://import-linter.readthedocs.io/en/stable/): enforce a self-imposed architecture on imports.
  - [`usethis tool pre-commit`](https://usethis.readthedocs.io/en/stable/cli/reference#code-quality-tools) - Use the [pre-commit](https://github.com/pre-commit/pre-commit) framework to manage and maintain Git hooks. Note that this will also install all the hooks to Git.
  - [`usethis tool pyproject-fmt`](https://usethis.readthedocs.io/en/stable/cli/reference#code-quality-tools) - Use the [pyproject-fmt formatter](https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt): opinionated formatting of 'pyproject.toml' files.
  - [`usethis tool ruff`](https://usethis.readthedocs.io/en/stable/cli/reference#code-quality-tools) - Use [Ruff](https://github.com/astral-sh/ruff): an extremely fast Python linter and code formatter.
  - [`usethis tool ty`](https://usethis.readthedocs.io/en/stable/cli/reference#code-quality-tools) - Use [ty](https://docs.astral.sh/ty/): an extremely fast Python type checker.
  - [`usethis tool coverage.py`](https://usethis.readthedocs.io/en/stable/cli/reference#testing) - Use [Coverage.py](https://github.com/nedbat/coveragepy): a code coverage measurement tool.
  - [`usethis tool pytest`](https://usethis.readthedocs.io/en/stable/cli/reference#testing) - Use the [pytest](https://github.com/pytest-dev/pytest) testing framework.
  - [`usethis tool mkdocs`](https://usethis.readthedocs.io/en/stable/cli/reference#documentation) - Use [MkDocs](https://www.mkdocs.org/): Generate project documentation sites with Markdown.
  - [`usethis tool pyproject.toml`](https://usethis.readthedocs.io/en/stable/cli/reference#testing) - Use a [pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-your-pyproject-toml) file to configure the project.
  - [`usethis tool requirements.txt`](https://usethis.readthedocs.io/en/stable/cli/reference#testing) - Use a [requirements.txt](https://pip.pypa.io/en/stable/reference/requirements-file-format/) file exported from the uv lockfile.

### Manage Configuration

- [`usethis author`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-author) — Set new author information for the project.
- [`usethis docstyle`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-docstyle-style) — Set a docstring style convention for the project, and [enforce it with Ruff](https://docs.astral.sh/ruff/rules/#pydocstyle-d).
- [`usethis rule`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-rule-rulecode) — Set linter rule configuration for specific rules across the project.
- [`usethis status`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-status-status) — Set the development status of the project (via trove classifiers).

### Manage the README

- [`usethis badge`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-badge) — Add badges to the README file.
- [`usethis readme`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-readme) — Add a new README file.

### Information

- [`usethis list`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-list) — Display a table of all available tools and their current usage status.
- [`usethis version`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-version) — Display the current version of usethis.
- [`usethis browse pypi`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-browse-pypi-package) — Display or open the PyPI landing page associated with another project.
- [`usethis show`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-show) — Show a specific piece of information about the project.
  - [`usethis show backend`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-show) - Show the inferred project manager backend, e.g. 'uv' or 'none'.
  - [`usethis show name`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-show) - Show the name of the project.
  - [`usethis show sonarqube`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-show) - Show appropriate contents of a `sonar-projects.properties` file for SonarQube analysis.

## 💡 Example Usage

### Starting a new project

To start a new project from scratch with a complete set of recommended tooling, simply run
the `uvx usethis init` command.

### Configuring individual tools

You can also configure individual tools one-by-one. For example, to add Ruff on an existing project, run:

```console
$ uvx usethis tool ruff
✔ Adding dependency 'ruff' to the 'dev' group in 'pyproject.toml'.
✔ Adding Ruff config to 'pyproject.toml'.
✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.
✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.
✔ Running the Ruff formatter.
☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.
☐ Run 'uv run ruff format' to run the Ruff formatter.
```

For a detailed breakdown of what each line of the output means, [there is a detailed explanation available](https://usethis.readthedocs.io/en/stable/start/detailed-example).

As another example, to use pytest, run:

```console
$ uvx usethis tool pytest
✔ Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'.
✔ Adding pytest config to 'pyproject.toml'.
✔ Creating '/tests'.
✔ Writing '/tests/conftest.py'.
✔ Selecting Ruff rule 'PT' in 'pyproject.toml'.
☐ Add test files to the '/tests' directory with the format 'test_*.py'.
☐ Add test functions with the format 'test_*()'.
☐ Run 'uv run pytest' to run the tests.
```

See the [CLI Reference](https://usethis.readthedocs.io/en/stable/cli/reference) for a full list of available commands.

## 📚 Similar Projects

Not sure if usethis is the exact fit for your project?

The closest match to usethis is [PyScaffold](https://github.com/pyscaffold/pyscaffold/). It provides a Command Line Interface to automate the creation of a project from a sensible templated structure.

You could also consider your own hard-coded template. Templating tools such as [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and [Copier](https://github.com/copier-org/copier) allow you to create static templates with fixed configuration you can use across multiple projects. However, it's not always obvious which template you should use, and many do not use state-of-practice tooling such as `pyproject.toml`. Also, sometimes a template can overwhelm you with too many unfamiliar tools.

You could consider [this template](https://github.com/pawamoy/copier-uv) or [this one](https://github.com/jlevy/simple-modern-uv), which work with Copier, or [this template](https://github.com/johnthagen/python-blueprint) which works with Cookiecutter.

> [!TIP]
> You can still use usethis as a part of a templates using [hooks](https://cookiecutter.readthedocs.io/en/latest/advanced/hooks.html#using-pre-post-generate-hooks-0-7-0) for Cookiecutter and [tasks](https://copier.readthedocs.io/en/stable/configuring/#tasks) for Copier.

If you're using Cookiecutter, then you can update to a latest version of a template using a tool like [cruft](https://github.com/cruft/cruft). Copier has inbuilt support for template updating. Another template-style option which provides updating is [jaraco/skeleton](https://blog.jaraco.com/skeleton/), which is a specific, git-based template rather than a general templating system.

If you're not interested in templating automations, then [configurator](https://github.com/jamesbraza/configurator) provides a list of useful tooling and configuration to consider for your Python projects. If you're adopting a specific framework like Django, FastAPI, Dagster, or Flask, [this list](https://usethis.readthedocs.io/en/stable/frameworks) gives options for initializing new projects via CLI. If you're looking for guidance on best practices for Python projects, the [Scientific Python Library Development Guide](https://learn.scientific-python.org/development/) is an excellent resource, including its [`repo-review`](https://learn.scientific-python.org/development/guides/repo-review/) tool.

## 🚀 Development

[![Commits since latest release](https://img.shields.io/github/commits-since/usethis-python/usethis-python/latest.svg)](https://github.com/usethis-python/usethis-python/releases)
[![GitHub Actions Status](https://github.com/usethis-python/usethis-python/workflows/CI/badge.svg)](https://github.com/usethis-python/usethis-python/actions)
[![codecov](https://codecov.io/gh/usethis-python/usethis-python/graph/badge.svg?token=0QW539GSP9)](https://codecov.io/gh/usethis-python/usethis-python)
[![CodSpeed](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/usethis-python/usethis-python)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Socket](https://badge.socket.dev/pypi/package/usethis)](https://socket.dev/pypi/package/usethis/overview)

Feature requests are tracked in the [GitHub Issues](https://github.com/usethis-python/usethis-python/issues) page.

### Contributing

See the
[CONTRIBUTING.md](https://github.com/usethis-python/usethis-python/blob/main/CONTRIBUTING.md)
file.

## Acknowledgements

Special thanks to the [Posit](https://posit.co/) team for creating the original [usethis package for **R**](https://usethis.r-lib.org/index.html) , which inspired this project.

Additional thanks are due to the maintainers of the various tools which usethis integrates with, especially the people with [Astral](https://astral.sh/) who created [uv](https://github.com/astral-sh/uv).

## License

usethis is licensed under the MIT license ([LICENSE](https://github.com/usethis-python/usethis-python/blob/main/LICENSE) or <https://opensource.org/licenses/MIT>)

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in usethis by you, as defined in the Apache License, Version 2.0, (<https://www.apache.org/licenses/LICENSE-2.0>), shall be licensed under the MIT license, without any additional terms or conditions.
