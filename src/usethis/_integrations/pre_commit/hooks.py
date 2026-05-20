"""Pre-commit hook addition and removal."""

from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._config import usethis_config
from usethis._console import instruct_print, tick_print
from usethis._file.yaml.io_ import YAMLDocument
from usethis._integrations.pre_commit import schema
from usethis._integrations.pre_commit.init import (
    ensure_pre_commit_config_exists,
)
from usethis._integrations.pre_commit.language import get_system_language
from usethis._integrations.pre_commit.yaml import PreCommitConfigYAMLManager
from usethis._integrations.pydantic.dump import fancy_model_dump
from usethis._pipeweld.containers import series
from usethis._pipeweld.func import Adder, get_predecessor

if TYPE_CHECKING:
    from collections.abc import Collection

HOOK_GROUPS: list[list[str]] = [
    [
        "sync-with-uv",
        "validate-pyproject",
        "uv-export",
        "pyproject-fmt",
        "ruff",  # Alias used for ruff-check
        "ruff-check",  # ruff-check followed by ruff-format seems to be the recommended way by Astral
    ],
    [
        "ruff-format",
    ],
    [
        "ty",
        "deptry",
        "lint_imports",  # Alias used for import-linter used in the Import Linter docs, see https://github.com/usethis-python/usethis-python/issues/1022
        "import-linter",
        "tach",
        "codespell",
    ],
]

_PLACEHOLDER_ID = "placeholder"


def add_repo(repo: schema.LocalRepo | schema.UriRepo) -> None:
    """Add a pre-commit repo configuration to the pre-commit configuration file.

    This assumes the hook doesn't already exist in the configuration file.
    """
    ensure_pre_commit_config_exists()

    mgr = PreCommitConfigYAMLManager()
    model = mgr.model_validate()

    if repo.hooks is None or len(repo.hooks) != 1:
        msg = "Currently, only repos with exactly one hook are supported."
        raise NotImplementedError(msg)  # Should allow multiple or 0 hooks per repo

    (hook_config,) = repo.hooks

    if hook_config.id is None:
        msg = "The hook ID must be specified."
        raise ValueError(msg)

    # Ordered list of the hooks already in the file
    existing_hooks = extract_hook_ids(model)

    if not existing_hooks:
        if hook_ids_are_equivalent(hook_config.id, _PLACEHOLDER_ID):
            tick_print("Adding placeholder hook to '.pre-commit-config.yaml'.")
        else:
            tick_print(f"Adding hook '{hook_config.id}' to '.pre-commit-config.yaml'.")

        repo_dict = fancy_model_dump(repo, reference={}, order_by_cls={})
        mgr.extend_list(keys=["repos"], values=[repo_dict])
    else:
        # There are existing hooks so we need to know where to insert the new hook.
        # Use pipeweld to determine the correct insertion position based on the
        # canonical hook ordering.
        hook_order = [hook for group in HOOK_GROUPS for hook in group]
        try:
            hook_idx = hook_order.index(hook_config.id)
        except ValueError:
            msg = f"Hook '{hook_config.id}' is not recognized."
            raise NotImplementedError(msg) from None

        prerequisites = set(hook_order[:hook_idx])
        postrequisites = set(hook_order[hook_idx + 1 :])

        pipeline = series(*existing_hooks)
        adder = Adder(
            pipeline=pipeline,
            step=hook_config.id,
            prerequisites=prerequisites,
            postrequisites=postrequisites,
            force_linear=True,
        )
        result = adder.add()

        predecessor = get_predecessor(result.solution, hook_config.id)

        # Find the insertion index and surgically insert/remove placeholder.
        yaml_doc = mgr.get()
        doc = yaml_doc.doc

        insert_idx, placeholder_idx = _find_insert_position(
            model.repos, predecessor
        )

        # Remove the placeholder if present (adjust insert index accordingly).
        if placeholder_idx is not None:
            repo_dict_to_remove = doc["repos", placeholder_idx]
            doc = doc.remove_from_list("repos", values=[repo_dict_to_remove])
            if placeholder_idx < insert_idx:
                insert_idx -= 1

        _report_adding_repo(repo)
        repo_dict = fancy_model_dump(repo, reference={}, order_by_cls={})

        # If the list is now empty (e.g. placeholder was the only item),
        # use upsert since insert_at requires an existing sequence.
        remaining = doc["repos"]
        if not remaining:
            doc = doc.upsert("repos", value=[repo_dict])
        else:
            doc = doc.insert("repos", index=insert_idx, value=repo_dict)
        mgr.commit(YAMLDocument(doc=doc))


