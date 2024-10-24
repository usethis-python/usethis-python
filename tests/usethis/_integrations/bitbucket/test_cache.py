from pathlib import Path

from usethis._integrations.bitbucket.cache import Cache, add_cache, get_caches
from usethis._utils._test import change_cwd


class TestAddCache:
    def test_in_caches(self, uv_init_dir: Path):
        cache = Cache(name="example", path="~/.cache/example")

        # Act
        with change_cwd(uv_init_dir):
            add_cache(cache)

            # Assert
            caches = get_caches()
        assert caches == [cache]
