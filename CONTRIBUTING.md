# Contributing

Thank you for your interest in contributing to usethis! There are issues labeled [Good First Issue](https://github.com/usethis-python/usethis-python/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22) which are good opportunities for new contributors.

Since `usethis` is at early stages of development, please [ensure a GitHub Issue is opened](https://github.com/usethis-python/usethis-python/issues) before starting work on a new feature or bug fix. This helps to ensure that the feature is aligned with the project's goals and that there is no duplication of effort. Sometimes these Issues don't have enough guidance in them, so consider asking for some more guidance from the ticket creator before getting started.

## Setup

### Development Environment

[uv](https://github.com/astral-sh/uv) is required to install the development environment. You can install it using the instructions here:

<https://docs.astral.sh/uv/getting-started/installation/>

Then with the current working directory set to the project root, run:

```shell
uv sync
```

### Git Hooks

This project uses the `prek` framework (similar to `pre-commit`) to manage Git hooks. To install the hooks, run:

```shell
uv run prek install
```

## Testing

### Running the Test Suite

To run the tests, simply run:

```shell
uv run pytest
```

### Writing Tests

Tests are written using the `pytest` framework. The test suite is located in the `tests` directory. The tests are organized into subdirectories with a directory structure that mirrors the structure of the code being tested. This makes it easy to find the tests for a specific module or function. For example: `src/x/y/z.py` would be tested at `tests/x/y/test_z.py`.

Tests are usually organized into classes centred around the objects being tested; either modules or classes. For example, tests for a class `MyClass` would be tested in a class `TestMyClass`. If testing a method of a class, the method tests would be nested within the class test. For example, tests for the `my_method` method of `MyClass` would be in a nested class `TestMyMethod` within `TestMyClass`.

PRs should ideally include tests for any new features or bug fixes.

To diagnose slow test speeds, you can run

```shell
uv run pyinstrument -m pytest
```

With any `pytest` options you wish to include, e.g. `-k` to run specific tests, or `--collect-only` to only profile test collection time. This will generate a CLI-friendly report of where time is being spent. For an interactive HTML report, you can run `pyinstrument` with the `-r=html` option before the `-m pytest` part.

A common pattern in the test suite is to use a [pytest fixture](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html) to get a temporary directory, and then use the `usethis._test.change_cwd` context manager in the test to simulate running usethis from within a project. If you're writing a new test and noticing unexpected creations or modifications of files, it's a sign that the working directory has not been properly configured for the test.

## Documentation

Documentation is hosted at <https://usethis.readthedocs.io/en/stable/>. It can be served locally with:

```shell
uv run mkdocs serve
```

Docstrings use [Google Style](https://google.github.io/styleguide/pyguide.html#381-docstrings). Note that type annotations should not be repeated in the docstring, since these are already present in the function signature.

## Version Control

Git is used for version control, using [Trunk-based development](https://trunkbaseddevelopment.com/).

It is recommended that you use signed commits, although this is not a requirement. Please see this guide from the VS Code project for instructions on how to do this: <https://github.com/microsoft/vscode/wiki/Commit-Signing>

## Architecture

This project uses [Import Linter](https://import-linter.readthedocs.io/en/stable/) to enforce a software architecture. Refer to the `[[tool.importlinter.contracts]]` sections in `pyproject.toml` to understand the structure of the project.

### Global Configuration State

The `usethis._config.usethis_config` object manages global application state that affects behavior across the entire application. This design avoids the need for pass-through variables that would otherwise need to be threaded through many layers of function calls. It provides a context manager, `usethis_config.set()`, which temporarily overrides global settings:

```python
# Temporarily suppress all output except warnings and errors
with usethis_config.set(alert_only=True):
    # Code here runs with modified config
    do_something()
# Original settings are automatically restored
```

## Python Version Support

This project supports all versions of Python through until end of life. The development environment uses the oldest supported version, which is given in the `.python-version` file. The GitHub Actions pipeline tests all supported versions.

## Conventions

### Print statements

To ensure the `--quiet` flag is always effective, avoid using simple `print` statements. Instead, use the purpose-built `usethis._console.plain_print` function.

### Branding

The usethis name should not be capitalized (i.e. not Usethis or UseThis), even at the
beginning of a sentence. It should only be styled in monospace as `usethis` when referring to the command itself.

These colours are used in branding materials:

- Green: #00c000
- Orange: #f26622
- Grey: #999999
- Darker Grey: #424242

Along with the fonts [EB Garamond](https://fonts.google.com/specimen/EB+Garamond) and [Cairo](https://fonts.google.com/specimen/Cairo).

## Guides

### Adding a new badge

To add a new `usethis badge` interface, follow these steps:

- Define a `get_<badge_name>_badge` function in <src\usethis\_core\badge.py>. Try to keep the definitions in alphabetical order.
- Declare the interface in <src\usethis\_ui\interface\badge.py>. Again, keep the declarations in alphabetical order. The pattern is basically just boilerplate with the other interfaces, but you need to give a description of your command for the `--help` option.
- Add a test for your badge in <tests\usethis\_ui\interface\test_interface_badge.py>. Follow the pattern of the existing tests, although you only need the `test_add` case, which simply tests that the command runs without error.
- Declare a recommended badge placement in the `get_badge_order` function in <src\usethis\_core\badge.py>. This helps ensure the badges are arranged in an opinionated way relative to existing badges.

Finally, run the command on this project, to make sure the badge gets inserted correctly with valid Markdown syntax. Check it renders successfully and that any hyperlink works as expected.

## License

By contributing, you agree that your contributions will be licensed under the MIT license. See the [LICENSE](https://github.com/usethis-python/usethis-python/blob/main/LICENSE) file.
