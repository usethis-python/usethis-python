from pathlib import Path

import pytest
from ruamel.yaml import YAML

from usethis._config_file import files_manager
from usethis._integrations.pre_commit import schema
from usethis._integrations.pre_commit.hooks import (
    HOOK_GROUPS,
    _get_placeholder_repo_config,
    add_placeholder_hook,
    add_repo,
    get_hook_ids,
    hooks_are_equivalent,
    insert_repo,
    remove_hook,
)
from usethis._integrations.pre_commit.yaml import PreCommitConfigYAMLManager
from usethis._test import change_cwd


class TestHookGroups:
    def test_is_list_of_lists(self):
        assert isinstance(HOOK_GROUPS, list)
        for group in HOOK_GROUPS:
            assert isinstance(group, list)
            for hook in group:
                assert isinstance(hook, str)

    def test_non_empty(self):
        assert len(HOOK_GROUPS) > 0
        for group in HOOK_GROUPS:
            assert len(group) > 0

    def test_no_duplicates(self):
        all_hooks = [hook for group in HOOK_GROUPS for hook in group]
        assert len(all_hooks) == len(set(all_hooks))


class TestAddRepo:
    def test_unregistered_id(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: foo
    hooks:
    - id: bar
""")
        with (
            change_cwd(tmp_path),
            files_manager(),
            pytest.raises(NotImplementedError, match="Hook 'foo' is not recognized"),
        ):
            add_repo(
                schema.UriRepo(
                    repo="foo",
                    rev="foo",
                    hooks=[schema.HookDefinition(id="foo", name="foo")],
                )
            )

    def test_adding_to_existing(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: foo
    hooks:
    - id: bar
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="deptry",
                            name="deptry",
                            entry="uv run --frozen deptry src",
                            language=schema.Language("system"),
                            always_run=True,
                        )
                    ],
                )
            )

        # Assert
        assert (
            (tmp_path / ".pre-commit-config.yaml").read_text()
            == """\
repos:
  - repo: foo
    hooks:
      - id: bar
  - repo: local
    hooks:
      - id: deptry
        name: deptry
        always_run: true
        entry: uv run --frozen deptry src
        language: system
"""
        )
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Adding hook 'deptry' to '.pre-commit-config.yaml'.\n"

    def test_placeholder(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(tmp_path), files_manager():
            add_repo(_get_placeholder_repo_config())

        # Assert
        assert (
            (tmp_path / ".pre-commit-config.yaml").read_text()
            == """\
repos:
  - repo: local
    hooks:
      - id: placeholder
        name: Placeholder - add your own hooks!
        entry: uv run --isolated --frozen --offline python -c "print('hello world!')"
        language: system
"""
        )
        out, err = capfd.readouterr()
        assert not err
        assert out == (
            "✔ Writing '.pre-commit-config.yaml'.\n"
            "✔ Adding placeholder hook to '.pre-commit-config.yaml'.\n"
        )

    def test_hook_order_constant_is_respected(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange: Add 'codespell' first (later in HOOK_GROUPS)
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="codespell",
                            name="codespell",
                            entry="codespell .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            # Now add 'pyproject-fmt' (earlier in HOOK_GROUPS)
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="pyproject-fmt",
                            name="pyproject-fmt",
                            entry="uv run --frozen pyproject-fmt .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            # Assert: pyproject-fmt should appear before codespell
            assert get_hook_ids() == [
                "pyproject-fmt",
                "codespell",
            ]

    def test_hooks_added_in_standard_order(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Arrange
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="pyproject-fmt",
                            name="pyproject-fmt",
                            entry="uv run --frozen pyproject-fmt .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            # Act
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="codespell",
                            name="codespell",
                            entry="codespell .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )
            # Assert
            assert get_hook_ids() == [
                "pyproject-fmt",
                "codespell",
            ]

    def test_hook_order_constant_is_respected_multi(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            # Act
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="foo",
                            name="foo",
                            entry="foo .",
                            language=schema.Language("system"),
                        )
                    ],
                ),
            )
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="codespell",
                            name="codespell",
                            entry="codespell .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="pyproject-fmt",
                            name="pyproject-fmt",
                            entry="uv run --frozen pyproject-fmt .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            # Assert
            assert get_hook_ids() == [
                "foo",
                "pyproject-fmt",
                "codespell",
            ]

    def test_prek_extra_fields_preserved(self, tmp_path: Path):
        """Extra keys like `priority` (from prek syntax) are preserved."""
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
minimum_prek_version: 0.2.23
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.0
    hooks:
      - id: ruff-check
        args: [--fix]
        priority: 0
      - id: ruff-format
        priority: 0
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="deptry",
                            name="deptry",
                            entry="uv run --frozen deptry src",
                            language=schema.Language("system"),
                            always_run=True,
                        )
                    ],
                )
            )

        # Assert - parse YAML to verify structure
        yaml = YAML()
        parsed = yaml.load((tmp_path / ".pre-commit-config.yaml").read_text())
        assert parsed["minimum_prek_version"] == "0.2.23"
        ruff_repo = parsed["repos"][0]
        assert ruff_repo["hooks"][0]["priority"] == 0
        assert ruff_repo["hooks"][1]["priority"] == 0
        assert any(
            hook["id"] == "deptry" for repo in parsed["repos"] for hook in repo["hooks"]
        )

    def test_prek_arbitrary_extra_keys(self, tmp_path: Path):
        """Arbitrary extra keys on hooks, repos, and top-level are preserved."""
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
custom_top_level_key: some_value
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.0
    custom_repo_key: 42
    hooks:
      - id: ruff-format
        custom_hook_key: true
""")

        # Act
        with change_cwd(tmp_path), files_manager():
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="codespell",
                            name="codespell",
                            entry="codespell .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

        # Assert - parse YAML to verify extra keys are at correct levels
        yaml = YAML()
        parsed = yaml.load((tmp_path / ".pre-commit-config.yaml").read_text())
        assert parsed["custom_top_level_key"] == "some_value"
        ruff_repo = parsed["repos"][0]
        assert ruff_repo["custom_repo_key"] == 42
        assert ruff_repo["hooks"][0]["custom_hook_key"] is True
        assert any(
            hook["id"] == "codespell"
            for repo in parsed["repos"]
            for hook in repo["hooks"]
        )


