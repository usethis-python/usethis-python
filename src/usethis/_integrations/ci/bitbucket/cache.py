from __future__ import annotations

from typing import TYPE_CHECKING

from usethis._console import tick_print
from usethis._integrations.ci.bitbucket.dump import bitbucket_fancy_dump
from usethis._integrations.ci.bitbucket.io_ import (
    edit_bitbucket_pipelines_yaml,
)
from usethis._integrations.ci.bitbucket.schema import Definitions
from usethis._integrations.file.yaml.update import update_ruamel_yaml_map

if TYPE_CHECKING:
    from usethis._integrations.ci.bitbucket.io_ import BitbucketPipelinesYAMLDocument
    from usethis._integrations.ci.bitbucket.schema import Cache


def get_cache_by_name() -> dict[str, Cache]:
    with edit_bitbucket_pipelines_yaml() as doc:
        config = doc.model

    if config.definitions is None:
        return {}

    cache_by_name = config.definitions.caches

    if cache_by_name is None:
        return {}

    return cache_by_name


def add_caches(cache_by_name: dict[str, Cache]) -> None:
    with edit_bitbucket_pipelines_yaml() as doc:
        _add_caches_via_doc(cache_by_name, doc=doc)
        dump = bitbucket_fancy_dump(doc.model, reference=doc.content)
        update_ruamel_yaml_map(doc.content, dump, preserve_comments=True)


def _add_caches_via_doc(
    cache_by_name: dict[str, Cache], *, doc: BitbucketPipelinesYAMLDocument
) -> None:
    config = doc.model

    if config.definitions is None:
        config.definitions = Definitions()
    if config.definitions.caches is None:
        config.definitions.caches = {}

    for name, cache in cache_by_name.items():
        if not _cache_exists(name, doc=doc):
            tick_print(
                f"Adding cache '{name}' definition to 'bitbucket-pipelines.yml'."
            )
            config.definitions.caches[name] = cache


def remove_cache(cache: str) -> None:
    with edit_bitbucket_pipelines_yaml() as doc:
        config = doc.model

        if config.definitions is None or config.definitions.caches is None:
            return

        if cache in config.definitions.caches:
            tick_print(
                f"Removing cache '{cache}' definition from 'bitbucket-pipelines.yml'."
            )
            del config.definitions.caches[cache]

            # Remove an empty caches section
            if not config.definitions.caches:
                del config.definitions.caches

        dump = bitbucket_fancy_dump(config, reference=doc.content)
        update_ruamel_yaml_map(doc.content, dump, preserve_comments=True)


def _cache_exists(name: str, *, doc: BitbucketPipelinesYAMLDocument) -> bool:
    if doc.model.definitions is None or doc.model.definitions.caches is None:
        return False

    return name in doc.model.definitions.caches
