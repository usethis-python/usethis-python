from pathlib import Path

import pytest

from usethis._core.ci import use_ci_bitbucket
from usethis._test import change_cwd


class TestBitBucket:
    class TestAdd:
        class TestConfigFile:
            def test_exists(self, uv_init_dir: Path):
                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                assert (uv_init_dir / "bitbucket-pipelines.yml").exists()

            def test_contents(self, uv_init_dir: Path):
                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()

                assert (
                    contents
                    == """\
image: atlassian/default-image:3
definitions:
    caches:
        uv: ~/.cache/uv
    script_items:
      - &install-uv |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.local/bin/env
        export UV_LINK_MODE=copy
        uv --version
pipelines:
    default:
      - step:
            name: Placeholder - add your own steps!
            caches:
              - uv
            script:
              - *install-uv
              - echo 'Hello, world!'
"""
                )

            def test_already_exists(self, tmp_path: Path):
                # Arrange
                (tmp_path / "bitbucket-pipelines.yml").touch()

                # Act
                with change_cwd(tmp_path):
                    use_ci_bitbucket()

                # Assert
                assert (tmp_path / "bitbucket-pipelines.yml").read_text() == ""

        class TestPreCommitIntegration:
            def test_mentioned_in_file(self, uv_init_dir: Path):
                # Arrange
                (uv_init_dir / ".pre-commit-config.yaml").touch()

                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pre-commit" in contents

            def test_not_mentioned_if_not_used(self, uv_init_dir: Path):
                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pre-commit" not in contents

            # TODO consistency in precommit vs pre_commit
            # and PreCommit vs Precommit

        class TestPytestIntegration:
            def test_mentioned_in_file(self, uv_init_dir: Path):
                # Arrange
                (uv_init_dir / "tests").mkdir()
                (uv_init_dir / "tests" / "conftest.py").touch()

                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pytest" in contents

            def test_not_mentioned_if_not_used(self, uv_init_dir: Path):
                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pytest" not in contents

    class TestRemove:
        class TestPyproject:
            def test_removed(self, tmp_path: Path):
                # Arrange
                (tmp_path / "bitbucket-pipelines.yml").touch()

                # Act
                with change_cwd(tmp_path):
                    use_ci_bitbucket(remove=True)

                # Assert
                assert not (tmp_path / "bitbucket-pipelines.yml").exists()

            def test_message(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
                # Arrange
                (tmp_path / "bitbucket-pipelines.yml").touch()

                # Act
                with change_cwd(tmp_path):
                    use_ci_bitbucket(remove=True)

                # Assert
                out, _ = capfd.readouterr()
                assert out == "✔ Removing 'bitbucket-pipelines.yml' file.\n"