def _find_insert_position(
    repos: Collection[schema.LocalRepo | schema.UriRepo | schema.MetaRepo],
    predecessor: str | None,
) -> tuple[int, int | None]:
    """Find the insertion index and optional placeholder index.

    Returns:
        A tuple of (insert_index, placeholder_index_or_None).
    """
    placeholder_idx: int | None = None
    insert_idx = 0  # Default: insert at the beginning

    for i, existing_repo in enumerate(repos):
        existing_hooks = existing_repo.hooks or []

        # Track the placeholder repo.
        if (
            len(existing_hooks) == 1
            and hook_ids_are_equivalent(existing_hooks[0].id, _PLACEHOLDER_ID)
        ):
            placeholder_idx = i

        if predecessor is None:
            # No predecessor means insert at position 0.
            continue

        # Check if this repo contains the predecessor hook.
        for hook in existing_hooks:
            if hook_ids_are_equivalent(hook.id, predecessor):
                insert_idx = i + 1

    return insert_idx, placeholder_idx


def insert_repo(
    *,
    repo_to_insert: schema.LocalRepo | schema.UriRepo | schema.MetaRepo,
    existing_repos: Collection[schema.LocalRepo | schema.UriRepo | schema.MetaRepo],
    predecessor: str | None,
) -> list[schema.LocalRepo | schema.UriRepo | schema.MetaRepo]:
    """Insert a repo into the list of repos after the named predecessor hook."""
    # Insert the new hook after the last precedent repo
    # Do this by iterating over the repos and hooks, and inserting the new hook
    # after the last precedent
    inserted = False
    repos: list[schema.LocalRepo | schema.UriRepo | schema.MetaRepo] = []

    if predecessor is None:
        # If there is no predecessor, we can just append the new repo
        _report_adding_repo(repo_to_insert)
        repos.append(repo_to_insert)
        inserted = True

    for existing_repo in existing_repos:
        existing_hooks = existing_repo.hooks
        if existing_hooks is None:
            existing_hooks = []

        # Add the existing repos, because they need to be in the final list too!
        # One exception is that we don't include the placeholder from now on, since
        # we're adding a repo which can be there instead.
        # One exception to _that_ is if the user has intentionally kept the placeholder,
        # i.e. there are multiple hooks; in that case we will not remove it.
        if not (
            len(existing_hooks) == 1
            and hook_ids_are_equivalent(existing_hooks[0].id, _PLACEHOLDER_ID)
        ):
            repos.append(existing_repo)

        # If we have already inserted the new repo, we're done.
        if inserted:
            continue

        # Otherwise, we need to search through this existing repo we've reached to see
        # if it's the earliest found predecessor. If so, we're done.
        for hook in existing_hooks:
            if hook_ids_are_equivalent(hook.id, predecessor):
                _report_adding_repo(repo_to_insert)
                repos.append(repo_to_insert)
                inserted = True

    return repos


def _report_adding_repo(
    repo: schema.LocalRepo | schema.UriRepo | schema.MetaRepo,
) -> None:
    """Append a repo to the end of the existing repos with message."""
    if repo.hooks is not None:
        for inserted_hook in repo.hooks:
            tick_print(
                f"Adding hook '{inserted_hook.id}' to '.pre-commit-config.yaml'."
            )


