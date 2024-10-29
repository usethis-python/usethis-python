# usethis

Automate Python project setup and development tasks that are otherwise performed manually.

Inspired by an [**R** package of the same name](https://usethis.r-lib.org/index.html),
this package brings a similar experience to the Python ecosystem as a CLI tool.

## Highlights

- First-class support for state-of-the-practice tooling: `uv`, `ruff`, `pytest`, and `pre-commit`.
- Automatically add and remove tools: declare, install, and configure in one step.
- Powerful knowledge of how different tools interact and sensible defaults.
- Get started on a new Python project or a new workflow in seconds.

## Getting Started

First, it is strongly recommended you [install the `uv` package manager](https://docs.astral.sh/uv/getting-started/installation/): this is a simple, documented process.

If you are starting a new project, it is recommended to call `uv init --lib` to
initialize the project directory.

Then, you can install usethis for the project:

```console
# With uv
$ uv add --dev usethis

# With pip
$ pip install usethis
```

Alternatively, run in isolation, using `uvx` or `pipx`.

## Interface

### `usethis tool`

Add a new tool to a Python project, including:

- declared & installed dependencies with `uv add`,
- relevant `pyproject.toml` configuration,
- any other relevant directories or tool-bespoke configuration files, and
- `.pre-commit-config.yaml` configuration if using `pre-commit`.

Currently supported tools:

- ruff
- pytest
- deptry
- pre-commit

Example:

`usethis tool ruff`

Supported arguments:

- `--remove` to remove the tool instead of adding it
- `--offline` to disable network access and rely on caches

### `usethis ci`

Add Continuous Integration pipelines to the project.

Currently supported platforms:

- Bitbucket

Example:

`usethis ci bitbucket`.

### `usethis browse pypi`

Dispaly or open the PyPI landing page associated with another project.

Example:

`usethis browse pypi numpy`

Supported arguments:

- `--browser` to open the link in the browser automatically.

## Development

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

This project is at the early stages of development. If you are interested in contributing,
please ensure you have a corresponsing GitHub Issue open.

## License

usethis is licensed under the MIT license ([LICENSE](https://github.com/nathanjmcdougall/usethis-python/blob/main/LICENSE) or <https://opensource.org/licenses/MIT>)

Unless you explicitly state otherwise, any contribution intentionally submitted for
inclusion in usethis by you, as defined in the Apache License, Version 2.0,
(<https://www.apache.org/licenses/LICENSE-2.0>), shall be licensed under the
MIT license, without any additional terms or conditions.
