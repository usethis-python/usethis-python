from pathlib import Path

import pytest

from usethis._pre_commit.core import (
    DuplicatedHookNameError,
    delete_hook,
    get_hook_names,
)
from usethis._test import change_cwd


class TestDeleteHook:
    def test_empty(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
        with change_cwd(tmp_path):
            delete_hook("foo")
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
            delete_hook("bar")
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
            delete_hook("bar")
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
