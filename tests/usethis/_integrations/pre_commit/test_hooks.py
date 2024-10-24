from pathlib import Path

import pytest

from usethis._integrations.pre_commit.config import HookConfig, PreCommitRepoConfig
from usethis._integrations.pre_commit.hooks import (
    DuplicatedHookNameError,
    add_hook,
    get_hook_names,
    remove_hook,
)
from usethis._utils._test import change_cwd


class TestAddHook:
    def test_unregistered_id(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text("""
repos:
  - repo: foo
    hooks:
    - id: bar
""")
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

        with change_cwd(tmp_path):
            assert get_hook_names() == []

    def test_single(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """
repos:
  - repo: foo
    hooks:
      - id: bar
"""
        )
        with change_cwd(tmp_path):
            assert get_hook_names() == ["bar"]

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
        with change_cwd(tmp_path):
            assert get_hook_names() == ["bar", "baz"]

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
        with change_cwd(tmp_path):
            assert get_hook_names() == ["bar", "qux"]

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

        with (
            change_cwd(tmp_path),
            pytest.raises(
                DuplicatedHookNameError, match="Hook name 'bar' is duplicated"
            ),
        ):
            get_hook_names()
