from pathlib import Path

import pytest

from usethis._ci import (
    is_bitbucket_used,
    remove_bitbucket_pytest_steps,
    update_bitbucket_pytest_steps,
)
from usethis._integrations.bitbucket.config import add_bitbucket_pipeline_config
from usethis._integrations.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.python.version import (
    extract_major_version,
    get_python_version,
)
from usethis._test import change_cwd


class TestIsBitbucketUsed:
    def test_file_exists(self, tmp_path: Path):
        (tmp_path / "bitbucket-pipelines.yml").touch()
        with change_cwd(tmp_path):
            assert is_bitbucket_used()

    def test_file_does_not_exist(self, tmp_path: Path):
        with change_cwd(tmp_path):
            assert not is_bitbucket_used()


class TestUpdateBitbucketPytestSteps:
    def test_no_file(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(uv_init_dir), PyprojectTOMLManager():
            update_bitbucket_pytest_steps()

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
            name: Test on 3.12
            caches:
              - uv
            script:
              - *install-uv
              - uv run --python 3.12 pytest -x --junitxml=test-reports/report.xml
      - step:
            name: Test on 3.13
            caches:
              - uv
            script:
              - *install-uv
              - uv run --python 3.13 pytest -x --junitxml=test-reports/report.xml
"""
        )

        out, err = capfd.readouterr()
        assert not err
        assert out == (
            "✔ Writing 'bitbucket-pipelines.yml'.\n"
            "✔ Adding cache 'uv' definition to 'bitbucket-pipelines.yml'.\n"
            "✔ Adding 'Test on 3.12' to default pipeline in 'bitbucket-pipelines.yml'.\n"
            "✔ Adding 'Test on 3.13' to default pipeline in 'bitbucket-pipelines.yml'.\n"
        )

    def test_remove_old_steps(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        """Note this test also checks we don't add a cache when it's not needed."""
        # Arrange
        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: Test on 3.11
            script:
                - echo 'Hello, Python 3.11!'
      - step:
            name: Test on 3.12
            script:
                - echo 'Hello, Python 3.12!'
"""
        )
        (uv_init_dir / "pyproject.toml").write_text(
            """\
[project]
requires-python = ">=3.12,<3.13"
version = "0.1.0"
"""
        )

        # Act
        with change_cwd(uv_init_dir), PyprojectTOMLManager():
            update_bitbucket_pytest_steps()

        # Assert
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()
        assert (
            contents
            == """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: Test on 3.12
            script:
              - echo 'Hello, Python 3.12!'
"""
        )
        out, err = capfd.readouterr()
        assert not err
        assert out == (
            "✔ Removing 'Test on 3.11' from default pipeline in 'bitbucket-pipelines.yml'.\n"
        )

    def test_no_requires_python(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "example"
version = "0.1.0"
"""
        )

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            update_bitbucket_pytest_steps()

        # Assert
        assert (tmp_path / "bitbucket-pipelines.yml").exists()
        contents = (tmp_path / "bitbucket-pipelines.yml").read_text()
        version = extract_major_version(get_python_version())
        assert (
            contents
            == f"""\
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
            name: Test on 3.{version}
            caches:
              - uv
            script:
              - *install-uv
              - uv run --python 3.{version} pytest -x --junitxml=test-reports/report.xml
"""
        )


class TestRemoveBitbucketPytestSteps:
    def test_no_file(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            remove_bitbucket_pytest_steps()

        # Assert
        assert not (uv_init_dir / "bitbucket-pipelines.yml").exists()

    def test_dont_touch_if_no_pytest_steps(self, uv_init_dir: Path):
        # Arrange
        with change_cwd(uv_init_dir), PyprojectTOMLManager():
            add_bitbucket_pipeline_config()
        contents = (uv_init_dir / "bitbucket-pipelines.yml").read_text()

        # Act
        with change_cwd(uv_init_dir), PyprojectTOMLManager():
            remove_bitbucket_pytest_steps()

        # Assert
        assert (uv_init_dir / "bitbucket-pipelines.yml").exists()
        assert (uv_init_dir / "bitbucket-pipelines.yml").read_text() == contents

    def test_one_step(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / "bitbucket-pipelines.yml").write_text(
            """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: Test on 3.12
            script:
                - echo 'Hello, Python 3.12!'
"""
        )

        # Act
        with change_cwd(uv_init_dir), PyprojectTOMLManager():
            remove_bitbucket_pytest_steps()

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
