import subprocess
from collections import Counter
from pathlib import Path

import ruamel.yaml
from ruamel.yaml.util import load_yaml_guess_indent

from usethis import console
from usethis._deptry.core import PRE_COMMIT_NAME as DEPTRY_PRE_COMMIT_NAME
from usethis._git import _get_github_latest_tag, _GitHubTagError
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
    DEPTRY_PRE_COMMIT_NAME,
]


def make_pre_commit_config() -> None:
    console.print("✔ Creating .pre-commit-config.yaml file", style="green")
    try:
        pkg_version = _get_github_latest_tag("abravalheri", "validate-pyproject")
    except _GitHubTagError:
        # Fallback to last known working version
        pkg_version = _VALIDATEPYPROJECT_VERSION
    yaml_contents = _YAML_CONTENTS_TEMPLATE.format(pkg_version=pkg_version)

    (Path.cwd() / ".pre-commit-config.yaml").write_text(yaml_contents)


def delete_hook(name: str) -> None:
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


def add_single_hook(config: PreCommitRepoConfig) -> None:
    # We should have a canonical sort order for all usethis-supported hooks to decide where to place the section. The main objective with the sort order is to ensure dependency relationships are satisfied. For example, valdiate-pyproject will check if the pyproject.toml is valid - if it isn't then some later tools might fail. It would be better to catch this earlier. A general principle is to move from the simpler hooks to the more complicated. Of course, this order might already be violated, or the config might include unrecognized repos - in any case, we aim to ensure the new tool is configured correctly, so it should be placed after the last of its precedents. This logic can be encoded in the adding function.

    path = Path.cwd() / ".pre-commit-config.yaml"

    with path.open(mode="r") as f:
        content, sequence_ind, offset_ind = load_yaml_guess_indent(f)

    yaml = ruamel.yaml.YAML(typ="rt")
    yaml.indent(mapping=sequence_ind, sequence=sequence_ind, offset=offset_ind)

    (hook_config,) = config.hooks
    hook_name = hook_config.id

    # Get an ordered list of the hooks already in the file
    existing_hooks = get_hook_names(path.parent)

    # Get the precendents, i.e. hooks occuring before the new hook
    hook_idx = _HOOK_ORDER.index(hook_name)
    if hook_idx == -1:
        raise ValueError(f"Hook {hook_name} not recognized")
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
