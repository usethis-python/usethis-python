import subprocess
from collections import Counter
from pathlib import Path

import ruamel.yaml
from ruamel.yaml.util import load_yaml_guess_indent

from usethis import console
from usethis._github import GitHubTagError, get_github_latest_tag
from usethis._pre_commit.config import PreCommitRepoConfig

_YAML_CONTENTS_TEMPLATE = """
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: "{pkg_version}"
    hooks:
      - id: validate-pyproject
        additional_dependencies: ["validate-pyproject-schema-store[all]"]
"""
# Manually bump this version when necessary
_VALIDATEPYPROJECT_VERSION = "v0.21"

_HOOK_ORDER = [
    "validate-pyproject",
    "ruff-format",
    "ruff-check",
    "deptry",
]


def ensure_pre_commit_config() -> None:
    if (Path.cwd() / ".pre-commit-config.yaml").exists():
        # Early exit; the file already exists
        return

    console.print("✔ Creating .pre-commit-config.yaml file", style="green")
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

    console.print("✔ Removing .pre-commit-config.yaml file", style="green")
    (Path.cwd() / ".pre-commit-config.yaml").unlink()


def add_hook(config: PreCommitRepoConfig) -> None:
    path = Path.cwd() / ".pre-commit-config.yaml"

    with path.open(mode="r") as f:
        content, sequence_ind, offset_ind = load_yaml_guess_indent(f)

    yaml = ruamel.yaml.YAML(typ="rt")
    yaml.indent(mapping=sequence_ind, sequence=sequence_ind, offset=offset_ind)

    (hook_config,) = config.hooks
    hook_name = hook_config.id

    # Get an ordered list of the hooks already in the file
    existing_hooks = get_hook_names(path.parent)

    if not existing_hooks:
        raise NotImplementedError

    # Get the precendents, i.e. hooks occuring before the new hook
    try:
        hook_idx = _HOOK_ORDER.index(hook_name)
    except ValueError:
        raise NotImplementedError(f"Hook '{hook_name}' not recognized")
    precedents = _HOOK_ORDER[:hook_idx]

    # Find the last of the precedents in the existing hooks
    existings_precedents = [hook for hook in existing_hooks if hook in precedents]
    if existings_precedents:
        last_precedent = existings_precedents[-1]
    else:
        # Use the last existing hook
        last_precedent = existing_hooks[-1]

    # Insert the new hook after the last precedent repo
    # Do this by iterating over the repos and hooks, and inserting the new hook after
    # the last precedent
    new_repos = []
    for repo in content["repos"]:
        new_repos.append(repo)
        for hook in repo["hooks"]:
            if hook["id"] == last_precedent:
                new_repos.append(config.model_dump(exclude_none=True))
    content["repos"] = new_repos

    # Dump the new content
    yaml.dump(content, path)


def remove_hook(name: str) -> None:
    path = Path.cwd() / ".pre-commit-config.yaml"

    with path.open(mode="r") as f:
        content, sequence_ind, offset_ind = load_yaml_guess_indent(f)

    yaml = ruamel.yaml.YAML(typ="rt")
    yaml.indent(mapping=sequence_ind, sequence=sequence_ind, offset=offset_ind)

    # search across the repos for any hooks with ID equal to name
    for repo in content["repos"]:
        for hook in repo["hooks"]:
            if hook["id"] == name:
                repo["hooks"].remove(hook)

        # if repo has no hooks, remove it
        if not repo["hooks"]:
            content["repos"].remove(repo)

    yaml.dump(content, path)


def get_hook_names(path: Path) -> list[str]:
    yaml = ruamel.yaml.YAML()
    with (path / ".pre-commit-config.yaml").open(mode="r") as f:
        content = yaml.load(f)

    hook_names = []
    for repo in content["repos"]:
        for hook in repo["hooks"]:
            hook_names.append(hook["id"])

    # Need to validate there are no duplciates
    for name, count in Counter(hook_names).items():
        if count > 1:
            raise DuplicatedHookNameError(f"Hook name '{name}' is duplicated")

    return hook_names


class DuplicatedHookNameError(ValueError):
    """Raised when a hook name is duplicated in a pre-commit configuration file."""


def install_pre_commit() -> None:
    console.print("✔ Installing pre-commit hooks", style="green")
    subprocess.run(
        ["uv", "run", "pre-commit", "install"],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def uninstall_pre_commit() -> None:
    console.print("✔ Uninstalling pre-commit hooks", style="green")
    subprocess.run(
        ["uv", "run", "pre-commit", "uninstall"],
        check=True,
        stdout=subprocess.DEVNULL,
    )