def add_placeholder_hook() -> None:
    """Add a placeholder hook to the pre-commit configuration with instructions for the user."""
    add_repo(_get_placeholder_repo_config())
    instruct_print("Remove the placeholder hook in '.pre-commit-config.yaml'.")
    instruct_print("Replace it with your own hooks.")
    instruct_print(
        "Alternatively, use 'usethis tool' to add other tools and their hooks."
    )


def _get_placeholder_repo_config() -> schema.LocalRepo:
    return schema.LocalRepo(
        repo="local",
        hooks=[
            schema.HookDefinition(
                id=_PLACEHOLDER_ID,
                name="Placeholder - add your own hooks!",
                entry="""uv run --isolated --frozen --offline python -c "print('hello world!')\"""",
                language=get_system_language(),
            )
        ],
    )


def remove_hook(hook_id: str) -> None:
    """Remove pre-commit hook configuration.

    If the hook doesn't exist, this function will have no effect. Meta hooks are
    ignored.
    """
    ensure_pre_commit_config_exists()

    mgr = PreCommitConfigYAMLManager()
    model = mgr.model_validate()

    # Work directly with the yamltrip document for surgical removal that
    # preserves comments and formatting.
    yaml_doc = mgr.get()
    doc = yaml_doc.doc
    raw_repos: list[dict] = doc["repos"] or []

    # Iterate in reverse so index shifts from removal don't affect later indices.
    for i in range(len(model.repos) - 1, -1, -1):
        repo = model.repos[i]
        if isinstance(repo, schema.MetaRepo) or repo.hooks is None:
            continue

        hooks_to_remove = [
            raw_repos[i]["hooks"][j]
            for j, hook in enumerate(repo.hooks)
            if hook_ids_are_equivalent(hook.id, hook_id)
        ]

        for hook_dict in hooks_to_remove:
            hook_display_id = hook_dict.get("id", hook_id)
            tick_print(
                f"Removing hook '{hook_display_id}' from '.pre-commit-config.yaml'."
            )
            doc = doc.remove_from_list("repos", i, "hooks", values=[hook_dict])

        if hooks_to_remove and len(repo.hooks) == len(hooks_to_remove):
            # All hooks removed — remove the entire repo entry.
            repo_dict = doc["repos"][i]
            doc = doc.remove_from_list("repos", values=[repo_dict])

    # If no repos remain, add a placeholder.
    remaining_repos = doc["repos"]
    if not remaining_repos:
        placeholder = fancy_model_dump(
            _get_placeholder_repo_config(), reference={}, order_by_cls={}
        )
        doc = doc.upsert("repos", value=[placeholder])

    mgr.commit(YAMLDocument(doc=doc))


def get_hook_ids() -> list[str]:
    """Get the list of hook IDs currently configured in the pre-commit configuration file."""
    path = usethis_config.cpd() / ".pre-commit-config.yaml"

    if not path.exists():
        return []

    mgr = PreCommitConfigYAMLManager()
    model = mgr.model_validate()
    return extract_hook_ids(model)


def extract_hook_ids(
    model: schema.JsonSchemaForPreCommitConfigYaml,
) -> list[str]:
    """Extract all hook IDs from a pre-commit configuration model."""
    hook_ids: list[str] = []
    for repo in model.repos:
        if repo.hooks is None:
            continue

        for hook in repo.hooks:
            if hook.id is not None:
                hook_ids.append(hook.id)

    return hook_ids


def hook_ids_are_equivalent(hook_id: str | None, other: str | None) -> bool:
    """Check if two hook IDs are equivalent."""
    # Same name
    if hook_id == other:
        return True

    # Same name up to case differences
    if isinstance(hook_id, str) and isinstance(other, str):
        hook_id_str = hook_id.lower()
        other_str = other.lower()
        if hook_id_str == other_str:
            return True
        if {hook_id_str, other_str} == {"ruff", "ruff-check"}:
            return True

    return False
