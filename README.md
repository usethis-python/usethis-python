# usethis

Automate Python package and project setup tasks that are otherwise performed manually.

## Development

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

### Plan for interface

The current interfaces are being considered:

- `usethis tool` to configure a tool, e.g. `usethis tool ruff`. Adding a tool will install it, as well as add relevant files and/or configuration to use the tool. Tools can interact, for example if you run `usethis tool pytest` it wo;; install `pytest`, add it as a testing dependency, etc. but if you then run `usethis tool ruff` then `usethis` will strategically configure `pytest` with `pytest`-specific linter rules. Also vice-versa - if you already have ruff configured but then run `usethis tool pytest`, then `usethis` will strategically add new ruff configuration to reflect the fact you are now using `pytest`. In this way, `usethis` calls are order-invariant.
- `usethis badge` to add various badges. Note that you can often get the badge with `usethis tool ... --badge` when available for a tool.
- `usethis browse` to browse something, e.g. `usethis browse pypi ruff` would open the URL to the PyPI page for `ruff` in the browser.
- `usethis license` to choose a license, e.g. `usethis license mit` to use the MIT license.
- `usethis file` to create a python file at the specifified location. Add the `--test` flag to create a corresponding test file in the `tests` directory.

### Keeping Config Sections Synchronized

Tools are not configured independently from one another. For example, if we are using pytest, we might want to enable the PTD rules in ruff, whereas if we are not using pytest, it really doesn't make sense to do this. Another example would be shared config, e.g. if two tools both need to know that the source code is in the `src` folder. One last example is a tool that cannot be used at all without another, e.g. `setuptools_scm` requires that we have setuptools in the first place.

Each usethis function is potentially the dependent for another, and itself might have dependents. Both directions need to be considered when the function is designed and tested. In general, functions need to be able to read configuration to determine which actions to take, and then they need robust write functionality to extend existing config and append to existing files.

Generally, information for tool configuration should be in `pyproject.toml` in the appropriate section. In rare cases, it might be necessary to store information in a `[tool.usethis]` section, although this is not yet clear.
