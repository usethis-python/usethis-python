# Backends

A **backend** in usethis refers to the package manager that usethis delegates to when performing certain operations. The backend handles tasks like installing dependencies, managing lockfiles, and working with virtual environments. By knowing which package manager your project uses, usethis can automate these steps for you and tailor its instructions accordingly.

## Available Backends

### `uv`

The [`uv`](https://docs.astral.sh/uv) backend is recommended for new projects. When the `uv` backend is active, usethis will:

- Install and uninstall dependencies automatically using `uv add` and `uv remove`.
- Generate and update lockfiles.
- Give instructions using `uv run` to run tools like `ruff`, `pytest`, etc.

### `none`

The `none` backend means no package manager is being used by usethis. When this backend is active, usethis will still configure tools and update configuration files, but it will not install or uninstall any dependencies for you. Instead, the console output will display instructions for you to follow up on manually.

## How the Backend is Selected

By default, usethis auto-detects the appropriate backend using the following logic:

1. If [Poetry](https://python-poetry.org/) usage is detected, usethis warns that Poetry is not fully supported, and falls back to `none`.
2. If `uv` usage is detected (e.g. via the presence of a `uv.lock` file), the `uv` backend is selected.
3. If no `pyproject.toml` exists yet and `uv` is available on your system, the `uv` backend is selected.
4. Otherwise, the `none` backend is used.

You can override this auto-detection by passing the `--backend` option to any usethis command:

```console
uvx usethis tool ruff --backend=none
```

To check which backend usethis would use for your project, run:

```console
uvx usethis show backend
```
