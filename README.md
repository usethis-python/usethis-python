<h1 align="center">
  <img src="https://raw.githubusercontent.com/nathanjmcdougall/usethis-python/refs/heads/main/docs/logo.svg"><br>
</h1>

# usethis

[![usethis](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/nathanjmcdougall/usethis-python/main/assets/badge/v1.json)](https://github.com/nathanjmcdougall/usethis-python)
[![PyPI Version](https://img.shields.io/pypi/v/usethis.svg)](https://pypi.python.org/pypi/usethis)
![PyPI License](https://img.shields.io/pypi/l/usethis.svg)
[![PyPI Supported Versions](https://img.shields.io/pypi/pyversions/usethis.svg)](https://pypi.python.org/pypi/usethis)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![CodSpeed](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/nathanjmcdougall/usethis-python)
[![codecov](https://codecov.io/gh/nathanjmcdougall/usethis-python/graph/badge.svg?token=MU1AZS0KHV)](https://codecov.io/gh/nathanjmcdougall/usethis-python)
[![GitHub Actions Status](https://github.com/nathanjmcdougall/usethis-python/workflows/CI/badge.svg)](https://github.com/nathanjmcdougall/usethis-python/actions)

Automate Python project setup and development tasks that are otherwise performed manually.

`usethis` knows about popular Python tools, workflows and frameworks, and knows how they interact. It can declaratively add and remove tools, configure them, and set up the project for you in a way that won't break your existing configuration and it will make the necessary adjustments to your project configuration files.

`usethis` gives detailed messages about what it is doing (and what you need to do next).

- Output beginning with `✔` represents a task which usethis has automated.
- Output beginning with `☐` represents a task which you need to perform manually.
- Output beginning with `ℹ` gives hints and tips.

Inspired by an [**R** package of the same name](https://usethis.r-lib.org/index.html), this package brings a similar experience to the Python ecosystem as a CLI tool.

> [!TIP]
> `usethis` is great for fresh projects using [uv](https://docs.astral.sh/uv), but also supports updating existing projects. However, this should be considered experimental. If you encounter problems or have feedback, please [open an issue](https://github.com/nathanjmcdougall/usethis-python/issues/new?template=idea.md).

## Highlights

- 🧰 First-class support for state-of-the-practice tooling: `uv`, `ruff`, `pytest`, `pre-commit`, and many more.
- 🤖 Automatically add and remove tools: declare, install, and configure in one step.
- 🧠 Powerful knowledge of how different tools interact and sensible defaults.
- 🔄 Update existing configuration files automatically.
- 📢 Fully declarative project configuration.
- ⚡ Get started on a new Python project or a new workflow in seconds.

## 🧭 Getting Started

First, it is strongly recommended you [install the `uv` package manager](https://docs.astral.sh/uv/getting-started/installation/): this is a simple, documented process. If you're already using `uv`, make sure you're using at least
version v0.5.29 (run `uv version` to check, and `uv self update` to upgrade).

> [!TIP]
> At the moment, `usethis` assumes you will have `uv` installed in some circumstances. Support for projects that don't use `uv` is planned for late 2025.

Then, you can install usethis for the project:

```console
# With uv
$ uv add --dev usethis

# With pip
$ pip install usethis
```

Alternatively, run in isolation, using `uvx` or `pipx`.

## 🖥️ Command Line Interface

### Manage Tooling

- [`usethis ci`](#usethis-ci)
- [`usethis tool`](#usethis-tool)

### Manage Configuration

- [`usethis author`](#usethis-author)
- [`usethis docstyle`](#usethis-docstyle)
- [`usethis rule`](#usethis-rule-rulecode)

### Manage README

- [`usethis badge`](#usethis-badge)
- [`usethis readme`](#usethis-readme)

### Information

- [`usethis list`](#usethis-list)
- [`usethis version`](#usethis-version)
- [`usethis browse pypi`](#usethis-browse-pypi-package)
- [`usethis show`](#usethis-show)

## 💡 Example Usage

To use Ruff on a fresh project, run:

```console
$ uvx usethis tool ruff
✔ Writing 'pyproject.toml'.
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
✔ Adding 'Test on 3.12' to default pipeline in 'bitbucket-pipelines.yml'.
✔ Adding 'Test on 3.13' to default pipeline in 'bitbucket-pipelines.yml'.
☐ Run your pipeline via the Bitbucket website.
```

## 🖥️ Command Reference

### `usethis tool`

Add a new tool to a Python project, including:

- declared & installed dependencies with `uv add`,
- relevant `pyproject.toml` configuration,
- any other relevant directories or tool-bespoke configuration files, and
- `.pre-commit-config.yaml` configuration if using `pre-commit`.

#### Code Quality Tools

- `usethis tool codespell` - Use the codespell spellchecker: detect common spelling mistakes.
- `usethis tool deptry` - Use the deptry linter: avoid missing or superfluous dependency declarations.
- `usethis tool import-linter` - Use Import Linter: enforce a self-imposed architecture on imports.
- `usethis tool pre-commit` - Use the pre-commit framework to manage and maintain pre-commit hooks.
- `usethis tool pyproject-fmt` - Use the pyproject-fmt linter: opinionated formatting of 'pyproject.toml' files.
- `usethis tool ruff` - Use Ruff: an extremely fast Python linter and code formatter.

#### Testing

- `usethis tool coverage` - Use coverage: a code coverage measurement tool.
- `usethis tool pytest` - Use the pytest testing framework.

#### Configuration Files

- `usethis tool pyproject.toml` - Use a pyproject.toml file to configure the project.
- `usethis tool requirements.txt` - Use a requirements.txt file exported from the uv lockfile.

Supported options:

- `--remove` to remove the tool instead of adding it
- `--how` to only print how to use the tool, with no other side effects
- `--offline` to disable network access and rely on caches
- `--frozen` to leave the virtual environment and lockfile unchanged
- `--quiet` to suppress output

### `usethis ci`

Add Continuous Integration pipelines to the project.

Currently supported platforms:

- `usethis ci bitbcuket`

Supported options:

- `--remove` to remove the CI configuration instead of adding it
- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output

### `usethis badge`

Add badges to README.md.

Currently supported badges:

- `usethis badge pre-commit`
- `usethis badge pypi`
- `usethis badge ruff`
- `usethis badge usethis`
- `usethis badge uv`

Supported options:

- `--remove` to remove the badge instead of adding it
- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output

### `usethis rule <rulecode>`

Add (or manage configuration) of Ruff and Deptry rules in `pyproject.toml`.

Example:

`usethis rule RUF001`

Supported options:

- `--remove` to remove the rule selection or ignore status.
- `--ignore` to add the rule to the ignore list (or remove it if --remove is specified).
- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output

### `usethis docstyle`

Set a docstring style convention for the project, and enforce it with Ruff.

Currently supported docstring styles:

- `usethis docstyle numpy`
- `usethis docstyle google`
- `usethis docstyle pep257`

Supported options:

- `--quiet` to suppress output

### `usethis readme`

Add a README.md file to the project.

Supported options:

- `--quiet` to suppress output
- `--badges` to also add badges to the README.md file

### `usethis author`

Set new author information for the project.

Required options:

- `--name` for the new author's name

Other supported options:

- `--email` to set the author email address
- `--overwrite` to overwrite all existing author information
- `--quiet` to suppress output

### `usethis list`

Display a table of all available tools and their current usage status.

### `usethis version`

Display the current version of usethis.

### `usethis show`

Show a piece of information about the project.

Currently supported subcommands:

- `usethis show name` to show the name of the project.
- `usethis show sonarqube` to show appropriate contents of a `sonar-projects.properties` file for SonarQube analysis.

### `usethis browse pypi <package>`

Display or open the PyPI landing page associated with another project.

Example:

`usethis browse pypi numpy`

Supported options:

- `--browser` to open the link in the browser automatically.

## 📚 Similar Projects

Not sure if usethis is the exact fit for your project?

The closest match to usethis is [PyScaffold](https://github.com/pyscaffold/pyscaffold/). It provides a Command Line Interface to automate the creation of a project from a sensible templated structure.

You could also consider your own hard-coded template. Templating tools such as [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and [Copier](https://github.com/copier-org/copier) allow you to create static templates with fixed configuration you can use across multiple projects. However, it's not always obvious which template you should use, and many do not use state-of-practice tooling such as `pyproject.toml`. Also, sometimes a template can overwhelm you with too many unfamiliar tools.

You could [consider this template](https://github.com/pawamoy/copier-uv) which works with Copier, or [this template](https://github.com/johnthagen/python-blueprint) which works with Cookiecutter.

> [!TIP]
> You can still use usethis as a part of a templates using [hooks](https://cookiecutter.readthedocs.io/en/latest/advanced/hooks.html#using-pre-post-generate-hooks-0-7-0) for Cookiecutter and [tasks](https://copier.readthedocs.io/en/stable/configuring/#tasks) for Copier.

One of usethis's strengths is that it can update existing configuration. If you're using Cookiecutter, then you can update to a latest version of a template using a tool like [cruft](https://github.com/cruft/cruft). Copier has inbuilt support for template updating.

## 🚧 Development Roadmap

Major features planned for later in 2025 are:

- Support for users who aren't using uv, e.g. poetry users,
- Support for automated GitHub Actions workflows ([#57](https://github.com/nathanjmcdougall/usethis-python/issues/57)),
- Support for a typechecker (likely Pyright, [#121](https://github.com/nathanjmcdougall/usethis-python/issues/121)), and
- Support for documentation pages (likely using mkdocs, [#188](https://github.com/nathanjmcdougall/usethis-python/issues/188)).

Other features are tracked in the [GitHub Issues](https://github.com/nathanjmcdougall/usethis-python/issues) page.

## 🙌 Contributing

See the
[CONTRIBUTING.md](https://github.com/nathanjmcdougall/usethis-python/blob/main/CONTRIBUTING.md)
file.

## License

usethis is licensed under the MIT license ([LICENSE](https://github.com/nathanjmcdougall/usethis-python/blob/main/LICENSE) or <https://opensource.org/licenses/MIT>)

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in usethis by you, as defined in the Apache License, Version 2.0, (<https://www.apache.org/licenses/LICENSE-2.0>), shall be licensed under the MIT license, without any additional terms or conditions.
