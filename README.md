# usethis

Automate Python package and project setup tasks that are otherwise performed manually.

## Commands

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

### Hypothetical Interface

The current interfaces are being considered:

- `usethis tool` to configure a tool, e.g. `usethis tool ruff`. Adding a tool will install it, as well as add relevant files and/or configuration to use the tool. Tools can interact, for example if you run `usethis tool pytest` it will install `pytest`, add it as a testing dependency, etc. but if you then run `usethis tool ruff` then `usethis` will strategically configure `pytest` with `pytest`-specific linter rules. Also vice-versa - if you already have ruff configured but then run `usethis tool pytest`, then `usethis` will strategically add new ruff configuration to reflect the fact you are now using `pytest`. In this way, `usethis` calls are order-invariant.
- `usethis badge` to add various badges. Note that you can often get the badge with `usethis tool ... --badge` when available for a tool.
- `usethis browse` to browse something, e.g. `usethis browse pypi ruff` would open the URL to the PyPI page for `ruff` in the browser.
- `usethis license` to choose a license, e.g. `usethis license mit` to use the MIT license.
- `usethis file` to create a python file at the specifified location. Add the `--test` flag to create a corresponding test file in the `tests` directory.
- `usethis package` to configure the packages distributed by your project.

### Keeping Config Sections Synchronized

Tools are not configured independently from one another. For example, if we are using pytest, we might want to enable the PTD rules in ruff, whereas if we are not using pytest, it really doesn't make sense to do this. Another example would be shared config, e.g. if two tools both need to know that the source code is in the `src` folder. One last example is a tool that cannot be used at all without another, e.g. `setuptools_scm` requires that we have setuptools in the first place.

Each usethis function is potentially the dependent for another, and itself might have dependents. Both directions need to be considered when the function is designed and tested. In general, functions need to be able to read configuration to determine which actions to take, and then they need robust write functionality to extend existing config and append to existing files.

Generally, information for tool configuration should be in `pyproject.toml` in the appropriate section. In rare cases, it might be necessary to store information in a `[tool.usethis]` section, although this is not yet clear.

#### Worked Example

We might run `usethis package` to make a distribution package associated with the project. This will be stored in the `packages` list in `[tool.setuptools]` in `pyproject.toml`. Then `usethis tool deptry` to set up deptry. This will add config to `pyproject.toml` for deptry, including ignoring the rule code DEP001 specifically for the packages listed by `usethis package`. If we added a new package with `usethis package --name other_package` then the deptry configuration would be extended to include this new package.
