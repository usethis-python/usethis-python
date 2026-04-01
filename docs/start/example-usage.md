# 💡 Example Usage

## Starting a new project

To start a new project from scratch with a complete set of recommended tooling, simply run
the `uvx usethis init` command.

## Configuring individual tools

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

For a detailed breakdown of what each line of the output means, [there is a detailed explanation available](detailed-example.md).

As another example, to use pytest, run:

```console
$ uvx usethis tool pytest
✔ Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'.
✔ Adding pytest config to 'pyproject.toml'.
✔ Creating '/tests'.
✔ Writing '/tests/conftest.py'.
✔ Writing '/tests/test_example.py'.
✔ Selecting Ruff rule 'PT' in 'pyproject.toml'.
☐ Add test files to the '/tests' directory with the format 'test_*.py'.
☐ Add test functions with the format 'test_*()'.
☐ Run 'uv run pytest' to run the tests.
```

See the [CLI Reference](../cli/reference.md) for a full list of available commands.
