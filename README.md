<h1 align="center">
  <img src="https://raw.githubusercontent.com/nathanjmcdougall/usethis-python/refs/heads/main/docs/logo.svg"><br>
</h1>

# usethis

[![PyPI Version](<https://img.shields.io/pypi/v/usethis.svg>)](<https://pypi.python.org/pypi/usethis>)
![PyPI License](<https://img.shields.io/pypi/l/usethis.svg>)
[![PyPI Supported Versions](<https://img.shields.io/pypi/pyversions/usethis.svg>)](<https://pypi.python.org/pypi/usethis>)
[![uv](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json>)](<https://github.com/astral-sh/uv>)
[![Ruff](<https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json>)](<https://github.com/astral-sh/ruff>)
[![CodSpeed](https://img.shields.io/endpoint?url=https://codspeed.io/badge.json)](https://codspeed.io/nathanjmcdougall/usethis-python)
[![codecov](https://codecov.io/gh/nathanjmcdougall/usethis-python/graph/badge.svg?token=MU1AZS0KHV)](https://codecov.io/gh/nathanjmcdougall/usethis-python)
[![GitHub Actions Status](https://github.com/nathanjmcdougall/usethis-python/workflows/CI/badge.svg)](https://github.com/nathanjmcdougall/usethis-python/actions)

Automate Python project setup and development tasks that are otherwise performed manually.

usethis knows about popular Python tools, workflows and frameworks, and knows how they
interact. It can add and remove tools, configure them, and set up the project for you
in a way that won't break your existing configuration and it will make the necessary
adjustments to your project configuration files.

usethis gives detailed messages about what it is doing (and what you need to do next).

- Output beginning with `✔` represents a task which usethis has automated.
- Output beginning with `☐` represents a task which you need to perform manually.
- Output beginning with `ℹ` gives hints and tips.

Inspired by an [**R** package of the same name](https://usethis.r-lib.org/index.html),
this package brings a similar experience to the Python ecosystem as a CLI tool.

## Highlights

- First-class support for state-of-the-practice tooling: `uv`, `ruff`, `pytest`, `pre-commit`, and many more.
- Automatically add and remove tools: declare, install, and configure in one step.
- Powerful knowledge of how different tools interact and sensible defaults.
- Get started on a new Python project or a new workflow in seconds.

## Getting Started

First, it is strongly recommended you [install the `uv` package manager](https://docs.astral.sh/uv/getting-started/installation/): this is a simple, documented process. If you're already using `uv`, make sure you're using at least
version v0.5.29 (run `uv version` to check, and `uv self update` to upgrade).

Then, you can install usethis for the project:

```console
# With uv
$ uv add --dev usethis

# With pip
$ pip install usethis
```

Alternatively, run in isolation, using `uvx` or `pipx`.

## Example Usage

To use Ruff on a fresh project, run:

```console
$ uvx usethis tool ruff
✔ Writing 'pyproject.toml'.
✔ Adding dependency 'ruff' to the 'dev' dependency group.
✔ Adding Ruff config to 'pyproject.toml'.
✔ Enabling Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'EM', 'F', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.
✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.
☐ Run 'ruff check --fix' to run the Ruff linter with autofixes.
☐ Run 'ruff format' to run the Ruff formatter.
```

To use pytest, run:

```console
$ uvx usethis tool pytest
✔ Adding dependency 'pytest' to the 'test' dependency group in 'pyproject.toml'.
✔ Adding pytest config to 'pyproject.toml'.
✔ Enabling Ruff rule 'PT' in 'pyproject.toml'.
✔ Creating '/tests'.
✔ Writing '/tests/conftest.py'.
☐ Add test files to the '/tests' directory with the format 'test_*.py'.
☐ Add test functions with the format 'test_*()'.
☐ Run 'pytest' to run the tests.
```

To configure Bitbucket pipelines, run:

```console
$ uvx usethis ci bitbucket
✔ Writing 'bitbucket-pipelines.yml'.
✔ Adding cache 'uv' definition to 'bitbucket-pipelines.yml'.
✔ Adding 'Test on 3.12' to default pipeline in 'bitbucket-pipelines.yml'.
✔ Adding 'Test on 3.13' to default pipeline in 'bitbucket-pipelines.yml'.
☐ Run your pipeline via the Bitbucket website.
```

## Interface

### `usethis tool`

Add a new tool to a Python project, including:

- declared & installed dependencies with `uv add`,
- relevant `pyproject.toml` configuration,
- any other relevant directories or tool-bespoke configuration files, and
- `.pre-commit-config.yaml` configuration if using `pre-commit`.

Currently supported tools:

- `usethis tool codespell`
- `usethis tool coverage`
- `usethis tool deptry`
- `usethis tool pre-commit`
- `usethis tool pyproject-fmt`
- `usethis tool pyproject.toml`
- `usethis tool pytest`
- `usethis tool requirements.txt`
- `usethis tool ruff`

Supported arguments:

- `--remove` to remove the tool instead of adding it
- `--offline` to disable network access and rely on caches
- `--frozen` to leave the virtual environment and lockfile unchanged
- `--quiet` to suppress output

### `usethis badge`

Add badges to README.md.

Currently supported badges:

- `usethis badge ruff`
- `usethis badge pre-commit`
- `usethis badge pypi`

Supported arguments:

- `--remove` to remove the badge instead of adding it
- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output

### `usethis ci`

Add Continuous Integration pipelines to the project.

Currently supported platforms:

- `usethis ci bitbcuket`

Supported arguments:

- `--remove` to remove the CI configuration instead of adding it
- `--offline` to disable network access and rely on caches
- `--quiet` to suppress output

### `usethis browse pypi <package>`

Display or open the PyPI landing page associated with another project.

Example:

`usethis browse pypi numpy`

Supported arguments:

- `--browser` to open the link in the browser automatically.

## Development

This project is at the early stages of development. If you are interested in contributing,
please ensure you have a corresponding GitHub Issue open.

## License

usethis is licensed under the MIT license ([LICENSE](https://github.com/nathanjmcdougall/usethis-python/blob/main/LICENSE) or <https://opensource.org/licenses/MIT>)

Unless you explicitly state otherwise, any contribution intentionally submitted for
inclusion in usethis by you, as defined in the Apache License, Version 2.0,
(<https://www.apache.org/licenses/LICENSE-2.0>), shall be licensed under the
MIT license, without any additional terms or conditions.