class TestInsertRepo:
    def test_predecessor_is_none(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
    - repo: codespell
      hooks:
      - id: codespell
""")

        # Act
        with change_cwd(tmp_path), PreCommitConfigYAMLManager() as mgr:
            existing_repos = mgr.model_validate().repos
            repos = insert_repo(
                repo_to_insert=schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="pyproject-fmt",
                            name="pyproject-fmt",
                            entry="uv run --frozen pyproject-fmt .",
                            language=schema.Language("system"),
                        )
                    ],
                ),
                existing_repos=existing_repos,
                predecessor=None,
            )

        # Assert
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Adding hook 'pyproject-fmt' to '.pre-commit-config.yaml'.\n"
        assert isinstance(repos, list)
        assert len(repos) == 2
        assert [repo.repo for repo in repos] == ["local", "codespell"]

    def test_existing_repo_has_none_hooks(self):
        # Arrange
        existing_repos = [schema.LocalRepo(repo="local", hooks=None)]
        new_hook = schema.HookDefinition(
            id="new-hook",
            name="New Hook",
            entry="echo 'New hook'",
            language=schema.Language("system"),
        )
        repo_to_insert = schema.LocalRepo(
            repo="local",
            hooks=[new_hook],
        )

        # Act
        results = insert_repo(
            repo_to_insert=repo_to_insert,
            existing_repos=existing_repos,
            predecessor=None,
        )

        # Assert
        assert isinstance(results, list)
        assert len(results) == 2
        assert results == [
            schema.LocalRepo(repo="local", hooks=[new_hook]),
            schema.LocalRepo(repo="local", hooks=None),
        ]

    def test_duplicate_predecessor(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # What if the predecessor ID is repeated multiple times? Will we end up
        # inserting the new repo multiple times? No.
        # Arrange
        (tmp_path / ".pre-commit-config.yaml").write_text("""\
repos:
  - repo: foo
    hooks:
    - id: bar
  - repo: foo
    hooks:
    - id: bar
""")

        # Act
        with change_cwd(tmp_path), PreCommitConfigYAMLManager() as mgr:
            existing_repos = mgr.model_validate().repos
            repos = insert_repo(
                repo_to_insert=schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="pyproject-fmt",
                            name="pyproject-fmt",
                            entry="uv run --frozen pyproject-fmt .",
                            language=schema.Language("system"),
                        )
                    ],
                ),
                existing_repos=existing_repos,
                predecessor="bar",
            )

        # Assert
        assert isinstance(repos, list)
        assert len(repos) == 3
        out, err = capfd.readouterr()
        assert not err
        assert out == "✔ Adding hook 'pyproject-fmt' to '.pre-commit-config.yaml'.\n"


class TestRemoveHook:
    def test_empty(self, tmp_path: Path):
        with change_cwd(tmp_path), files_manager():
            remove_hook("foo")
        assert (
            (tmp_path / ".pre-commit-config.yaml").read_text()
            == """\
repos:
  - repo: local
    hooks:
      - id: placeholder
        name: Placeholder - add your own hooks!
        entry: uv run --isolated --frozen --offline python -c "print('hello world!')"
        language: system
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
        with change_cwd(tmp_path), files_manager():
            remove_hook("bar")
        assert (
            (tmp_path / ".pre-commit-config.yaml").read_text()
            == """\
repos:
  - repo: local
    hooks:
      - id: placeholder
        name: Placeholder - add your own hooks!
        entry: uv run --isolated --frozen --offline python -c "print('hello world!')"
        language: system
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
        with change_cwd(tmp_path), files_manager():
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

    def test_dont_delete_no_hook_repo(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """\
repos:
  - repo: local
"""
        )

        with change_cwd(tmp_path), files_manager():
            remove_hook("bar")

        assert (tmp_path / ".pre-commit-config.yaml").read_text() == (
            """\
repos:
  - repo: local
"""
        )


class TestGetHookNames:
    def test_empty(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")

        with change_cwd(tmp_path), files_manager():
            assert get_hook_ids() == []

    def test_single(self, tmp_path: Path):
        (tmp_path / ".pre-commit-config.yaml").write_text(
            """
repos:
  - repo: foo
    hooks:
      - id: bar
"""
        )
        with change_cwd(tmp_path), files_manager():
            assert get_hook_ids() == ["bar"]

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
        with change_cwd(tmp_path), files_manager():
            assert get_hook_ids() == ["bar", "baz"]

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
        with change_cwd(tmp_path), files_manager():
            assert get_hook_ids() == ["bar", "qux"]

    def test_duplicated_ok(self, tmp_path: Path):
        # Arrange
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

        # Act
        with change_cwd(tmp_path), files_manager():
            result = get_hook_ids()

        # Assert
        assert result == ["bar", "bar"]


class TestAddPlaceholderHook:
    def test_contents(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(tmp_path), files_manager():
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
        entry: uv run --isolated --frozen --offline python -c "print('hello world!')"
        language: system
"""
        )

        out, _ = capfd.readouterr()
        assert out == (
            "✔ Writing '.pre-commit-config.yaml'.\n"
            "✔ Adding placeholder hook to '.pre-commit-config.yaml'.\n"
            "☐ Remove the placeholder hook in '.pre-commit-config.yaml'.\n"
            "☐ Replace it with your own hooks.\n"
            "☐ Alternatively, use 'usethis tool' to add other tools and their hooks.\n"
        )


class TestHooksAreEquivalent:
    def test_identical(self):
        # Arrange
        hook = schema.HookDefinition(
            id="foo",
            name="Foo",
            entry="echo 'Hello, world!'",
            language=schema.Language("python"),
        )
        other = schema.HookDefinition(
            id="foo",
            name="Foo",
            entry="echo 'Hello, world!'",
            language=schema.Language("python"),
        )

        # Act
        result = hooks_are_equivalent(hook, other)

        # Assert
        assert result is True

    def test_different_id(self):
        # Arrange
        hook = schema.HookDefinition(
            id="foo",
            name="Foo",
            entry="echo 'Hello, world!'",
            language=schema.Language("python"),
        )
        other = schema.HookDefinition(
            id="bar",
            name="Foo",
            entry="echo 'Hello, world!'",
            language=schema.Language("python"),
        )

        # Act
        result = hooks_are_equivalent(hook, other)

        # Assert
        assert result is False

    def test_different_name(self):
        # Arrange
        hook = schema.HookDefinition(
            id="foo",
            name="Foo",
            entry="echo 'Hello, world!'",
            language=schema.Language("python"),
        )
        other = schema.HookDefinition(
            id="foo",
            name="Bar",
            entry="echo 'Hello, world!'",
            language=schema.Language("python"),
        )

        # Act
        result = hooks_are_equivalent(hook, other)

        # Assert
        assert result is True

    def test_case_sensitive_id_difference(self):
        # Arrange
        hook = schema.HookDefinition(
            id="foo",
            name="Foo",
            entry="echo 'Hello, world!'",
        )
        other = schema.HookDefinition(
            id="FOO",
            name="Different",
            entry="echo 'Au revoir!'",
        )

        # Act
        result = hooks_are_equivalent(hook, other)

        # Assert
        assert result is True

    def test_no_id(self):
        # Arrange
        hook = schema.HookDefinition(
            id=None,
            name="Foo",
            entry="echo 'Hello, world!'",
            language=schema.Language("python"),
        )
        other = schema.HookDefinition(
            id="foo",
            name="Foo",
            entry="echo 'Hello, world!'",
            language=schema.Language("python"),
        )

        # Act
        result = hooks_are_equivalent(hook, other)

        # Assert
        assert result is False

    def test_aliases(self):
        # Arrange / Act / Assert
        assert hooks_are_equivalent(
            schema.HookDefinition(id="ruff"),
            schema.HookDefinition(id="ruff-check"),
        )
        assert hooks_are_equivalent(
            schema.HookDefinition(id="ruff-check"),
            schema.HookDefinition(id="ruff"),
        )


class TestAddRepoPipeweld:
    """Integration tests for pipeweld-based hook insertion."""

    def test_insert_between_nondependent_and_postrequisite(self, tmp_path: Path):
        """Insert a recognized hook between an unrecognized hook and a postrequisite."""
        with change_cwd(tmp_path), files_manager():
            # Set up: foo (unrecognized) then codespell (recognized, late in order)
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="foo",
                            name="foo",
                            entry="foo .",
                            language=schema.Language("system"),
                        )
                    ],
                ),
            )
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="codespell",
                            name="codespell",
                            entry="codespell .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            # Act: add ruff-format (comes before codespell, after foo)
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="ruff-format",
                            name="ruff-format",
                            entry="ruff format .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            # Assert: ruff-format should be between foo and codespell
            assert get_hook_ids() == ["foo", "ruff-format", "codespell"]

    def test_insert_with_prerequisite_present(self, tmp_path: Path):
        """Insert a hook after an existing prerequisite."""
        with change_cwd(tmp_path), files_manager():
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="ruff-check",
                            name="ruff-check",
                            entry="ruff check .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="ruff-format",
                            name="ruff-format",
                            entry="ruff format .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            assert get_hook_ids() == ["ruff-check", "ruff-format"]

    def test_insert_before_postrequisite_only(self, tmp_path: Path):
        """Insert a hook before an existing postrequisite when no predecessor exists."""
        with change_cwd(tmp_path), files_manager():
            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="codespell",
                            name="codespell",
                            entry="codespell .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            add_repo(
                schema.LocalRepo(
                    repo="local",
                    hooks=[
                        schema.HookDefinition(
                            id="ruff-check",
                            name="ruff-check",
                            entry="ruff check .",
                            language=schema.Language("system"),
                        )
                    ],
                )
            )

            assert get_hook_ids() == ["ruff-check", "codespell"]
