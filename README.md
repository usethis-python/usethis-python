<h1 align="center">
  <img src="https://raw.githubusercontent.com/usethis-python/usethis-python/refs/heads/main/docs/logo.svg"><br>
</h1>

# usethis

[![usethis](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/usethis-python/usethis-python/main/assets/badge/v1.json)](https://github.com/usethis-python/usethis-python)
[![PyPI Version](https://img.shields.io/pypi/v/usethis.svg)](https://pypi.python.org/pypi/usethis)
![PyPI License](https://img.shields.io/pypi/l/usethis.svg)
[![PyPI Supported Versions](https://img.shields.io/pypi/pyversions/usethis.svg)](https://pypi.python.org/pypi/usethis)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![codecov](https://codecov.io/gh/usethis-python/usethis-python/graph/badge.svg?token=0QW539GSP9)](https://codecov.io/gh/usethis-python/usethis-python)
[![GitHub Actions Status](https://github.com/usethis-python/usethis-python/workflows/CI/badge.svg)](https://github.com/usethis-python/usethis-python/actions)
[![Docs](https://app.readthedocs.org/projects/usethis/badge/?version=stable)](https://usethis.readthedocs.io/en/stable/)

Automate Python project setup and development tasks that are otherwise performed manually.

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

## 🧭 Getting Started

First, it is strongly recommended you [install the uv package manager](https://docs.astral.sh/uv/getting-started/installation/): this is a simple, documented process. If you're already using uv, make sure you're using at least
version v0.6.8 (run `uv --version` to check, and `uv self update` to upgrade).

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

## 🖥️ Command Line Interface

### Start a New Project

- [`usethis init`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-init) — Initialize a new project with recommended defaults.

### Manage Tooling

- [`usethis doc`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-doc) — Add/Configure recommended documentation tools (namely, [MkDocs](https://www.mkdocs.org/)).
- [`usethis format`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-format) — Add/Configure recommended formatters (namely, [Ruff](https://docs.astral.sh/ruff/formatter/) and [pyproject-fmt](https://pyproject-fmt.readthedocs.io/en/latest/)).
- [`usethis lint`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-lint) — Add/Configure recommended linters (namely, [Ruff](https://docs.astral.sh/ruff/linter) and [deptry](https://github.com/fpgmaas/deptry)).
- [`usethis spellcheck`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-spellcheck) — Add/Configure recommended spellcheckers (namely, [codespell](https://github.com/codespell-project/codespell)).
- [`usethis test`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-test) — Add/Configure a recommended testing framework (namely, [pytest](https://github.com/pytest-dev/pytest) with [Coverage.py](https://github.com/nedbat/coveragepy)).
- [`usethis ci`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-ci) — Add/Configure a specified CI service.
- [`usethis tool`](https://usethis.readthedocs.io/en/stable/cli/reference#usethis-tool) — Add/Configure specific tools individually.

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

## 💡 Example Usage

To start a new project from scratch with a complete set of recommended tooling, run:

```console
$ uvx usethis init
✔ Writing 'pyproject.toml' and initializing project.
✔ Writing 'README.md'.
☐ Populate 'README.md' to help users understand the project.
✔ Adding recommended documentation tools.
☐ Run 'uv run mkdocs build' to build the documentation.
☐ Run 'uv run mkdocs serve' to serve the documentation locally.
✔ Adding recommended linters.
☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.
☐ Run 'uv run deptry src' to run deptry.
✔ Adding recommended formatters.
☐ Run 'uv run ruff format' to run the Ruff formatter.
☐ Run 'uv run pyproject-fmt pyproject.toml' to run pyproject-fmt.
✔ Adding recommended spellcheckers.
☐ Run 'uv run codespell' to run the Codespell spellchecker.
✔ Adding recommended test frameworks.
☐ Add test files to the '/tests' directory with the format 'test_*.py'.
☐ Add test functions with the format 'test_*()'.
☐ Run 'uv run pytest' to run the tests.
☐ Run 'uv run pytest --cov' to run your tests with Coverage.py.
```

To use Ruff on an existing project, run:

```console
$ uvx usethis tool ruff
✔ Adding dependency 'ruff' to the 'dev' group in 'pyproject.toml'.
✔ Adding Ruff config to 'pyproject.toml'.
✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.
✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.
☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.
☐ Run 'uv run ruff format' to run the Ruff formatter.
```

To use pytest, run:

```console
$ uvx usethis tool pytest
✔ Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'.
✔ Adding pytest config to 'pyproject.toml'.
✔ Selecting Ruff rule 'PT' in 'pyproject.toml'.
✔ Creating '/tests'.
✔ Writing '/tests/conftest.py'.
☐ Add test files to the '/tests' directory with the format 'test_*.py'.
☐ Add test functions with the format 'test_*()'.
☐ Run 'uv run pytest' to run the tests.
```

To configure Bitbucket pipelines, run:

```console
$ uvx usethis ci bitbucket
✔ Writing 'bitbucket-pipelines.yml'.
✔ Adding cache 'uv' definition to 'bitbucket-pipelines.yml'.
✔ Adding 'Run Ruff' to default pipeline in 'bitbucket-pipelines.yml'.
✔ Adding 'Test on 3.13' to default pipeline in 'bitbucket-pipelines.yml'.
✔ Adding 'Test on 3.14' to default pipeline in 'bitbucket-pipelines.yml'.
☐ Run your pipeline via the Bitbucket website.
```

## 📚 Similar Projects

Not sure if usethis is the exact fit for your project?

The closest match to usethis is [PyScaffold](https://github.com/pyscaffold/pyscaffold/). It provides a Command Line Interface to automate the creation of a project from a sensible templated structure.

You could also consider your own hard-coded template. Templating tools such as [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and [Copier](https://github.com/copier-org/copier) allow you to create static templates with fixed configuration you can use across multiple projects. However, it's not always obvious which template you should use, and many do not use state-of-practice tooling such as `pyproject.toml`. Also, sometimes a template can overwhelm you with too many unfamiliar tools.

You could consider [this template](https://github.com/pawamoy/copier-uv) or [this one](https://github.com/jlevy/simple-modern-uv), which work with Copier, or [this template](https://github.com/johnthagen/python-blueprint) which works with Cookiecutter.

> [!TIP]
> You can still use usethis as a part of a templates using [hooks](https://cookiecutter.readthedocs.io/en/latest/advanced/hooks.html#using-pre-post-generate-hooks-0-7-0) for Cookiecutter and [tasks](https://copier.readthedocs.io/en/stable/configuring/#tasks) for Copier.

If you're using Cookiecutter, then you can update to a latest version of a template using a tool like [cruft](https://github.com/cruft/cruft). Copier has inbuilt support for template updating. Another template-style option which provides updating is [jaraco/skeleton](https://blog.jaraco.com/skeleton/), which is a specific, git-based template rather than a general templating system.

If you're not interested in templating automations, then [configurator](https://github.com/jamesbraza/configurator) provides a list of useful tooling and configuration to consider for your Python projects.

## 🚀 Development

[![Commits since latest release](https://img.shields.io/github/commits-since/usethis-python/usethis-python/latest.svg)](https://github.com/usethis-python/usethis-python/releases)
[![CodSpeed](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/usethis-python/usethis-python)

### Roadmap

Major features planned for later in 2025 are:

- Support for automated GitHub Actions workflows ([#57](https://github.com/usethis-python/usethis-python/issues/57)),
- Support for a typechecker (likely Pyright, [#121](https://github.com/usethis-python/usethis-python/issues/121)), and

Other features are tracked in the [GitHub Issues](https://github.com/usethis-python/usethis-python/issues) page.

### Contributing

See the
[CONTRIBUTING.md](https://github.com/usethis-python/usethis-python/blob/main/CONTRIBUTING.md)
file.

## License

usethis is licensed under the MIT license ([LICENSE](https://github.com/usethis-python/usethis-python/blob/main/LICENSE) or <https://opensource.org/licenses/MIT>)

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in usethis by you, as defined in the Apache License, Version 2.0, (<https://www.apache.org/licenses/LICENSE-2.0>), shall be licensed under the MIT license, without any additional terms or conditions.
