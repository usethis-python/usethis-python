# 💡 Example Usage

## Starting a new project

To start a new project from scratch with a complete set of recommended tooling, simply run
the `uvx usethis init` command.

## Configuring individual tools

You can also configure individual tools one-by-one. For example, to add Ruff on an existing project, run:

<!--
```python
import shutil
import tempfile
from pathlib import Path

from usethis._backend.uv.call import call_uv_subprocess
from usethis._config import usethis_config
from usethis._console import _cached_warn_print, get_icon_mode
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._test import CliRunner, change_cwd
from usethis._ui.interface.tool import app

_cached_warn_print.cache_clear()
get_icon_mode.cache_clear()

tmpdir = Path(tempfile.mkdtemp())
try:
    with change_cwd(tmpdir):
        call_uv_subprocess(
            ["init", "--lib", "--python", "3.13", "--vcs", "none"],
            change_toml=True,
        )
        with PyprojectTOMLManager() as mgr:
            mgr[["tool", "uv", "environment"]] = []

    runner = CliRunner()
    with change_cwd(tmpdir), usethis_config.set(frozen=True):
        result = runner.invoke_safe(app, ["ruff"])

    assert result.exit_code == 0, result.output
    assert result.output == (
        "✔ Adding dependency 'ruff' to the 'dev' group in 'pyproject.toml'.\n"
        "✔ Adding Ruff config to 'pyproject.toml'.\n"
        "✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', \n"
        "'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.\n"
        "✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.\n"
        "☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.\n"
        "☐ Run 'uv run ruff format' to run the Ruff formatter.\n"
    )
finally:
    shutil.rmtree(tmpdir)
```
-->

```console
$ uvx usethis tool ruff
✔ Adding dependency 'ruff' to the 'dev' group in 'pyproject.toml'.
✔ Adding Ruff config to 'pyproject.toml'.
✔ Selecting Ruff rules 'A', 'C4', 'E4', 'E7', 'E9', 'F', 'FLY', 'FURB', 'I', 'PLE', 'PLR', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.
✔ Ignoring Ruff rules 'PLR2004', 'SIM108' in 'pyproject.toml'.
☐ Run 'uv run ruff check --fix' to run the Ruff linter with autofixes.
☐ Run 'uv run ruff format' to run the Ruff formatter.
```

For a detailed breakdown of what each line of the output means, [there is a detailed explanation available](detailed-example.md).

As another example, to use pytest, run:

<!--
```python
import shutil
import tempfile
from pathlib import Path

from usethis._config import usethis_config
from usethis._console import _cached_warn_print, get_icon_mode
from usethis._test import CliRunner, change_cwd
from usethis._ui.interface.tool import app

_cached_warn_print.cache_clear()
get_icon_mode.cache_clear()

tmpdir = Path(tempfile.mkdtemp())
try:
    (tmpdir / "pyproject.toml").write_text(
        "[project]\n"
        'name = "example"\n'
        'version = "0.1.0"\n'
        "\n"
        "[tool.ruff]\n"
        "line-length = 88\n"
    )

    runner = CliRunner()
    with change_cwd(tmpdir), usethis_config.set(frozen=True):
        result = runner.invoke_safe(app, ["pytest", "--backend=uv"])

    assert result.exit_code == 0, result.output
    assert result.output == (
        "✔ Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'.\n"
        "✔ Adding pytest config to 'pyproject.toml'.\n"
        "✔ Creating '/tests'.\n"
        "✔ Writing '/tests/conftest.py'.\n"
        "✔ Selecting Ruff rule 'PT' in 'pyproject.toml'.\n"
        "☐ Add test files to the '/tests' directory with the format 'test_*.py'.\n"
        "☐ Add test functions with the format 'test_*()'.\n"
        "☐ Run 'uv run pytest' to run the tests.\n"
    )
finally:
    shutil.rmtree(tmpdir)
```
-->

```console
$ uvx usethis tool pytest
✔ Adding dependency 'pytest' to the 'test' group in 'pyproject.toml'.
✔ Adding pytest config to 'pyproject.toml'.
✔ Creating '/tests'.
✔ Writing '/tests/conftest.py'.
✔ Selecting Ruff rule 'PT' in 'pyproject.toml'.
☐ Add test files to the '/tests' directory with the format 'test_*.py'.
☐ Add test functions with the format 'test_*()'.
☐ Run 'uv run pytest' to run the tests.
```

See the [CLI Reference](../cli/reference.md) for a full list of available commands.
