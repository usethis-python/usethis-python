# FAQ

## Is this a Python port of usethis in R?

No. `usethis-python` was built from the ground up, and specializes in servicing the Python ecosystem. It is definitely inspired by R's `usethis` package, but it is not a port. There are too many fundamental differences between the two languages' ecosystems and communities to make a port feasible.

One major difference is that `usethis-python` provides a Command Line Interface (CLI) rather than a collection of functions - again this is due to the differences in the language communities, where Python developers are more likely to use a CLI. Actually, under the hood, `usethis-python` does use a collection of functions, but these are not currently guaranteed to be stable or well-documented.

## If I add a tool which is already configured, why does additional configuration get added?

Some configuration is necessary to ensure smooth integrations with other tools. However, usethis will never overwrite existing configuration options, only add new ones, i.e. override defaults. If you want to rely on default values and prevent usethis from overwriting them, you can set a configuration entry explicitly to the default value in your configuration file.

## Why does usethis make formatting changes to my config files?

When modifying files like `pyproject.toml` and `.pre-commit-config.yaml`, usethis
attempts to preserve the original formatting as much as possible.

However, there are some known limitations for YAML files. In Python, there is currently
no YAML parser with pure round-trip support. The closest is `ruamel.yaml`, but it has
some known limitations. If you find that usethis has modified your files in a way
that you did not expect, please open an issue on the usethis GitHub repository, and
if necessary the issue can be escalated to the `ruamel.yaml` repository on SourceForge,
or other appropriate repository.
