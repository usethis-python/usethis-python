from pathlib import Path

import pytest

from usethis._config_file import files_manager
from usethis._integrations.file.pyproject_toml.io_ import PyprojectTOMLManager
from usethis._test import change_cwd
from usethis._tool.config import ConfigEntry, ConfigItem
from usethis._tool.impl.deptry import DeptryTool


class TestDeptryTool:
    """Tests for DeptryTool."""

    def test_get_pyproject_id_keys(self):
        """Test that get_pyproject_id_keys returns the correct keys."""
        # Arrange
        tool = DeptryTool()

        # Act
        result = tool.get_config_spec()

        # Assert
        config_item, *_ = result.config_items
        assert isinstance(config_item, ConfigItem)
        assert config_item.root[Path("pyproject.toml")] == ConfigEntry(
            keys=["tool", "deptry"]
        )

    def test_remove_pyproject_configs_removes_deptry_section(self, tmp_path: Path):
        """Test that remove_pyproject_configs removes the deptry section."""
        # Arrange
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""[tool.deptry]
ignore_missing = ["pytest"]
""")

        # Act
        with change_cwd(tmp_path), PyprojectTOMLManager():
            tool = DeptryTool()
            tool.remove_configs()

        # Assert
        assert "[tool.deptry]" not in pyproject.read_text()
        assert "ignore_missing" not in pyproject.read_text()

    class TestIsManagedRule:
        def test_dep001(self):
            # Arrange
            rule = "DEP001"

            # Act
            result = DeptryTool().is_managed_rule(rule)

            # Assert
            assert result is True

        def test_not_deptry_rule(self):
            # Arrange
            rule = "NOT_DEPTRY_RULE"

            # Act
            result = DeptryTool().is_managed_rule(rule)

            # Assert
            assert result is False

        def test_extra_letters(self):
            # Arrange
            rule = "DEPA001"

            # Act
            result = DeptryTool().is_managed_rule(rule)

            # Assert
            assert result is False

        def test_leading_numbers(self):
            # Arrange
            rule = "001DEP"

            # Act
            result = DeptryTool().is_managed_rule(rule)

            # Assert
            assert result is False

        def test_letters_separated_by_numbers(self):
            # Arrange
            rule = "D0E0P1"

            # Act
            result = DeptryTool().is_managed_rule(rule)

            # Assert
            assert result is False

        def test_four_numbers(self):
            # Arrange
            rule = "DEP0001"

            # Act
            result = DeptryTool().is_managed_rule(rule)

            # Assert
            assert result is True

        def test_no_numbers(self):
            # N.B. Deptry does not accept rules without number codes, unlike Ruff.

            # Arrange
            rule = "DEP"

            # Act
            result = DeptryTool().is_managed_rule(rule)

            # Assert
            assert result is False

        def test_truncated(self):
            # Arrange
            rule = "DE"

            # Act
            result = DeptryTool().is_managed_rule(rule)

            # Assert
            assert result is False

    class TestSelectRules:
        def test_always_empty(self, tmp_path: Path):
            # Arrange
            tool = DeptryTool()

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                tool.select_rules(["A", "B", "C"])

                # Assert
                assert tool.get_selected_rules() == []

    class TestGetSelectedRules:
        def test_always_empty(self, tmp_path: Path):
            # Arrange
            tool = DeptryTool()

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = tool.get_selected_rules()

                # Assert
                assert result == []

    class TestDeselectRules:
        def test_no_effect(self, tmp_path: Path):
            # Arrange
            tool = DeptryTool()

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                tool.deselect_rules(["A", "B", "C"])

                # Assert
                assert tool.get_selected_rules() == []

    class TestIgnoreRules:
        def test_ignore_dep001_no_pyproject_toml(
            self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
        ):
            # Arrange
            tool = DeptryTool()

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                tool.ignore_rules(["DEP001"])

                # Assert
                assert tool.get_ignored_rules() == ["DEP001"]

            out, err = capfd.readouterr()
            assert not err
            assert out == (
                "✔ Writing 'pyproject.toml'.\n"
                "✔ Ignoring deptry rule 'DEP001' in 'pyproject.toml'.\n"
            )

        def test_ignore_dep001(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
            # Arrange
            tool = DeptryTool()
            (tmp_path / "pyproject.toml").write_text("")

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                tool.ignore_rules(["DEP001"])

                # Assert
                assert tool.get_ignored_rules() == ["DEP001"]

            assert (
                (tmp_path / "pyproject.toml").read_text()
                == """\
[tool.deptry]
ignore = ["DEP001"]
"""
            )

            out, err = capfd.readouterr()
            assert not err
            assert out == ("✔ Ignoring deptry rule 'DEP001' in 'pyproject.toml'.\n")

    class TestGetIgnoredRules:
        def test_no_pyproject_toml(self, tmp_path: Path):
            # Arrange
            tool = DeptryTool()

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = tool.get_ignored_rules()

                # Assert
                assert result == []

        def test_empty(self, tmp_path: Path):
            # Arrange
            tool = DeptryTool()
            (tmp_path / "pyproject.toml").write_text("")

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = tool.get_ignored_rules()

                # Assert
                assert result == []

        def test_with_rule(self, tmp_path: Path):
            # Arrange
            tool = DeptryTool()
            (tmp_path / "pyproject.toml").write_text(
                """\
[tool.deptry]
ignore = ["DEP003"]
"""
            )

            # Act
            with change_cwd(tmp_path), PyprojectTOMLManager():
                result = tool.get_ignored_rules()

                # Assert
                assert result == ["DEP003"]

    class TestAddConfig:
        def test_empty_dir(self, tmp_path: Path):
            # Act
            with change_cwd(tmp_path), files_manager():
                DeptryTool().add_configs()

            # Assert
            assert (tmp_path / "pyproject.toml").exists()

        def test_pyproject_toml_exists(self, tmp_path: Path):
            # Arrange
            (tmp_path / "pyproject.toml").touch()

            # Act
            with change_cwd(tmp_path), files_manager():
                DeptryTool().add_configs()

            # Assert
            assert (tmp_path / "pyproject.toml").exists()
