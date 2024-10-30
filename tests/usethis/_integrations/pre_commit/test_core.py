from pathlib import Path

import pytest
import requests

from usethis._integrations.pre_commit.core import (
    _VALIDATEPYPROJECT_VERSION,
    add_pre_commit_config,
    remove_pre_commit_config,
)
from usethis._utils._test import change_cwd


class TestAddPreCommitConfig:
    def test_exists(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            add_pre_commit_config()

        # Assert
        contents = (uv_init_dir / ".pre-commit-config.yaml").read_text()
        assert contents == (
            f"""\
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: "{_VALIDATEPYPROJECT_VERSION}"
    hooks:
      - id: validate-pyproject
        additional_dependencies: ["validate-pyproject-schema-store[all]"]
"""
        )

    def test_fallback(self, uv_init_dir: Path, monkeypatch: pytest.MonkeyPatch):
        # Arrange
        def mock_get(*args, **kwargs):
            class MockResponse:
                def raise_for_status(self):
                    raise requests.exceptions.HTTPError("Failed to fetch tags")

            return MockResponse()

        monkeypatch.setattr("requests.get", mock_get)

        # Act
        with change_cwd(uv_init_dir):
            add_pre_commit_config()

        # Assert
        contents = (uv_init_dir / ".pre-commit-config.yaml").read_text()
        assert contents == (
            f"""\
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: "{_VALIDATEPYPROJECT_VERSION}"
    hooks:
      - id: validate-pyproject
        additional_dependencies: ["validate-pyproject-schema-store[all]"]
"""
        )

    def test_message(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(uv_init_dir):
            add_pre_commit_config()

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Writing '.pre-commit-config.yaml'.\n"

    def test_already_exists(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (uv_init_dir / ".pre-commit-config.yaml").touch()

        # Act
        with change_cwd(uv_init_dir):
            add_pre_commit_config()

        # Assert
        out, _ = capfd.readouterr()
        assert out == ""
        assert (uv_init_dir / ".pre-commit-config.yaml").read_text() == ""


class TestRemovePreCommitConfig:
    def test_exists(self, uv_init_dir: Path):
        # Arrange
        (uv_init_dir / ".pre-commit-config.yaml").touch()

        # Act
        with change_cwd(uv_init_dir):
            remove_pre_commit_config()

        # Assert
        assert not (uv_init_dir / ".pre-commit-config.yaml").exists()

    def test_message(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (uv_init_dir / ".pre-commit-config.yaml").touch()

        # Act
        with change_cwd(uv_init_dir):
            remove_pre_commit_config()

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Removing .pre-commit-config.yaml file.\n"

    def test_already_missing(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Act
        with change_cwd(uv_init_dir):
            remove_pre_commit_config()

        # Assert
        out, _ = capfd.readouterr()
        assert out == ""
        assert not (uv_init_dir / ".pre-commit-config.yaml").exists()

    def test_does_not_exist(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            remove_pre_commit_config()

        # Assert
        assert not (uv_init_dir / ".pre-commit-config.yaml").exists()
