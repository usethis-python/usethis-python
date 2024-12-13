from collections import Counter
from pathlib import Path

from usethis._console import box_print, tick_print
from usethis._integrations.pre_commit.dump import precommit_fancy_dump
from usethis._integrations.pre_commit.io import edit_pre_commit_config_yaml
from usethis._integrations.pre_commit.schema import (
    HookDefinition,
    JsonSchemaForPreCommitConfigYaml,
    Language,
    LocalRepo,
    MetaRepo,
    UriRepo,
)
from usethis._integrations.pydantic.dump import fancy_model_dump
from usethis._integrations.yaml.update import update_ruamel_yaml_map

_HOOK_ORDER = [
    "validate-pyproject",
    "pyproject-fmt",
    "ruff",  # ruff followed by ruff-format seems to be the recommended way by Astral
    "ruff-format",
    "deptry",
]


class DuplicatedHookNameError(ValueError):
    """Raised when a hook name is duplicated in a pre-commit configuration file."""


# TODO refactor to avoid complexity and enable the below ruff rule
def add_repo(repo: LocalRepo | UriRepo) -> None:  # noqa: PLR0912
    """Add a pre-commit repo configuration to the pre-commit configuration file.

    This assumes the hook doesn't already exist in the configuration file.
    """
    # TODO in general need a convention around "add" versus "ensure", "use", etc.
    # which indicates whether we assume the hook already exists or not.
    # TODO this function should use the classes.

    with edit_pre_commit_config_yaml() as doc:
        if repo.hooks is None or len(repo.hooks) != 1:
            msg = "Currently, only repos with exactly one hook are supported."
            raise NotImplementedError(msg)  # Should allow multiple or 0 hooks per repo

        (hook_config,) = repo.hooks
        hook_name = hook_config.id

        if hook_name is None:
            msg = "Hook ID must be specified"
            raise ValueError(msg)

        # Ordered list of the hooks already in the file
        existing_hooks = extract_hook_names(doc.model)

        if not existing_hooks:
            if hook_name == "placeholder":
                tick_print("Adding placeholder hook to '.pre-commit-config.yaml'.")
            else:
                tick_print(f"Adding hook '{hook_name}' to '.pre-commit-config.yaml'.")

            doc.model.repos.append(repo)
        else:
            # Get the precendents, i.e. hooks occuring before the new hook
            try:
                hook_idx = _HOOK_ORDER.index(hook_name)
            except ValueError:
                msg = f"Hook '{hook_name}' not recognized"
                raise NotImplementedError(msg)
            precedents = _HOOK_ORDER[:hook_idx]

            # Find the last of the precedents in the existing hooks
            existings_precedents = [
                hook for hook in existing_hooks if hook in precedents
            ]
            if existings_precedents:
                last_precedent = existings_precedents[-1]
            else:
                # Use the last existing hook
                last_precedent = existing_hooks[-1]

            # Insert the new hook after the last precedent repo
            # Do this by iterating over the repos and hooks, and inserting the new hook
            # after the last precedent
            new_repos = []
            for _repo in doc.model.repos:
                # TODO shouldn't hard-code placeholder, should reference the placeholder
                # function's hard-coded value.
                # Also need to move these dicts to pydamtic classes.
                hooks = _repo.hooks
                if hooks is None:
                    hooks = []

                # Check consistency in the way we handle placeholders - are they
                # automatically removed once we have a way to do so?
                if [hook.id for hook in hooks] != ["placeholder"]:
                    new_repos.append(_repo)
                for hook in hooks:
                    # TODO Also need to think about this precedent logic in terms of how
                    # it handles repos - there might be other hooks in-between from the same
                    # repo as the one we are adding, in which case we are "giving up" on
                    # keeping precedent order so nicely.
                    # Maybe the solution is that precedent order is in a repo:hook pair, not
                    # just a hook. more thought needed.

                    if hook.id == last_precedent:
                        # TODO check this shouldn't be a fancy model dump that chooses
                        # sensible key order automatically
                        # TODO Test this message; it was probably wrong before.
                        # TODO this message should have an if-statement style exception
                        tick_print(
                            f"Adding hook '{hook_name}' to '.pre-commit-config.yaml'."
                        )
                        # TODO should have a wrapper around fancy_model_dump.
                        # should ctrl-f to find all instances of raw fancy_model_dump and
                        # ensure they are all wrapped
                        new_repos.append(fancy_model_dump(repo))
            doc.model.repos = new_repos

        update_ruamel_yaml_map(
            doc.content,
            precommit_fancy_dump(doc.model, reference=doc.content),
            preserve_comments=True,
        )


