# 💡 Example Usage

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
