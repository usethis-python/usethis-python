from pathlib import Path

from usethis._console import tick_print
from usethis._integrations.github.tags import GitHubTagError, get_github_latest_tag
from usethis._integrations.uv.call import call_subprocess

_YAML_CONTENTS_TEMPLATE = """\
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: "{pkg_version}"
    hooks:
      - id: validate-pyproject
        additional_dependencies: ["validate-pyproject-schema-store[all]"]
"""
# Manually bump this version when necessary
_VALIDATEPYPROJECT_VERSION = "v0.22"


def add_pre_commit_config() -> None:
    if (Path.cwd() / ".pre-commit-config.yaml").exists():
        # Early exit; the file already exists
        return

    tick_print("Writing '.pre-commit-config.yaml'.")
    try:
        pkg_version = get_github_latest_tag("abravalheri", "validate-pyproject")
    except GitHubTagError:
        # Fallback to last known working version
        pkg_version = _VALIDATEPYPROJECT_VERSION
    yaml_contents = _YAML_CONTENTS_TEMPLATE.format(pkg_version=pkg_version)

    (Path.cwd() / ".pre-commit-config.yaml").write_text(yaml_contents)


def remove_pre_commit_config() -> None:
    if not (Path.cwd() / ".pre-commit-config.yaml").exists():
        # Early exit; the file already doesn't exist
        return

    tick_print("Removing .pre-commit-config.yaml file.")
    (Path.cwd() / ".pre-commit-config.yaml").unlink()


def install_pre_commit() -> None:
    tick_print("Ensuring pre-commit hooks are installed.")
    call_subprocess(["uv", "run", "pre-commit", "install"])


def uninstall_pre_commit() -> None:
    tick_print("Ensuring pre-commit hooks are uninstalled.")
    call_subprocess(["uv", "run", "pre-commit", "uninstall"])
