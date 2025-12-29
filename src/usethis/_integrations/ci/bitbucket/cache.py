from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._console import tick_print
from usethis._integrations.ci.bitbucket.init import (
    ensure_bitbucket_pipelines_config_exists,
)
from usethis._integrations.ci.bitbucket.schema import Definitions
from usethis._integrations.ci.bitbucket.yaml import BitbucketPipelinesYAMLManager

if TYPE_CHECKING:
    from usethis._integrations.ci.bitbucket.schema import Cache, PipelinesConfiguration


def get_cache_by_name() -> dict[str, Cache]:
    mgr = BitbucketPipelinesYAMLManager()
    config = mgr.model_validate()

    if config.definitions is None:
        return {}

    cache_by_name = config.definitions.caches

    if cache_by_name is None:
        return {}

    return cache_by_name


def add_caches(cache_by_name: dict[str, Cache]) -> None:
    ensure_bitbucket_pipelines_config_exists()

    mgr = BitbucketPipelinesYAMLManager()
    model = mgr.model_validate()
    _add_caches_via_model(cache_by_name, model=model)
    mgr.commit_model(model)


def _add_caches_via_model(
    cache_by_name: dict[str, Cache], *, model: PipelinesConfiguration
) -> None:
    if model.definitions is None:
        model.definitions = Definitions()
    if model.definitions.caches is None:
        model.definitions.caches = {}

    for name, cache in cache_by_name.items():
        if not _cache_exists(name, model=model):
            tick_print(
                f"Adding cache '{name}' definition to 'bitbucket-pipelines.yml'."
            )
            model.definitions.caches[name] = cache


def remove_cache(cache: str) -> None:
    mgr = BitbucketPipelinesYAMLManager()
    model = mgr.model_validate()

    if model.definitions is None or model.definitions.caches is None:
        return

    if cache in model.definitions.caches:
        tick_print(
            f"Removing cache '{cache}' definition from 'bitbucket-pipelines.yml'."
        )
        del model.definitions.caches[cache]

        # Remove an empty caches section
        if not model.definitions.caches:
            del model.definitions.caches

    mgr.commit_model(model)


def _cache_exists(name: str, *, model: PipelinesConfiguration) -> bool:
    if model.definitions is None or model.definitions.caches is None:
        return False

    return name in model.definitions.caches
