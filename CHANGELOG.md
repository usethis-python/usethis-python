# Changelog

## 0.11.0

### 🚀 New Features

- This release adds a new `--show` option to the `usethis badge` interface. This option will display the badge as markdown output without adding it to the README file.

- The latest version of the Bitbucket Pipelines configuration file schema is now supported, specifically support for new options available regarding artifact uploads.

### 🐞 Bug Fixes

- The `--quiet` option did not properly suppress output when displaying warnings associated with failed README parsing in `usethis badge`. This has been fixed.

- Due to a breaking change in Click v8.2.0, Click is now declared as a direct dependency temporarily until the ramifications can be addressed in Typer. The lower bound is declared as `>=8.0.0` and the constraint `!=8.2.0` to avoid the breaking change. For more information, see [here](https://github.com/fastapi/typer/discussions/1215).

### 📚 Documentation

There have been various improvements to the documentation, especially the contribution guide.

### 🔧 Internal Changes

Minor improvements to the CI configuration have been made; the CI will no longer trigger for changes to markdown files only, and `--break-system-packages` is no longer used.

## 0.10.0

This is the first Alpha release of usethis. Releases up to this point do not have
a changelog recorded against them.
