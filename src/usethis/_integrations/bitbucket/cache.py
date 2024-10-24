from pathlib import Path

from pydantic import BaseModel

from usethis._utils._yaml import edit_yaml, load_yaml


class Cache(BaseModel):
    name: str
    path: str


class CacheAlreadyExistsError(Exception):
    """Raised when trying to add a cache that already exists."""


def get_caches() -> list[Cache]:
    path = Path.cwd() / "bitbucket-pipelines.yml"

    content = load_yaml(path)

    try:
        caches: dict[str, str] = content["definitions"]["caches"]
    except KeyError:
        return []

    return [Cache(name=name, path=path) for name, path in caches.items()]


def add_cache(cache: Cache, exists_ok: bool = False) -> None:
    path = Path.cwd() / "bitbucket-pipelines.yml"

    if not path.exists():
        path.touch()

    with edit_yaml(path) as content:
        try:
            content["definitions"]
        except KeyError:
            content["definitions"] = {}

        try:
            content["definitions"]["caches"]
        except KeyError:
            content["definitions"]["caches"] = {}

        try:
            content["definitions"]["caches"][cache.name]
        except KeyError:
            content["definitions"]["caches"][cache.name] = cache.path
        else:
            if not exists_ok:
                raise CacheAlreadyExistsError(f"Cache '{cache.name}' already exists.")
            else:
                # Exit early; the cache is already present so we'll leave it alone.
                return
