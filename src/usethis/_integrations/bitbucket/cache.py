from usethis._console import tick_print
from usethis._integrations.bitbucket.dump import fancy_pipelines_model_dump
from usethis._integrations.bitbucket.io import (
    BitbucketPipelinesYAMLDocument,
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
    with edit_bitbucket_pipelines_yaml() as doc:
        config = doc.model

        if config.definitions is None:
            config.definitions = Definitions(caches=cache_by_name)
        elif config.definitions.caches is None:
            config.definitions.caches = cache_by_name
        else:
            for name, cache in cache_by_name.items():
                if not _cache_exists(name, doc=doc):
                    tick_print(
                        f"Adding cache '{name}' definition to "
                        f"'bitbucket-pipelines.yml'."
                    )
                    config.definitions.caches[name] = cache
                # Otherwise, the cache is already present so we'll leave it alone.

        dump = fancy_pipelines_model_dump(config, reference=doc.content)
        update_ruamel_yaml_map(doc.content, dump, preserve_comments=True)


def _cache_exists(name: str, *, doc: BitbucketPipelinesYAMLDocument) -> bool:
    if doc.model.definitions is None or doc.model.definitions.caches is None:
        return False

    return name in doc.model.definitions.caches

    # TODO also we could check whether it's the same content but different name. That's
    # harder because it requires we identify the differing name and start using that
    # instead in our adding the hook... or change the name, which is a bit aggressive.
    #
    # Record this in GitHub perhaps... more thought needed on the architectural impacts
    # of trying to support this.

    # Here's some more thought... we're trying to identify a cache by name as a kind
    # of identifying ID. But maybe better to identify a cache by its content. If we
    # need to add it because it doesn't already exist, then we could have a lookup
    # which gives conventional names for different contents (turning it on its head;
    # it becomes name_by_cache). But what about if the user keeps a cache's name but
    # modifies the script? We should allow that to also be referring to the same thing.
    # So more thought needed.

    # Also note that there's currently an issue where the user might define multiple
    # scripts with the same contents
