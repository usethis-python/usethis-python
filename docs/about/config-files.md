# Configuration Files

## The General Principle

When writing configuration for a tool, usethis follows the same configuration file discovery logic as the tool itself.

This means:

- If you already have an existing configuration file that the tool supports, usethis will write to that file.
- If multiple supported configuration files exist, usethis uses the one the tool itself would use (typically the one with highest precedence).
- If no existing configuration file is found, usethis falls back to `pyproject.toml` when the tool supports it and `pyproject.toml` already exists in the project. Otherwise it creates a tool-specific default configuration file.

## Per-Tool Config File Reference

The tables below list the supported configuration files for each tool, in priority order (highest priority first). When usethis needs to resolve which file to use and multiple supported files exist, it uses the highest-priority file that already exists.

### codespell

| File             | Section            |
| ---------------- | ------------------ |
| `.codespellrc`   | _(top-level)_      |
| `setup.cfg`      | `[codespell]`      |
| `pyproject.toml` | `[tool.codespell]` |

Default (when no config file exists): `pyproject.toml` if it already exists in the project, otherwise `.codespellrc`.

Note: usethis checks for _existing codespell configuration_ (not just file existence) when determining the active file.

### Coverage.py

| File               | Section                                     |
| ------------------ | ------------------------------------------- |
| `.coveragerc`      | _(top-level)_                               |
| `.coveragerc.toml` | _(top-level)_                               |
| `setup.cfg`        | `[coverage:run]`, `[coverage:report]`, etc. |
| `tox.ini`          | `[coverage:run]`, `[coverage:report]`, etc. |
| `pyproject.toml`   | `[tool.coverage]`                           |

Default (when no config file exists): `pyproject.toml` if it already exists in the project, otherwise `.coveragerc`.

### deptry

| File             | Section         |
| ---------------- | --------------- |
| `pyproject.toml` | `[tool.deptry]` |

deptry only supports configuration in `pyproject.toml`.

### Import Linter

| File             | Section               |
| ---------------- | --------------------- |
| `setup.cfg`      | `[importlinter]`      |
| `.importlinter`  | `[importlinter]`      |
| `pyproject.toml` | `[tool.importlinter]` |

Default (when no config file exists): `pyproject.toml` if it already exists in the project, otherwise `.importlinter`.

### MkDocs

| File         | Section       |
| ------------ | ------------- |
| `mkdocs.yml` | _(top-level)_ |

MkDocs only supports configuration in `mkdocs.yml`.

### pre-commit

| File                      | Section       |
| ------------------------- | ------------- |
| `.pre-commit-config.yaml` | _(top-level)_ |

pre-commit only supports configuration in `.pre-commit-config.yaml`.

### pyproject-fmt

| File             | Section                |
| ---------------- | ---------------------- |
| `pyproject.toml` | `[tool.pyproject-fmt]` |

pyproject-fmt only supports configuration in `pyproject.toml`.

### pyproject.toml

| File             | Section       |
| ---------------- | ------------- |
| `pyproject.toml` | _(top-level)_ |

`pyproject.toml` only supports configuration in `pyproject.toml`.

### pytest

| File             | Section                     |
| ---------------- | --------------------------- |
| `pytest.ini`     | `[pytest]`                  |
| `.pytest.ini`    | `[pytest]`                  |
| `pyproject.toml` | `[tool.pytest.ini_options]` |
| `tox.ini`        | `[pytest]`                  |
| `setup.cfg`      | `[tool:pytest]`             |

Default (when no config file exists): `pyproject.toml` if it already exists in the project, otherwise `pytest.ini`.

Note: usethis follows [pytest's own configuration file discovery logic](https://docs.pytest.org/en/stable/reference/customize.html#finding-the-rootdir). In particular, `pytest.ini` and `.pytest.ini` always match when they exist, whereas `pyproject.toml` only matches if it contains a `[tool.pytest.ini_options]` table. A `pyproject.toml` file without this table is only used as a last resort when no other config file is found.

### requirements.txt

| File             | Section               |
| ---------------- | --------------------- |
| `pyproject.toml` | `[tool.sync-with-uv]` |

`requirements.txt` only supports configuration in `pyproject.toml`.

### Ruff

| File             | Section       |
| ---------------- | ------------- |
| `.ruff.toml`     | _(top-level)_ |
| `ruff.toml`      | _(top-level)_ |
| `pyproject.toml` | `[tool.ruff]` |

Default (when no config file exists): `pyproject.toml` if it already exists in the project, otherwise `ruff.toml`.

### Tach

| File        | Section       |
| ----------- | ------------- |
| `tach.toml` | _(top-level)_ |

Tach only supports configuration in `tach.toml`.

### ty

| File             | Section       |
| ---------------- | ------------- |
| `.ty.toml`       | _(top-level)_ |
| `ty.toml`        | _(top-level)_ |
| `pyproject.toml` | `[tool.ty]`   |

Default (when no config file exists): `pyproject.toml` if it already exists in the project, otherwise `ty.toml`.
