# Roundtrip formatting

When modifying files like `pyproject.toml` and `.pre-commit-config.yaml`, usethis
attempts to preserve the original formatting as much as possible.

However, there are some known limitations for YAML files. In Python, there is currently
no YAML parser with pure round-trip support. The closest is `ruamel.yaml`, but it has
some known limitations. If you find that usethis has modified your YAML files in a way
that you did not expect, please open an issue on the usethis GitHub repository, and
if necessary the issue can be escalated to the `ruamel.yaml` repository on SourceForge.
