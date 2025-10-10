# 🧭 Getting Started

First, it is strongly recommended you [install the uv package manager](https://docs.astral.sh/uv/getting-started/installation/): this is a simple, documented process. If you're already using uv, make sure you're using at least
version v0.6.8 (run `uv --version` to check, and `uv self update` to upgrade).

You can install usethis directly into the project environment:

```console
# With uv
$ uv add --dev usethis

# With pip
$ pip install usethis
```

Alternatively, you can also run usethis commands in isolation, using `uvx` or `pipx`. For example, to add Ruff to the project:

```console
# With uv
$ uvx usethis tool ruff

# With pipx
$ pipx run usethis tool ruff
```
