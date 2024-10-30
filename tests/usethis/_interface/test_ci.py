from pathlib import Path

import pytest

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

            def test_already_exists(self, uv_init_dir: Path):
                # Arrange
                (uv_init_dir / "bitbucket-pipelines.yml").touch()

                # Act
                with change_cwd(uv_init_dir):
                    _bitbucket(offline=is_offline())

                # Assert
                assert (uv_init_dir / "bitbucket-pipelines.yml").read_text() == ""

        class TestPreCommitIntegration:
            def test_mentioned_in_file(self, uv_init_dir: Path):
                # Arrange
                (uv_init_dir / ".pre-commit-config.yaml").touch()

                # Act
                with change_cwd(uv_init_dir):
                    _bitbucket(offline=is_offline())

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pre-commit" in contents

            def test_not_mentioned_if_not_used(self, uv_init_dir: Path):
                # Act
                with change_cwd(uv_init_dir):
                    _bitbucket(offline=is_offline())

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pre-commit" not in contents

        class TestPytestIntegration:
            def test_mentioned_in_file(self, uv_init_dir: Path):
                # Arrange
                (uv_init_dir / "tests").mkdir()
                (uv_init_dir / "tests" / "conftest.py").touch()

                # Act
                with change_cwd(uv_init_dir):
                    _bitbucket(offline=is_offline())

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pytest" in contents

            def test_not_mentioned_if_not_used(self, uv_init_dir: Path):
                # Act
                with change_cwd(uv_init_dir):
                    _bitbucket(offline=is_offline())

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pytest" not in contents

    class TestRemove:
        class TestPyproject:
            def test_removed(self, uv_init_dir: Path):
                # Arrange
                (uv_init_dir / "bitbucket-pipelines.yml").touch()

                # Act
                with change_cwd(uv_init_dir):
                    _bitbucket(remove=True, offline=is_offline())

                # Assert
                assert not (uv_init_dir / "bitbucket-pipelines.yml").exists()

            def test_message(
                self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
            ):
                # Arrange
                (uv_init_dir / "bitbucket-pipelines.yml").touch()

                # Act
                with change_cwd(uv_init_dir):
                    _bitbucket(remove=True, offline=is_offline())

                # Assert
                out, _ = capfd.readouterr()
                assert out == "✔ Removing 'bitbucket-pipelines.yml' file.\n"
