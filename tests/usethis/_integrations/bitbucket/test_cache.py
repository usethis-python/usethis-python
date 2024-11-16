from pathlib import Path

from usethis._integrations.bitbucket.cache import (
    Cache,
    add_caches,
    get_cache_by_name,
)
from usethis._integrations.bitbucket.config import add_bitbucket_pipeline_config
from usethis._integrations.bitbucket.pipeline import CachePath
from usethis._test import change_cwd

# TODO it makes sense for errors about incorrect config to get handled in the ui layer.
# So let's raise - but the raise interface needs to be documented in all docstrings.


class TestAddCaches:
    def test_in_caches(self, uv_init_dir: Path):
        # Arrange
        cache_by_name = {"example": Cache(CachePath("~/.cache/example"))}

        # Act
        with change_cwd(uv_init_dir):
            add_bitbucket_pipeline_config()
            add_caches(cache_by_name)

            # Assert
            default_cache_by_name = {"uv": Cache(CachePath("~/.cache/uv"))}
            assert get_cache_by_name() == cache_by_name | default_cache_by_name

    def test_already_exists(self, uv_init_dir: Path):
        # Arrange
        cache_by_name = {
            "uv": Cache(CachePath("~/.cache/uv"))  # uv cache is in the default config
        }

        # Act
        with change_cwd(uv_init_dir):
            add_bitbucket_pipeline_config()
            add_caches(cache_by_name)

            # Assert
            assert get_cache_by_name() == cache_by_name

    def test_definitions_order(self, uv_init_dir: Path):
        """Test that the newly-created definitions section is placed after the image."""
        # Arrange
        cache_by_name = {"example": Cache(CachePath("~/.cache/example"))}

        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            script: ["echo 'Hello, world!'"]
"""
        )

        # Act
        with change_cwd(uv_init_dir):
            add_caches(cache_by_name)

        # Assert
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:3
definitions:
    caches:
        example: ~/.cache/example
pipelines:
    default:
      - step:
            script: ["echo 'Hello, world!'"]
"""
        )
