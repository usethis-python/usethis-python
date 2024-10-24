from pathlib import Path

from usethis._interface.ci import _bitbucket
from usethis._utils._test import change_cwd, is_offline


class TestBitBucket:
    class TestAdd:
        class TestConfigFile:
            def test_exists(self, uv_init_dir: Path):
                # Act
                with change_cwd(uv_init_dir):
                    _bitbucket(offline=is_offline())

                # Assert
                assert (uv_init_dir / "bitbucket-pipelines.yml").exists()

            def test_contents(self, uv_init_dir: Path):
                # Act
                with change_cwd(uv_init_dir):
                    _bitbucket(offline=is_offline())

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()

                assert (
                    contents
                    == """\
image: atlassian/default-image:3

definitions:
    caches:
        uv: ~/.cache/uv
    scripts:
      - script: &install-uv |-
            curl -LsSf https://astral.sh/uv/install.sh | sh
            source $HOME/.cargo/env
            export UV_LINK_MODE=copy
pipelines:
    default:
      - step:
            name: Placeholder - add your own steps!
            script:
              - *install-uv
              - echo 'Hello, world!'
"""
                )
