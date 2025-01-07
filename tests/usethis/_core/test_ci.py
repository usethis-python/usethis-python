from pathlib import Path

import pytest

from usethis._ci import add_bitbucket_pytest_steps
from usethis._core.ci import use_ci_bitbucket
from usethis._core.tool import use_pre_commit
from usethis._integrations.bitbucket.steps import get_steps_in_default
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

            def test_already_exists(self, uv_init_dir: Path):
                # Arrange
                (uv_init_dir / "bitbucket-pipelines.yml").touch()

                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                assert (uv_init_dir / "bitbucket-pipelines.yml").read_text() == ""

        class TestPreCommitIntegration:
            def test_mentioned_in_file(
                self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
            ):
                # Arrange
                (uv_init_dir / ".pre-commit-config.yaml").touch()

                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pre-commit" in contents
                out, err = capfd.readouterr()
                assert not err
                assert (
                    out
                    == (
                        "✔ Writing 'bitbucket-pipelines.yml'.\n"
                        "✔ Adding cache 'uv' definition to 'bitbucket-pipelines.yml'.\n"
                        "✔ Adding cache 'pre-commit' definition to 'bitbucket-pipelines.yml'.\n"
                        "✔ Adding 'Run pre-commit' to default pipeline in 'bitbucket-pipelines.yml'.\n"
                        "ℹ Consider `usethis tool pytest` to test your code for the pipeline.\n"  # noqa: RUF001
                        "☐ Run your pipeline via the Bitbucket website.\n"
                    )
                )

            def test_not_mentioned_if_not_used(self, uv_init_dir: Path):
                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pre-commit" not in contents

        def test_placeholder_removed(self, uv_init_repo_dir: Path):
            with change_cwd(uv_init_repo_dir):
                # Arrange
                use_ci_bitbucket()
                contents = (uv_init_repo_dir / "bitbucket-pipelines.yml").read_text()
                assert "Placeholder" in contents

                # Act
                use_pre_commit()

            # Assert
            contents = (uv_init_repo_dir / "bitbucket-pipelines.yml").read_text()
            assert "Placeholder" not in contents

        def test_placeholder_restored(self, uv_init_repo_dir: Path):
            with change_cwd(uv_init_repo_dir):
                # Arrange
                use_pre_commit()
                use_ci_bitbucket()
                contents = (uv_init_repo_dir / "bitbucket-pipelines.yml").read_text()
                assert "Placeholder" not in contents

                # Act
                use_pre_commit(remove=True)

            # Assert
            contents = (uv_init_repo_dir / "bitbucket-pipelines.yml").read_text()
            assert "Placeholder" in contents

        def test_unused_cache_removed(self, uv_init_repo_dir: Path):
            # Arrange
            (uv_init_repo_dir / "bitbucket-pipelines.yml").write_text("""\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: This step doesn't cache anything
            script:
              - echo 'Hello, world!'
""")

            with change_cwd(uv_init_repo_dir):
                # Act
                use_pre_commit()
                use_pre_commit(remove=True)

            # Assert
            for step in get_steps_in_default():
                if step.caches is not None:
                    assert "uv" not in step.caches
            content = (uv_init_repo_dir / "bitbucket-pipelines.yml").read_text()
            assert "caches" not in content  # Should remove the empty cache section

        class TestPytestIntegration:
            def test_mentioned_in_file(
                self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
            ):
                # Arrange
                (uv_init_dir / "tests").mkdir()
                (uv_init_dir / "tests" / "conftest.py").touch()

                # Act
                with change_cwd(uv_init_dir):
                    use_ci_bitbucket()

                # Assert
                contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
                assert "pytest" in contents
                out, err = capfd.readouterr()
                assert not err
                assert out == (
                    "✔ Writing 'bitbucket-pipelines.yml'.\n"
                    "✔ Adding cache 'uv' definition to 'bitbucket-pipelines.yml'.\n"
                    "✔ Adding 'Test - Python 3.12' to default pipeline in 'bitbucket-pipelines.yml'.\n"
                    "✔ Adding 'Test - Python 3.13' to default pipeline in 'bitbucket-pipelines.yml'.\n"
                    "☐ Run your pipeline via the Bitbucket website.\n"
                )

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
                assert out == "✔ Removing 'bitbucket-pipelines.yml'.\n"


class TestAddBitbucketPytestSteps:
    def test_no_file(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(uv_init_dir):
            add_bitbucket_pytest_steps()

        # Assert
        assert (uv_init_dir / "bitbucket-pipelines.yml").exists()
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
            name: Test - Python 3.12
            caches:
              - uv
            script:
              - *install-uv
              - uv run --python 3.12 pytest
      - step:
            name: Test - Python 3.13
            caches:
              - uv
            script:
              - *install-uv
              - uv run --python 3.13 pytest
"""
        )

        out, err = capfd.readouterr()
        assert not err
        assert out == (
            "✔ Writing 'bitbucket-pipelines.yml'.\n"
            "✔ Adding cache 'uv' definition to 'bitbucket-pipelines.yml'.\n"
            "✔ Adding 'Test - Python 3.12' to default pipeline in 'bitbucket-pipelines.yml'.\n"
            "✔ Adding 'Test - Python 3.13' to default pipeline in 'bitbucket-pipelines.yml'.\n"
        )
