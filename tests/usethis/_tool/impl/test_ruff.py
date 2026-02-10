import os
from pathlib import Path

import pytest

from usethis._config import usethis_config
from usethis._config_file import DotRuffTOMLManager, RuffTOMLManager, files_manager
from usethis._core.tool import use_ruff
from usethis._file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._integrations.ci.github.errors import GitHubTagError
from usethis._integrations.ci.github.tags import get_github_latest_tag
from usethis._integrations.pre_commit import schema
from usethis._test import change_cwd
from usethis._tool.impl.ruff import RuffTool


class TestRuffTool:
    class TestSelectRules:
        def test_no_pyproject_toml(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Act
            with (
                change_cwd(tmp_path),
                files_manager(),
            ):
                RuffTool().select_rules(["A", "B", "C"])

                # Assert
                assert RuffTool().get_selected_rules() == ["A", "B", "C"]

            # Assert
            out, err = capfd.readouterr()
            assert not err
            assert out == ("✔ Selecting Ruff rules 'A', 'B', 'C' in 'ruff.toml'.\n")

        def test_message(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("")

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules(["A", "B", "C"])

            # Assert
            out, _ = capfd.readouterr()
            assert "✔ Selecting Ruff rules 'A', 'B', 'C' in 'pyproject.toml" in out

        def test_blank_slate(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("")

            # Act
            new_rules = ["A", "B", "C"]
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules(new_rules)

                # Assert
                rules = RuffTool().get_selected_rules()
            assert rules == new_rules

        def test_mixing(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """
    [tool.ruff.lint]
    select = ["A", "B"]
    """
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules(["C", "D"])

                # Assert
                rules = RuffTool().get_selected_rules()
            assert rules == ["A", "B", "C", "D"]

        def test_respects_order(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """
[tool.ruff.lint]
select = ["D", "B", "A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules(["E", "C", "A"])

                # Assert
                assert RuffTool().get_selected_rules() == ["D", "B", "A", "C", "E"]

        def test_ruff_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / "ruff.toml").write_text(
                """
[lint]
select = ["A", "B"]
"""
            )

            # Act
            with change_cwd(tmp_path), RuffTOMLManager():
                RuffTool().select_rules(["C", "D"])

                # Assert
                rules = RuffTool().get_selected_rules()

            assert rules == ["A", "B", "C", "D"]

        def test_no_rules(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """
[tool.ruff.lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().select_rules([])

                # Assert
                assert RuffTool().get_selected_rules() == ["A"]

    class TestDeselectRules:
        def test_no_pyproject_toml(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                RuffTool().deselect_rules(["A"])

                # Assert
                assert RuffTool().get_selected_rules() == []

        def test_blank_slate(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text("")

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().deselect_rules(["A", "B", "C"])

                # Assert
                assert RuffTool().get_selected_rules() == []

        def test_single_rule(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """
[tool.ruff.lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().deselect_rules(["A"])

                # Assert
                assert RuffTool().get_selected_rules() == []

        def test_mix(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """
[tool.ruff.lint]
select = ["A", "B", "C"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().deselect_rules(["A", "C"])

                # Assert
                assert RuffTool().get_selected_rules() == ["B"]

        def test_ruff_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".ruff.toml").write_text(
                """\
[lint]
select = ["A", "B"]
"""
            )

            # Act
            with change_cwd(tmp_path), DotRuffTOMLManager():
                RuffTool().deselect_rules(["A"])

                # Assert
                assert RuffTool().get_selected_rules() == ["B"]

    class TestIgnoreRules:
        def test_add_to_existing(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
ignore = ["A", "B"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().ignore_rules(["C", "D"])

                # Assert
                assert RuffTool().get_ignored_rules() == ["A", "B", "C", "D"]

        def test_no_rules(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
ignore = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                RuffTool().ignore_rules([])

                # Assert
                assert RuffTool().get_ignored_rules() == ["A"]

    class TestIsLinterUsed:
        def test_neither_subtool_has_config_assume_both_used(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                assert RuffTool().is_linter_used()

        def test_formatter_used(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.format]
select = ["A"]
"""
            )
            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                assert not RuffTool().is_linter_used()

        def test_pyproject_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                assert RuffTool().is_linter_used()

        def test_ruff_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".ruff.toml").write_text(
                """\
[lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), DotRuffTOMLManager():
                assert RuffTool().is_linter_used()

    class TestIsFormatterUsed:
        def test_neither_subtool_has_config_assume_both_used(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                assert RuffTool().is_formatter_used()

        def test_linter_used(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.lint]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                assert not RuffTool().is_formatter_used()

        def test_pyproject_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.ruff.format]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                assert RuffTool().is_formatter_used()

        def test_ruff_toml(self, tmp_path: Path):
            # Arrange
            (tmp_path / ".ruff.toml").write_text(
                """\
[format]
select = ["A"]
"""
            )

            # Act
            with change_cwd(tmp_path), DotRuffTOMLManager():
                assert RuffTool().is_formatter_used()

    class TestIgnoreRulesInGlob:
        def test_dont_break_config(self, tmp_path: Path):
            # https://github.com/usethis-python/usethis-python/issues/862
            # The issue is basically the same as this one though:
            # https://github.com/usethis-python/usethis-python/issues/507
            # Arrange
            (tmp_path / "pyproject.toml").write_text("""\
[tool.ruff]
lint.select = [ "INP" ]
""")

            with change_cwd(tmp_path), files_manager():
                # Act
                RuffTool().ignore_rules_in_glob(["INP"], glob="tests/**")

            # Assert
            contents = (tmp_path / "pyproject.toml").read_text()
            assert (
                contents
                == """\
[tool.ruff]
lint.select = [ "INP" ]
lint.per-file-ignores."tests/**" = ["INP"]
"""
            )

    class TestAddConfig:
        def test_empty_dir(self, tmp_path: Path):
            # Expect ruff.toml to be preferred

            # Act
            with change_cwd(tmp_path), files_manager():
                RuffTool(
                    # Needed to ensure the config is non-null (and so `ruff.toml` is
                    # written)
                    linter_detection="always",
                ).add_configs()

            # Assert
            assert not (tmp_path / ".ruff.toml").exists()
            assert not (tmp_path / "pyproject.toml").exists()
            assert (tmp_path / "ruff.toml").exists()

        def test_pyproject_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                RuffTool().add_configs()

            # Assert
            assert not (tmp_path / ".ruff.toml").exists()
            assert (tmp_path / "pyproject.toml").exists()
            assert not (tmp_path / "ruff.toml").exists()

    @pytest.mark.usefixtures("_vary_network_conn")
    def test_latest_version(self, tmp_path: Path):
        if os.getenv("CI"):
            pytest.skip("Avoid flaky pipelines by testing version bumps manually")

        with change_cwd(tmp_path), files_manager():
            # Arrange
            use_ruff(formatter=False)

            # Act
            (config,) = RuffTool().get_pre_commit_config().repo_configs
        repo = config.repo
        assert isinstance(repo, schema.UriRepo)
        try:
            assert repo.rev == get_github_latest_tag(
                owner="astral-sh", repo="ruff-pre-commit"
            )
        except GitHubTagError as err:
            if (
                usethis_config.offline
                or "rate limit exceeded for url" in str(err)
                or "Read timed out." in str(err)
            ):
                pytest.skip(
                    "Failed to fetch GitHub tags (connection issues); skipping test"
                )
            raise err

    class TestUpdateBitbucketSteps:
        def test_remove_stale_steps_when_pre_commit_used(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            """When pre-commit is enabled, stale Bitbucket steps should be removed."""
            # Arrange - first add Bitbucket steps for Ruff
            (tmp_path / "ruff.toml").touch()
            (tmp_path / "pyproject.toml").write_text(
                """\
[project]
name = "example"
version = "0.1.0"
"""
            )
            with change_cwd(tmp_path), files_manager():
                from usethis._integrations.ci.bitbucket.steps import (
                    add_placeholder_step_in_default,
                )

                add_placeholder_step_in_default(report_placeholder=False)
                RuffTool().update_bitbucket_steps()

            # Verify steps were added
            contents_before = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert "Run Ruff" in contents_before
            assert "Run Ruff Formatter" in contents_before
            capfd.readouterr()  # Clear captured output

            # Act - enable pre-commit and run update_bitbucket_steps again
            (tmp_path / ".pre-commit-config.yaml").touch()
            with change_cwd(tmp_path), files_manager():
                RuffTool().update_bitbucket_steps()

            # Assert - stale steps should be removed
            contents_after = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert "Run Ruff" not in contents_after
            assert "Run Ruff Formatter" not in contents_after
            out, err = capfd.readouterr()
            assert not err
            assert "Removing 'Run Ruff'" in out
            assert "Removing 'Run Ruff Formatter'" in out

        def test_dont_remove_steps_when_tool_not_used(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            """When pre-commit is enabled but tool isn't used, don't remove steps."""
            # Arrange - create Bitbucket steps manually (simulating legacy config)
            # but DON'T create ruff.toml (tool is not actually used)
            (tmp_path / "pyproject.toml").write_text(
                """\
[project]
name = "example"
version = "0.1.0"
"""
            )
            (tmp_path / "bitbucket-pipelines.yml").write_text(
                """\
image: atlassian/default-image:3
pipelines:
    default:
      - step:
            name: Run Ruff
            script:
              - ruff check
      - step:
            name: Some Other Step
            script:
              - echo "hello"
"""
            )

            # Act - enable pre-commit and run update_bitbucket_steps
            # (tool is NOT used, so steps should NOT be removed)
            (tmp_path / ".pre-commit-config.yaml").touch()
            with change_cwd(tmp_path), files_manager():
                RuffTool().update_bitbucket_steps()

            # Assert - steps should NOT be removed because tool is not used
            contents_after = (tmp_path / "bitbucket-pipelines.yml").read_text()
            assert "Run Ruff" in contents_after
            assert "Some Other Step" in contents_after
            out, err = capfd.readouterr()
            assert not err
            # Should not contain any removal messages
            assert "Removing" not in out
