from collections import Counter
from pathlib import Path

from ruamel.yaml.comments import CommentedMap

from usethis._config import usethis_config
from usethis._console import tick_print
from usethis._integrations.pre_commit.config import HookConfig, PreCommitRepoConfig
from usethis._integrations.yaml.io import edit_yaml

_HOOK_ORDER = [
    "validate-pyproject",
    "pyproject-fmt",
    "ruff-format",
    "ruff-check",
    "deptry",
]


class DuplicatedHookNameError(ValueError):
    """Raised when a hook name is duplicated in a pre-commit configuration file."""


def add_hook(config: PreCommitRepoConfig) -> None:
    # TODO docstring. Need to mention that this function assumes the hook doesn't
    # already exist
    # TODO in general need a convention around "add" versus "ensure", "use", etc.
    # which indicates whether we assume the hook already exists or not.
    path = Path.cwd() / ".pre-commit-config.yaml"

    is_first_hook = not path.exists()
    if is_first_hook:
        tick_print("Writing '.pre-commit-config.yaml'.")
        # This might seem pointless, but it is to give the ruamel.yaml indention guesser
        # an idea of the indentation level we'd like by default.
        # TODO instead of this, edit_yaml should accept a bool "guess_indent: bool = True"
        # which we would set to False for first hook = True
        path.write_text("""\
repos:
  - repo: local
""")

    with edit_yaml(path) as doc:
        if is_first_hook:
            doc.content = CommentedMap({})
        # TODO need to remove placeholder hook if present and test

        # TODO test the case where we try to add a hook of the same name that already
        # exists. Related to above docstring and naming convention issue.
        content = doc.content
        if not isinstance(content, CommentedMap):
            msg = f"Unrecognized pre-commit configuration file format of type {type(content)}"
            raise NotImplementedError(msg)

        (hook_config,) = (
            config.hooks
        )  # TODO Weird assumption! Should allow multiple hooks per repo config.
        hook_name = hook_config.id

        # Get an ordered list of the hooks already in the file
        existing_hooks = get_hook_names()

        if not existing_hooks:
            # TODO duplicated message.
            tick_print(f"Adding hook '{hook_name}' to '.pre-commit-config.yaml'.")
            if "repos" not in content:
                content["repos"] = []
            content["repos"].append(config.model_dump(exclude_none=True))
            return

        # Get the precendents, i.e. hooks occuring before the new hook
        try:
            hook_idx = _HOOK_ORDER.index(hook_name)
        except ValueError:
            msg = f"Hook '{hook_name}' not recognized"
            raise NotImplementedError(msg)
        precedents = _HOOK_ORDER[:hook_idx]

        # Find the last of the precedents in the existing hooks
        existings_precedents = [hook for hook in existing_hooks if hook in precedents]
        if existings_precedents:
            last_precedent = existings_precedents[-1]
        else:
            # Use the last existing hook
            last_precedent = existing_hooks[-1]

        # Insert the new hook after the last precedent repo
        # Do this by iterating over the repos and hooks, and inserting the new hook
        # after the last precedent
        new_repos = []
        for repo in content["repos"]:
            # TODO shouldn't use model_dump because of inconistent handling of defaults
            # should use some kind of dict subset approach. Need internet to think about
            # this properly. So test the edge cases.
            if repo != _get_placeholder_repo_config().model_dump(exclude_defaults=True):
                new_repos.append(repo)
            for hook in repo["hooks"]:
                # TODO Also need to think about this precedent logic in terms of how
                # it handles repos - there might be other hooks in-between from the same
                # repo as the one we are adding, in which case we are "giving up" on
                # keeping precedent order so nicely.
                # Maybe the solution is that precedent order is in a repo:hook pair, not
                # just a hook. more thought needed.

                if hook["id"] == last_precedent:
                    # TODO check this shouldn't be a fancy model dump that chooses
                    # sensible key order automatically
                    # TODO Test this message; it was probably wrong before.
                    tick_print(
                        f"Adding hook '{hook_name}' to '.pre-commit-config.yaml'."
                    )
                    new_repos.append(config.model_dump(exclude_none=True))
        content["repos"] = new_repos


def add_placeholder_hook() -> None:
    # print statement is duplicated...
    tick_print("Writing '.pre-commit-config.yaml'.")
    with usethis_config.set(quiet=True):
        add_hook(_get_placeholder_repo_config())
    # TODO message and test for need to replace placeholder - c.f. BBPL msg


def _get_placeholder_repo_config() -> PreCommitRepoConfig:
    # TODO there might be a pre-commit repo already existent which purely does
    # placeholder activity - we should consider it.
    # On the other hand, local prevents downloads & versions which complicates
    # things, so maybe this is good.
    return PreCommitRepoConfig(
        repo="local",
        hooks=[
            HookConfig(
                id="placeholder",
                name="Placeholder - add your own hooks!",
                entry="uv run python -V",  # TODO better to do hello world.
                language="python",
            )
        ],
    )


def remove_hook(name: str) -> None:
    """Remove pre-commit hook configuration.

    If the hook doesn't exist, this function will have no effect.
    """
    # TODO similar to above discussion. Need a naming convention
    # to reflect this difference in assumption: remove vs. drop perhaps? For assuming
    # that the hook isn't already removed.
    path = Path.cwd() / ".pre-commit-config.yaml"

    with edit_yaml(path) as yaml_document:
        content = yaml_document.content
        if not isinstance(content, CommentedMap):
            msg = f"Unrecognized pre-commit configuration file format of type {type(content)}"
            raise NotImplementedError(msg)

        # search across the repos for any hooks with ID equal to name
        for repo in content["repos"]:
            for hook in repo["hooks"]:
                if hook["id"] == name:
                    tick_print(
                        f"Removing {hook["id"]} config from '.pre-commit-config.yaml'."
                    )
                    repo["hooks"].remove(hook)

            # if repo has no hooks, remove it
            # TODO we shouldn't remove it if we haven't touched the repo, we should be
            # minimizing the diff. Need to test this.
            if not repo["hooks"]:
                content["repos"].remove(repo)

    # TODO but what if there's no hooks left at all? Should we delete the file?


# TODO look at places where we use the fast read-in functions: we should make sure that
# in such cases it is not possible to call the function concurrently with a context
# manager (concurrent reads). It's not obvious how we'd achieve this anyway.


def get_hook_names() -> list[str]:
    path = Path.cwd() / ".pre-commit-config.yaml"

    if not path.exists():
        return []

    with edit_yaml(path) as yaml_document:
        # TODO duplication with above - should have a new abstraction specifically
        # edit_precommit_yaml
        content = yaml_document.content
        if not isinstance(content, CommentedMap):
            msg = f"Unrecognized pre-commit configuration file format of type {type(content)}"
            raise NotImplementedError(msg)

        return extract_hook_names(content)


def extract_hook_names(cmap: CommentedMap) -> list[str]:
    if cmap is None:
        return []

    hook_names = []
    for repo in cmap["repos"]:
        if "hooks" not in repo:
            continue

        for hook in repo["hooks"]:
            hook_names.append(hook["id"])

    # Need to validate there are no duplciates
    for name, count in Counter(hook_names).items():
        if count > 1:
            msg = f"Hook name '{name}' is duplicated"
            raise DuplicatedHookNameError(msg)

    return hook_names
