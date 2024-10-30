from pathlib import Path

import pytest

from usethis._integrations.bitbucket.cache import (
    Cache,
    CacheAlreadyExistsError,
    add_cache,
    get_caches,
)
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

    def test_already_exists(self, uv_init_dir: Path):
        # Arrange
        cache = Cache(name="example", path="~/.cache/example")

        with change_cwd(uv_init_dir):
            add_cache(cache)

            # Act, Assert
            with pytest.raises(CacheAlreadyExistsError):
                add_cache(cache, exists_ok=False)
