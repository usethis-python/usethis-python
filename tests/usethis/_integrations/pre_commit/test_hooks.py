from pathlib import Path

import pytest

from usethis._integrations.pre_commit.hooks import (
    DuplicatedHookNameError,
    add_placeholder_hook,
    add_repo,
    get_hook_names,
    remove_hook,
)
from usethis._integrations.pre_commit.schema import HookDefinition, UriRepo
from usethis._test import change_cwd


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
            add_repo(
                UriRepo(
                    repo="foo", rev="foo", hooks=[HookDefinition(id="foo", name="foo")]
                )
            )


class TestRemoveHook:
    def test_empty(self, tmp_path: Path):
        with change_cwd(tmp_path):
            remove_hook("foo")
        assert (
            (tmp_path / ".pre-commit-config.yaml").read_text()
            == """\
repos:
  - repo: local
    hooks:
      - id: placeholder
        name: Placeholder - add your own hooks!
        entry: uv run python -c "print('hello world!')"
        language: python
"""
        )

    def test_single(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """\
repos:
  - repo: foo
    hooks:    
    - id: bar
"""
        )
        with change_cwd(tmp_path):
            remove_hook("bar")
        assert (
            (tmp_path / ".pre-commit-config.yaml").read_text()
            == """\
repos:
  - repo: local
    hooks:
      - id: placeholder
        name: Placeholder - add your own hooks!
        entry: uv run python -c "print('hello world!')"
        language: python
"""
        )

    def test_multihooks(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """\
repos:
  - repo: local # comment
    hooks:    
      - id: bar
        name: bar
        entry: bar
        language: python
  - repo: local # other comment
    hooks:
      - id: baz
        name: baz
        entry: baz
        language: python
"""
        )
        with change_cwd(tmp_path):
            remove_hook("bar")
        assert (tmp_path / ".pre-commit-config.yaml").read_text() == (
            """\
repos:
  - repo: local # other comment
    hooks:
      - id: baz
        name: baz
        entry: baz
        language: python
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


class TestAddPlaceholderHook:
    def test_contents(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(tmp_path):
            add_placeholder_hook()

        # Assert
        assert (tmp_path / ".pre-commit-config.yaml").exists()
        assert (
            (tmp_path / ".pre-commit-config.yaml").read_text()
            == """\
repos:
  - repo: local
    hooks:
      - id: placeholder
        name: Placeholder - add your own hooks!
        entry: uv run python -c "print('hello world!')"
        language: python
"""
        )

        out, _ = capfd.readouterr()
        # Keep these messages in sync with the ones used for bitbucket
        assert out == (
            "✔ Writing '.pre-commit-config.yaml'.\n"
            "✔ Adding placeholder hook to '.pre-commit-config.yaml'.\n"
            "☐ Remove the placeholder hook in '.pre-commit-config.yaml'.\n"
            "☐ Replace it with your own hooks.\n"
            "☐ Alternatively, use 'usethis tool' to add other tools and their hooks.\n"
        )
