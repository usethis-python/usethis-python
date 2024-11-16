from ruamel.yaml.comments import CommentedMap

from usethis._console import tick_print
from usethis._integrations.bitbucket.dump import fancy_pipelines_model_dump
from usethis._integrations.bitbucket.io import (
    edit_bitbucket_pipelines_yaml,
    read_bitbucket_pipelines_yaml,
)
from usethis._integrations.bitbucket.pipeline import Cache, Definitions
from usethis._integrations.yaml.update import update_ruamel_yaml_map


def get_cache_by_name() -> dict[str, Cache]:
    content = read_bitbucket_pipelines_yaml()

    if content.definitions is None:
        return {}

    cache_by_name = content.definitions.caches

    if cache_by_name is None:
        return {}

    return cache_by_name


def add_caches(cache_by_name: dict[str, Cache]) -> None:
    # Tell the user what we are doing.
    names = list(cache_by_name.keys())
    if len(names) == 0:
        return
    elif len(names) == 1:
        name_str = f"'{names[0]}'"
    else:
        name_str = (
            ", ".join(f"'{name}'" for name in names[:-1]) + f", and '{names[-1]}'"
        )

    # TODO test this message.
    tick_print(f"Adding cache definitions {name_str} to 'bitbucket-pipelines.yml'.")

    with edit_bitbucket_pipelines_yaml() as doc:
        # TODO this is duplciated in cache.py
        if not isinstance(doc.content, CommentedMap):
            msg = (
                f"Error when parsing Bitbucket Pipelines configuration. Expected file "
                f"to be a map, got {type(doc.content)}."
            )
            raise ValueError(msg)

        config = doc.model

        if config.definitions is None:
            config.definitions = Definitions(caches=cache_by_name)
        elif config.definitions.caches is None:
            config.definitions.caches = cache_by_name
        else:
            for name, cache in cache_by_name.items():
                if name not in config.definitions.caches:
                    config.definitions.caches[name] = cache
                # Otherwise, the cache is already present so we'll leave it alone.
                # TODO we could check whether it's the same content but different name

        dump = fancy_pipelines_model_dump(config, reference=doc.content)
        update_ruamel_yaml_map(doc.content, dump, preserve_comments=True)