def add_placeholder_hook() -> None:
    add_repo(_get_placeholder_repo_config())
    box_print("Remove the placeholder hook in '.pre-commit-config.yaml'.")
    box_print("Replace it with your own hooks.")
    box_print("Alternatively, use 'usethis tool' to add other tools and their hooks.")


def _get_placeholder_repo_config() -> LocalRepo:
    # TODO there might be a pre-commit repo already existent which purely does
    # placeholder activity - we should consider it.
    # On the other hand, local prevents downloads & versions which complicates
    # things, so maybe this is good.
    return LocalRepo(
        repo="local",
        hooks=[
            HookDefinition(
                id="placeholder",
                name="Placeholder - add your own hooks!",
                entry="""uv run python -c "print('hello world!')\"""",
                language=Language("python"),
            )
        ],
    )


def remove_hook(name: str) -> None:
    """Remove pre-commit hook configuration.

    If the hook doesn't exist, this function will have no effect. Meta hooks are
    ignored.
    """
    # TODO similar to above discussion. Need a naming convention
    # to reflect this difference in assumption: remove vs. drop perhaps? For assuming
    # that the hook isn't already removed.
    with edit_pre_commit_config_yaml() as doc:
        # TODO we should use the pydantic schema + update function rather than
        # directly over-writing dictionaries.

        # search across the repos for any hooks with ID equal to name
        for repo in doc.model.repos:
            if isinstance(repo, MetaRepo) or repo.hooks is None:
                continue

            for hook in repo.hooks:
                if hook.id == name:
                    tick_print(
                        f"Removing {hook.id} config from '.pre-commit-config.yaml'."
                    )
                    repo.hooks.remove(hook)

            # if repo has no hooks, remove it
            # TODO we shouldn't remove it if we haven't touched the repo, we should be
            # minimizing the diff. Need to test this.
            if not repo.hooks:
                doc.model.repos.remove(repo)

        # If there are no more hooks, we should add a placeholder.
        if not doc.model.repos:
            doc.model.repos.append(_get_placeholder_repo_config())

        # TODO both here and for BBPL we should consider having update_ruamel_yaml_map
        # layer than takes a doc from the context manager and does the update with
        # correct fancy dumping. And maybe should be built-in to the context managers??
        dump = precommit_fancy_dump(doc.model, reference=doc.content)
        update_ruamel_yaml_map(doc.content, dump, preserve_comments=True)

    # TODO but what if there's no hooks left at all? Should we delete the file?


def get_hook_names() -> list[str]:
    path = Path.cwd() / ".pre-commit-config.yaml"

    if not path.exists():
        return []

    with edit_pre_commit_config_yaml() as doc:
        return extract_hook_names(doc.model)


def extract_hook_names(model: JsonSchemaForPreCommitConfigYaml) -> list[str]:
    hook_names = []
    for repo in model.repos:
        if repo.hooks is None:
            continue

        for hook in repo.hooks:
            hook_names.append(hook.id)

    # Need to validate there are no duplciates
    for name, count in Counter(hook_names).items():
        if count > 1:
            msg = f"Hook name '{name}' is duplicated"
            raise DuplicatedHookNameError(msg)

    return hook_names
