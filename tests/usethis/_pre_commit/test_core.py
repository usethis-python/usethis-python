from pathlib import Path

import pytest
import requests

from usethis._pre_commit.config import HookConfig, PreCommitRepoConfig
from usethis._pre_commit.core import (
    _VALIDATEPYPROJECT_VERSION,
    DuplicatedHookNameError,
    add_hook,
    ensure_pre_commit_config,
    get_hook_names,
    remove_hook,
    remove_pre_commit_config,
)
from usethis._test import change_cwd


class TestEnsurePreCommitConfig:
    def test_exists(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            ensure_pre_commit_config()

        # Assert
        contents = (uv_init_dir / ".pre-commit-config.yaml").read_text()
        assert contents == (
            f"""
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
            ensure_pre_commit_config()

        # Assert
        contents = (uv_init_dir / ".pre-commit-config.yaml").read_text()
        assert contents == (
            f"""
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
            ensure_pre_commit_config()

        # Assert
        out, _ = capfd.readouterr()
        assert out == "✔ Creating .pre-commit-config.yaml file\n"

    def test_already_exists(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (uv_init_dir / ".pre-commit-config.yaml").touch()

        # Act
        with change_cwd(uv_init_dir):
            ensure_pre_commit_config()

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
        assert out == "✔ Removing .pre-commit-config.yaml file\n"

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


class TestAddHook:
    def test_unregistered_id(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
        with (
            change_cwd(tmp_path),
            pytest.raises(NotImplementedError, match="Hook 'foo' not recognized"),
        ):
            add_hook(
                PreCommitRepoConfig(
                    repo="foo", rev="foo", hooks=[HookConfig(id="foo", name="foo")]
                )
            )


class TestRemoveHook:
    def test_empty(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
        with change_cwd(tmp_path):
            remove_hook("foo")
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == "repos: []\n"

    def test_single(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """repos:
  - repo: foo
    hooks:    
    - id: bar
"""
        )
        with change_cwd(tmp_path):
            remove_hook("bar")
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == "repos: []\n"

    def test_multihooks(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """repos:
  - repo: foo # comment
    hooks:    
    - id: bar
    - id: baz
"""
        )
        with change_cwd(tmp_path):
            remove_hook("bar")
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == (
            """repos:
  - repo: foo # comment
    hooks:
      - id: baz
"""
        )


class TestGetHookNames:
    def test_empty(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
        assert get_hook_names(tmp_path) == []

    def test_single(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """
repos:
  - repo: foo
    hooks:
      - id: bar
"""
        )
        assert get_hook_names(tmp_path) == ["bar"]

    def test_multihooks(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """
repos:
  - repo: foo
    hooks:
      - id: bar
      - id: baz
"""
        )
        assert get_hook_names(tmp_path) == ["bar", "baz"]

    def test_multirepo(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """
repos:
  - repo: foo
    hooks:
    - id: bar
  - repo: baz
    hooks:
    - id: qux
"""
        )
        assert get_hook_names(tmp_path) == ["bar", "qux"]

    def test_duplicated_raises(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """
repos:
  - repo: foo
    hooks:
    - id: bar
  - repo: baz
    hooks:
    - id: bar
"""
        )

        with pytest.raises(
            DuplicatedHookNameError, match="Hook name 'bar' is duplicated"
        ):
            get_hook_names(tmp_path)
